import json
import os
import sys

from deepdiff import DeepDiff
import httpx
from jinja2 import Environment, FileSystemLoader, meta, TemplateNotFound
from loguru import logger

from .exceptions import (
    CurcumaException,
    ConflictException,
    NotFoundException,
    PermissionException,
    TemplateParameterException,
)


class Endpoint:

    def __init__(self, client: httpx.Client):
        self._clt = client

    def _get(self, url: str):
        logger.trace(f"connecting to {url} via GET")
        r = self._clt.get(url)
        return self._response_handler(r)

    def _post(self, url: str, json: dict):
        logger.trace(f"connecting to {url} via POST")
        r = self._clt.post(url, json=json)
        return self._response_handler(r)

    def _put(self, url: str, json: dict):
        logger.debug(f"connecting to {url} via PUT")
        r = self._clt.put(url, json=json)
        return self._response_handler(r)

    def _delete(self, url: str):
        logger.debug(f"connecting to {url} via DELETE")
        r = self._clt.delete(url)
        return self._response_handler(r)

    @staticmethod
    def _fpretty(key: str):
        return key[5:-1].replace("][", ".").replace("'", "")

    @staticmethod
    def _deepdiff(old: dict, new: dict, show_untouched: bool = False) -> DeepDiff:
        logger.debug("determining the differences")
        diff = DeepDiff(old, new, ignore_order=True, verbose_level=2)

        added = diff.get("iterable_item_added")
        if added:
            logger.debug("new:")
            for a in added:
                logger.debug(f" - {Endpoint._fpretty(a)} => {added[a]}")

        changed = diff.get("values_changed")
        if changed:
            logger.info("changes:")
            for c in changed:
                logger.info(
                    f" - {Endpoint._fpretty(c)} changed from '{changed[c]["old_value"]}' to '{changed[c]["new_value"]}'"
                )

        if show_untouched:
            removed = diff.get("dictionary_item_removed")
            if removed:
                logger.debug("untouched:")
                for r in removed:
                    val = eval(r.replace("root", "old"))
                    if type(val) is not bool and len(val) == 0:
                        continue
                    logger.debug(f" - {Endpoint._fpretty(r)} => {removed[r]}")
        return diff

    @staticmethod
    def _render_template(path, name, params, check: bool = True):
        try:
            package_root = os.path.dirname(__file__)
            template_file = name + ".json.j2"
            env = Environment(
                loader=FileSystemLoader(f"{package_root}/templates/{path}")
            )
            if check:
                template_source = env.loader.get_source(env, template_file)[0]
                parsed_content = env.parse(template_source)
                variables = meta.find_undeclared_variables(parsed_content)
                diff = list(variables.difference(set(params)))
                if len(diff) > 0:
                    logger.error(f"Missing parameters: {diff}")
                    raise TemplateParameterException(
                        f"Missing template parameters: {diff}"
                    )

            template = env.get_template(template_file)
            config = template.render(params)
            return json.loads(config)
        except TemplateNotFound as e:
            logger.error(e.message)
            sys.exit(1)

    def _response_handler(self, r: httpx.Response):
        self._status_handler(r)
        try:
            if r.status_code == 204:
                return None
            elif r.text.startswith("{"):
                return r.json()
            else:
                return r.text
        except Exception as e:
            logger.error(e)
            logger.trace(r.text)

    def _status_handler(self, r: httpx.Response):
        logger.trace(f"status code: {r.status_code}")
        logger.trace(f"response body: {r.text}")
        if r.status_code <= 210:
            logger.success("done")
        elif r.status_code == 302:
            logger.info("relocated")
            raise NotFoundException(f"Status {r.status_code} - {r.headers['Location']}")
        elif r.status_code == 403:
            logger.error("permission denied")
            raise PermissionException(f"Status {r.status_code} - {r.text}")
        elif r.status_code == 404:
            logger.warning("not found")
            raise NotFoundException(
                f"Status {r.status_code}({r.json().get('error')}) - {r.json().get('message', r.text)}"
            )
        elif (
            r.status_code == 409
            or r.status_code == 400
            and (
                r.json().get("message", r.text).startswith("Duplicate")
                or r.json().get("message", r.text).endswith("conflict")
            )
        ):
            logger.error(
                f"Status {r.status_code}({r.json().get('error')}) - {r.json().get('message', r.text)}"
            )
            raise ConflictException(r.text)
        elif r.status_code >= 400:
            raise CurcumaException(
                f"Status {r.status_code} - {r.json().get('message', r.text)}"
            )
