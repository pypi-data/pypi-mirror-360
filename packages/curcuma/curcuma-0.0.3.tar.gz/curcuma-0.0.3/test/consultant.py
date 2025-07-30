# import os
import sys
from loguru import logger

# Packages providing functionality to get secrets from azure keyvault
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from src import curcuma


KEYVAULT_NAME = "sce-prod-kv-74c9ac7819c7"
CLUSTER_NAME = "ruv-sce-prod-customer-obs-9995"

logger.remove()
logger.add(sys.stdout, format="[{level:<7}] {message}", level="DEBUG")


def get_secret_from_keyvault(keyvault_name, secret_name):
    # The following environment variables are required by the azure.identity library
    # - AZURE_TENANT_ID
    # - AZURE_CLIENT_ID
    # - AZURE_CLIENT_SECRET
    # as alternative you can use 'az login' on the cli
    logger.info("initializing the azure secret client")
    client = SecretClient(
        vault_url=f"https://{keyvault_name}.vault.azure.net/",
        credential=DefaultAzureCredential(),
    )
    logger.info("reading the secret from azure keyvault")
    secret = client.get_secret(secret_name)
    print(secret.value)
    return secret.value


def get_client(cluster_name):
    # Initialize the curcuma client
    client = curcuma.AzureClient(
        cluster_name=cluster_name,
        location="westeurope",
        private_link=True,
        username="elastic",
        password=get_secret_from_keyvault(KEYVAULT_NAME, f"{cluster_name}-password"),
    )
    return client


clt = get_client(CLUSTER_NAME)

clt.kb.role.set(
    "ruv_consultant",
    {
        "elasticsearch": {
            "cluster": ["manage_own_api_key"],
            "indices": [{"names": [".*"], "privileges": ["read"]}],
            "run_as": [],
        }
    },
)


clt.es.role_mapping.set_with_template(
    "ruv_consultant",
    "oidc",
    {
        "roles": ["viewer", "ruv_consultant"],
        "group_ids": [
            "9fa76865-095f-4432-a036-d8ebd952df43"  # AZ_GITLAB_P_G_003137_DEVELOPER
        ],
    },
)
