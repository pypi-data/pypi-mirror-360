import json

from loguru import logger

from ...endpoint import Endpoint


class TrafficFilter(Endpoint):
    BASE_URL = "/api/v1/deployments/traffic-filter/rulesets"

    def get_all(self) -> dict:
        logger.info(f"Reading deployments")
        return self._get(TrafficFilter.BASE_URL)

    # def get(self, deployment_id: str) -> dict:
    #     logger.info(f'Reading deployment "{deployment_id}"')
    #     return self._get(
    #         f"{TrafficFilter.BASE_URL}/{deployment_id}?clear_transient=true"
    #     )
    #
    # def show(self, deployment_id: str):
    #     print(json.dumps(self.get(deployment_id), indent=2))

    def list(self):
        r = self.get_all()
        for deployment in r.get("rulesets"):
            print(f"Name: {deployment.get('name')}  ID: {deployment.get('id')}")
            # print(json.dumps(deployment, indent=2))

    # def create_by_template(self, template_name: str, template_params: dict = {}):
    #     logger.debug(
    #         f'Using template "{template_name}" and params "{template_params}" for deployment'
    #     )
    #     config = self._render_template("role", template_name, template_params)
    #     self._post(TrafficFilter.BASE_URL, config)
