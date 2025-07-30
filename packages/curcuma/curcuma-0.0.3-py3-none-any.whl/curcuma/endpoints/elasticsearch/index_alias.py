# https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-put-alias

import re

from loguru import logger

from ...endpoint import Endpoint


class IndexAlias(Endpoint):
    BASE_URL = "/_aliases/"

    def get(self):
        return self._get(IndexAlias.BASE_URL)

    def list(self, filter: str = None):
        pattern = re.compile(filter) if filter else None
        r = self.get()
        for name in sorted(r.keys()):
            try:
                if pattern and not pattern.search(name):
                    continue
                print(f"Index: {name}")
                for alias in r[name]["aliases"]:
                    print(f"  Alias: {alias}")
                    for key, value in r[name]["aliases"][alias].items():
                        print(f"    {key}: {value}")
            except KeyError:
                print(f"Index: {name}, Config: {r[name]}")

    def create(self, body: dict):
        logger.info(
            f"Creating index alias '{body.get('actions')[0].get('add').get('alias')}'"
        )
        self._post(IndexAlias.BASE_URL, json=body)

    def create_with_template(self, template_name: str, template_params: dict):
        logger.debug(
            f'Using index_alias template "{template_name}" with params "{template_params}"'
        )
        config = self._render_template(
            "elasticsearch/index_alias", template_name, template_params
        )
        self.create(config)

    def delete(self, index: str, name: str):
        self._delete(index + IndexAlias.BASE_URL + name)
