import json
from xml.etree.ElementTree import indent

from src import curcuma
from loguru import logger
import sys

# from old.read import azure_obs

curcuma.configure_logger()
# logger.remove()
# logger.add(sys.stdout, level="TRACE")

azure_obs_cluster_name = "ruv-sce-prod-azure-obs-01"

# from src.exceptions import ConflictException

cld = curcuma.CloudClient(
    api_key="essu_VDA1NU9IazFZMEpDTTNOVFlURm5jV1JIV1RjNk1qUmxlRVl4YW5wVE1rTm9RVUkzWVU5RmIxaHlkdz09AAAAANYE0DE=",
)

# curcuma.generics.prefix = PREFIX
# curcuma.generics.identifier = IDENTIFIER

try:
    # r = cld.deployment.get_all()
    # print(r)
    # cld.traffic_filter.list()
    params = {"elasticsearch.0.plan.cluster_technology.id#hot_content"}
    params = {"cluster_name": "rvt-test-1"}
    cld.deployment.create_with_template("azure-general-purpose", params)
    # print(
    #     json.dumps(
    #         cld.deployment._get_cloud_template("azure-general-purpose"), indent=2
    #     )
    # )

    # cld.deployment.show("85f2e0c6856a8db13fabb2ab6c9a46ec")
except curcuma.CurcumaException as e:
    print(f"Error: {e}")
# except Exception as e:
#     print(f"{e}")
