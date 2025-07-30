# https://www.elastic.co/docs/api/doc/kibana/group/endpoint-roles

import json
import re

from loguru import logger

from ...exceptions import NotFoundException
from ...endpoint import Endpoint


class Role(Endpoint):
    BASE_URL = "/api/security/role"

    def get(self, name: str) -> dict:
        logger.info(f'Reading role "{name}"')
        return self._get(f"{Role.BASE_URL}/{name}")

    def show(self, name: str):
        role = self.get(name)
        print(json.dumps(role, indent=2))

    def get_all(self):
        logger.info("Reading all roles")
        return self._get(Role.BASE_URL)

    def list(self, reserved: bool = False, filter: str = None):
        pattern = re.compile(filter) if filter else None
        r = self.get_all()
        for role in r:
            if not reserved and "_reserved" in role.get("metadata").keys():
                continue
            if pattern and not pattern.search(role["name"]):
                continue
            print(f"Role: {role['name']} \tDescription: {role['description']}")

    def compare(self, name: str, config: dict):
        cur_conf = self.get(name)
        logger.info(f'Comparing role "{name}"')
        logger.debug(f'with config "{config}"')
        self._deepdiff(cur_conf, config)

    def set(self, name: str, config: dict):
        try:
            cur_conf = self.get(name)
            logger.info(f'Updating role "{name}"')
            logger.debug(f'with config "{config}"')
            self._deepdiff(cur_conf, config)
        except NotFoundException:
            logger.info(f'Creating role "{name}"')
            logger.debug(f'with config "{config}"')
        self._put(f"{Role.BASE_URL}/{name}", json=config)

    def set_with_template(
        self, name: str, template_name: str, template_params: dict = {}
    ):
        logger.debug(
            f'Using template "{template_name}" and params "{template_params}" for role'
        )
        config = self._render_template("kibana/role", template_name, template_params)
        self.set(name, config)

    def delete(self, name: str):
        logger.info(f'Deleting role "{name}"')
        self._delete(f"{Role.BASE_URL}/{name}")
