# https://www.elastic.co/guide/en/kibana/8.12/data-views-api.html

import json
import sys

from loguru import logger

from ...endpoint import Endpoint


class DataView(Endpoint):
    BASE_URL = "/s/{space_id}/api/data_views"

    def default(self, space_id, id):
        logger.info(f"Setting data view '{id}' in space '{space_id}' as default")
        self._post(f"{DataView.BASE_URL}/default", data={"data_view_id": id})

    def get(self, space_id, id):
        logger.info(f"Reading data view '{id}' ... ")
        return self._get(
            f"{DataView.BASE_URL}/data_view/{id}".format(space_id=space_id)
        )

    def show(self, space_id, id):
        role = self.get(space_id, id)
        print(json.dumps(role, indent=2))

    def get_all(self, space_id):
        logger.info("Reading data views ... ")
        return self._get(f"{DataView.BASE_URL}".format(space_id=space_id))

    def get_id(self, space_id, name):
        for dataview in self.get_all(space_id):
            if dataview.get("name") == name:
                return dataview.get("id")

    def exits(self, space_id, name=None, id=None):
        if name is not None and id is not None:
            raise AttributeError(
                f"{self.__class__}.{sys._getframe().f_code.co_name}() supports name or id, not both"
            )
        if id is not None:
            print(f"id = {id}")
            r = self.get(space_id, id)
            return r.status_code < 300
        else:
            for dv in self.get_all(space_id):
                if dv.get("name") == name:
                    return True
            return False

    def list(self, space_id):
        for data_view in self.get_all(space_id):
            print(f"DataView: {data_view}")

    def create(self, space_id, config):
        data_view = config.get("data_view")
        logger.info(f"Creating data view '{data_view.get('id')}' ... ")
        self._post(
            f"{DataView.BASE_URL}/data_view".format(space_id=space_id), json=config
        )

    def update(self, space_id, config):
        id = config["data_view"]["id"]
        logger.info(f"Updating data view '{id}' ... ")
        del config["data_view"]["id"]
        self._post(
            f"{DataView.BASE_URL}/data_view/{id}".format(space_id=space_id), json=config
        )

    def create_with_template(self, space_id, template_name, params):
        config = self._render_template("kibana/data_view", template_name, params)
        self.create(space_id, config)

    def update_with_template(self, space_id, template_name, params):
        config = self._render_template("kibana/data_view", template_name, params)
        self.update(space_id, config)

    def set_with_template(self, space_id, template_name, params):
        if not self.exits(space_id, name=params.get("name")):
            self.create_with_template(space_id, template_name, params)
        else:
            self.update_with_template(space_id, template_name, params)

    def delete(self, space_id, id):
        logger.info(f"Deleting data view '{id}'")
        self._delete(f"{DataView.BASE_URL}/data_view/{id}".format(space_id=space_id))

    def delete_by_name(self, space_id, name):
        self.delete(space_id, self.get_id(space_id, name))
