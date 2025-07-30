from src import curcuma
from loguru import logger
import sys

# from old.read import azure_obs

curcuma.configure_logger()
# logger.remove()
# logger.add(sys.stdout, level="TRACE")

azure_obs_cluster_name = "ruv-sce-prod-azure-obs-01"
subscription_ids = [
    "aa5eade2-c1db-4dee-ad59-f8a49d585f9c",  # ruv-alz-sub-elastic-p01-private-prod
    "29ad8317-301c-4efd-a335-511bc7f07e17",  # ruv-alz-sub-elastic-p02-private-int
    "eae6710e-e802-4fb6-8b48-9b526059a136",  # ruv-alz-sub-monitoring
]
group_ids = [
    "4814d7aa-39f2-4a6e-9c24-39dc9cb4a263",  # AZ_GITLAB_P_G_000465_MAINTAINER
]
# art_short = "CCC"
# app_short = "EOA"
ciid = "9995"
app_long = "Elastic On Azure"
app_id = "COM-1754"
stage = "prod"
team = "Walley"

# from src.exceptions import ConflictException

obs = curcuma.AzureClient(
    cluster_name="ruv-sce-prod-customer-obs-9995",
    location="westeurope",
    private_link=True,
    api_key="ZHdqZmpKY0I1T2lwTld6OVNycWU6SHpYTHhaSkRHXzVSMXNVYlFwZXJaZw==",
)

PREFIX = "ruv"
IDENTIFIER = f"obs_{ciid}_{stage.lower()}"
SPACE_ID = f"{PREFIX}_{IDENTIFIER}"
SPACE_NAME = f"OBS - {ciid}" + f" [{stage.upper()}]" if stage != "all" else ""
SPACE_DESC = f"{app_long} ({app_id}) [{stage.upper()}] betreut durch Team '{team}'"

BANNER_TEXT = "Elastic On Azure - Customer Search - 0007 (Test)"
BANNER_TEXT = "Elastic On Azure - Shared Observability - Hub 01"
BANNER_TEXT = "Elastic On Azure - Customer Observability - 9995 (Production)"

BANNER_LINKS = (
    " - Confluence: &#128214; [Tipps & Tricks](https://confluence.ruv.de/x/0GeCKw)"
    " - Jira: &#128587; [Support](https://jira.ruv.de/secure/CreateIssueDetails!init.jspa?pid=23625&issuetype=3&priority=3&labels=Kundenanfrage&description=*Was%3A*+%20x+%0A%0A*Warum%3A*+%20x+%0A%0A)"
    " | &#128658; [Fehler](https://jira.ruv.de/secure/CreateIssueDetails!init.jspa?pid=23625&issuetype=1&priority=3&labels=Kundenanfrage&summary=[Customer-Obs-9995]%20Fehler%20bei%20|%20in%20%3Cbitte%20anpassen%3E)"
    " - Teams: &#128172; [Forum](https://teams.microsoft.com/l/channel/19%3AFdA38zuGK8xoVYRh0-rPxN-u562IxQMD2q3rI7vH8bU1%40thread.tacv2/Forum?groupId=b0a875cb-df38-4c84-b012-53b4b4714269&tenantId=d151fc68-72bf-474f-8a3c-a3c097baf010&ngc=true&allowXTenantAccess=true)"
    " | &#128227; [Ankündigungen](https://teams.microsoft.com/l/channel/19%3A1VXCK9_2ukrWloD6TJ30MS8RrSP15pqFWNQDHH6YzBU1%40thread.tacv2/Ank%C3%BCndigungen?groupId=b0a875cb-df38-4c84-b012-53b4b4714269&tenantId=d151fc68-72bf-474f-8a3c-a3c097baf010)"
)

# curcuma.generics.prefix = PREFIX
# curcuma.generics.identifier = IDENTIFIER

try:
    # obs.space.list()
    # obs.space.set(SPACE_ID, SPACE_NAME, SPACE_DESC)
    # SPACE_ID = "default"
    # obs.kibana_settings.get(SPACE_ID)
    # obs.kibana_settings.set(SPACE_ID, "banners:textContent", BANNER_TEXT + BANNER_LINKS)
    # obs.kibana_settings.set(SPACE_ID, "banners:backgroundColor", "#25282f")
    # obs.kibana_settings.set(SPACE_ID, "banners:textColor", "#ffffff")
    # obs.kibana_settings.set(SPACE_ID, "banners:linkColor", "#4dd2ca")
    # obs.kibana_settings.set(SPACE_ID, "defaultRoute", "/app/discover#/")

    # obs.kibana_settings.set(
    #     SPACE_ID,
    #     {
    #         "banners:textContent": BANNER_TEXT + BANNER_LINKS,
    #         "banners:backgroundColor": "#25282f",
    #         "banners:textColor": "#ffffff",
    #         "banners:linkColor": "#4dd2ca",
    #         "defaultRoute": "/app/discover#/",
    #     },
    # )
    # obs.kibana_settings.set(SPACE_ID, {
    # "notifications:banner": None,
    # "notifications:lifetime:banner":30000
    # })

    obs.kb.kibana_settings.set(
        SPACE_ID,
        {
            "dateFormat:dow": "Monday",
            "format:number:defaultLocale": "de",
            "theme:darkMode": "system",
            "defaultIndex": "azure_log",
            "timepicker:quickRanges": '[\n  {\n    "from": "now/d",\n    "to": "now/d",\n    "display": "Today"\n  },\n  {\n    "from": "now/w",\n    "to": "now/w",\n    "display": "This week"\n  },\n  {\n    "from": "now-1m",\n    "to": "now",\n    "display": "Last 1 minute"\n  },\n  {\n    "from": "now-15m",\n    "to": "now",\n    "display": "Last 15 minutes"\n  },\n  {\n    "from": "now-1h",\n    "to": "now",\n    "display": "Last 1 hour"\n  },\n  {\n    "from": "now-24h/h",\n    "to": "now",\n    "display": "Last 24 hours"\n  },\n  {\n    "from": "now-7d/d",\n    "to": "now",\n    "display": "Last 7 days"\n  },\n  {\n    "from": "now-30d/d",\n    "to": "now",\n    "display": "Last 30 days"\n  }\n]',
        },
    )

    obs.es.index_alias.create_with_template(
        "subscription_filter",
        {
            "index": "logs-*",
            "alias": f"logs-azure-{SPACE_ID}",
            "subscription_ids": subscription_ids,
        },
    )
    obs.es.index_alias.list("^logs-")
    # "notifications:banner": "this is a notification",
    ######
    ## Roles
    # obs.role.set_with_template(
    #     name=f"{SPACE_ID}_kibana_designer",
    #     template_name="kibana_designer",
    #     template_params={"space_id": SPACE_ID},
    # )
    # obs.role.set_with_template(
    #     name=f"{SPACE_ID}_hub2azure",
    #     template_name="remote",
    # )
    # obs.role.set_with_template(
    #     name=f"{SPACE_ID}_hub2azure",
    #     template_name="hub2azure",
    #     template_params={
    #         "identifier": SPACE_ID,
    #         "subscription_ids": subscription_ids,
    #     },
    # )
    # # # obs.role.list()
    # # obs.role.delete(name=f"{SPACE_ID}_hub2azure")
    # # obs.role_mapping.list()
    # obs.role_mapping.set_with_template(
    #     name=f"{SPACE_ID}_kibana_designer",
    #     template_name="oidc",
    #     template_params={
    #         "roles": [
    #             f"{SPACE_ID}_kibana_designer",
    #             f"{SPACE_ID}_hub2azure",
    #             "monitoring_user" if False else None,  # for monitoring
    #         ],
    #         "group_ids": group_ids,
    #     },
    # )

    # obs.data_view.set_with_template(
    #     SPACE_ID,
    #     "base",
    #     {
    #         "name": "Azure Logs",
    #         "id": f"{SPACE_ID}_logs_azure",
    #         "index": f"{azure_obs_cluster_name}:logs-azure-{SPACE_ID}",
    #     },
    # )
    # obs.role_mapping.delete(name=f"{SPACE_ID}_kibana_designer")
    # # cleanup
    # obs.space.delete(SPACE_ID)

except curcuma.CurcumaException as e:
    print(f"Error: {e}")
# except Exception as e:
#     print(f"{e}")
