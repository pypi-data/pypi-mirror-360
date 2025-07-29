from typing import List
from simple_logger.logger import get_logger
from azure.core.exceptions import HttpResponseError
from clouds.microsoft_azure.session_clients import azure_credentials, resource_client

LOGGER = get_logger(name="azure-nuke-cli")


def nuke_all_azure_resources(tenant_id: str, client_id: str, client_secret: str, subscription_id: str) -> None:
    """
    Run nuke for all Azure cloud resources associated with the given credentials.
    This action is irreversible and will permanently delete all resources.

    Args:
        tenant_id (str): The Azure managed-identity tenant ID.
        client_id (str): The Azure managed-identity client ID.
        client_secret (str): The Azure managed-identity client secret.
        subscription_id (str): The Azure subscription ID.
    """
    _resource_client = resource_client(
        credential=azure_credentials(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        ),
        subscription_id=subscription_id,
    )

    failed_delete_resource_groups: List[str] = []
    azure_post_cleanup_message: str = "Azure cleanup completed"

    LOGGER.info("Starting Azure resources cleanup")
    for resource_group_name in [resource_group.name for resource_group in _resource_client.resource_groups.list()]:
        try:
            LOGGER.info(f"Deleting resource group {resource_group_name}")
            _resource_client.resource_groups.begin_delete(resource_group_name=resource_group_name)
        except HttpResponseError as ex:
            LOGGER.error(f"Failed to delete resource group {resource_group_name}: {ex}")
            failed_delete_resource_groups.append(resource_group_name)

    if failed_delete_resource_groups:
        LOGGER.error(
            f"{azure_post_cleanup_message} except for the following resource groups: {failed_delete_resource_groups}"
        )
    else:
        LOGGER.success(azure_post_cleanup_message)
