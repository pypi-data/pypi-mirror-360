import json

from loguru import logger

from ...endpoint import Endpoint


class Deployment(Endpoint):
    BASE_URL = "/api/v1/deployments"

    def get_all(self) -> dict:
        logger.info(f"Reading deployments")
        return self._get(Deployment.BASE_URL)

    def get(self, deployment_id: str) -> dict:
        logger.info(f'Reading deployment "{deployment_id}"')
        return self._get(f"{Deployment.BASE_URL}/{deployment_id}?clear_transient=true")

    def show(self, deployment_id: str):
        print(json.dumps(self.get(deployment_id), indent=2))

    def list(self):
        r = self.get_all()
        for deployment in r.get("deployments"):
            print(f"Name: {deployment.get('name')}")
            print(json.dumps(deployment, indent=2))

    # @staticmethod
    # def _quote_if_string(value: str):
    #     return value if isinstance(value, int) or value.isdigit() else f"'{value}'"

    def create_with_template(self, template_name: str, template_params: dict = {}):
        logger.debug(
            f'Using template "{template_name}" and params "{template_params}" for deployment'
        )
        config = self._render_template(
            "cloud/deployment", template_name, template_params, check=False
        )
        # template = self._get_template(template_name)
        # for key, value in template_params.items():
        #     exec(
        #         f"template[{"][".join(Deployment._quote_if_string(k) for k in key.split("."))}] = {Deployment._quote_if_string(value)}"
        #     )
        r = self._post(Deployment.BASE_URL + "?validate_only=true", config)
        print(r)

    def reset_password(self, deployment_id: str, ref_id: str):
        r = self._post(
            Deployment.BASE_URL
            + f"/{deployment_id}/elasticsearch/{ref_id}/_reset-password"
        )

    def _list_cloud_templates(self):
        r = self._get(
            Deployment.BASE_URL
            + "/templates?region=azure-westeurope&hide-deprecated=true"
        )
        for template in r:
            print(
                f"Name: {template.get('name')}  ID: {template.get('id')}  Description: {template.get('description')}"
            )

    def _get_cloud_template(self, template_name: str, region: str):
        r = self._get(
            Deployment.BASE_URL + f"/templates/{template_name}?region={region}"
        )
        print(r)
        return r.get("deployment_template")
