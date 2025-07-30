import base64
import httpx

from .endpoints.cloud.deployment import Deployment
from .endpoints.cloud.traffic_filter import TrafficFilter

from .endpoints.elasticsearch.ilm import IndexLifecycleManagement
from .endpoints.elasticsearch.index_alias import IndexAlias
from .endpoints.elasticsearch.role_mapping import RoleMapping
from .endpoints.elasticsearch.snapshot import Snapshot

from .endpoints.kibana.data_view import DataView
from .endpoints.kibana.role import Role
from .endpoints.kibana.space import Space
from .endpoints.kibana.settings import AdvancedSettings


class Client:

    def __init__(
        self,
        elasticsearch_host: str = None,
        kibana_host: str = None,
        port: int = 443,
        username: str = None,
        password: str = None,
        api_key: str = None,
    ):
        authorization = (
            f"ApiKey {api_key}"
            if api_key is not None
            else f"Basic {base64.b64encode(bytes(username + ":" + password, 'utf-8')).decode('utf-8')}"
        )

        self.es = Client.ElasticSearch(elasticsearch_host, port, authorization)
        self.kb = Client.Kibana(kibana_host, port, authorization)

    class ElasticSearch:
        def __init__(self, host, port, authorization):
            self._es = httpx.Client(
                base_url=f"https://{host}:{port}",
                headers=httpx.Headers(
                    {
                        "Content-Type": "application/json",
                        "Authorization": authorization,
                    }
                ),
            )

        @property
        def role_mapping(self):
            return RoleMapping(self._es)

        @property
        def index_alias(self):
            return IndexAlias(self._es)

        @property
        def ilm(self):
            return IndexLifecycleManagement(self._es)

        @property
        def snapshot(self):
            return Snapshot(self._es)

    class Kibana:
        def __init__(self, host, port, authorization):
            self._kb = httpx.Client(
                base_url=f"https://{host}:{port}",
                headers=httpx.Headers(
                    {
                        "Content-Type": "application/json",
                        "Authorization": authorization,
                        "kbn-xsrf": "true",
                    }
                ),
            )

        @property
        def space(self):
            return Space(self._kb)

        @property
        def role(self):
            return Role(self._kb)

        @property
        def data_view(self):
            return DataView(self._kb)

        @property
        def kibana_settings(self):
            return KibanaSettings(self._kb)


class AzureClient(Client):
    def __init__(
        self,
        cluster_name: str,
        location: str,
        private_link: bool = False,
        api_key: str = None,
        username: str = None,
        password: str = None,
    ):
        super().__init__(
            elasticsearch_host=f"{cluster_name}.es{".privatelink" if private_link else ""}.{location}.azure.elastic-cloud.com",
            kibana_host=f"{cluster_name}.kb{".privatelink" if private_link else ""}.{location}.azure.elastic-cloud.com",
            api_key=api_key,
            username=username,
            password=password,
        )


class CloudClient:
    def __init__(self, api_key):
        _api_key = api_key

        self._cld = httpx.Client(
            base_url=f"https://api.elastic-cloud.com",
            headers=httpx.Headers(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"ApiKey {api_key}",
                }
            ),
        )

    @property
    def deployment(self):
        return Deployment(self._cld)

    @property
    def traffic_filter(self):
        return TrafficFilter(self._cld)
