# https://www.elastic.co/docs/api/doc/kibana/group/endpoint-spaces

from loguru import logger

from ...exceptions import NotFoundException
from ...endpoint import Endpoint


class Space(Endpoint):

    BASE_URL = "/api/spaces/space"

    def get(self, space_id):
        logger.info(f"reading space '{space_id}'")
        return self._get(f"{Space.BASE_URL}/{space_id}")

    def get_all(self):
        logger.info("reading all spaces")
        return self._get(Space.BASE_URL)

    def list(self):
        r = self.get_all()
        for space in r:
            print(
                f"{space['name']} ({space['id']}): {space['description'] if 'description' in space else 'null'}"
            )

    def create_json(self, body):
        logger.info(f"Creating space '{body.get("name")}' ... ")
        self._post(Space.BASE_URL, json=body)

    def create(self, space_id, name, description="", color=None, icon=None):
        body = {"id": space_id, "name": name}
        body["initials"] = "".join([x[0] for x in space_id.split("_")[:1]])
        if description:
            body["description"] = description
        if color:
            body["color"] = color
        if icon:
            body["icon"] = icon
        self.create_json(body)

    def update_json(self, body):
        logger.info(f"Updating space '{body.get("name")}' ... ")
        self._put(f"{Space.BASE_URL}/{body.get('id')}", json=body)

    def update(self, space_id, name, description="", color=None, icon=None):
        body = {"id": space_id, "name": name}
        body["initials"] = "".join([x[0] for x in space_id.split("_")[1:3]]).upper()
        if description:
            body["description"] = description
        if color:
            body["color"] = color
        if icon:
            body["icon"] = icon
        self.update_json(body)

    def set(self, space_id, name, description="", color=None, icon=None):
        try:
            self.get(space_id)
            self.update(space_id, name, description, color, icon)
        except NotFoundException:
            self.create(space_id, name, description, color, icon)

    def delete(self, space_id):
        logger.info(f"Deleting space: {space_id}")
        self._delete(f"{Space.BASE_URL}/{space_id}")
