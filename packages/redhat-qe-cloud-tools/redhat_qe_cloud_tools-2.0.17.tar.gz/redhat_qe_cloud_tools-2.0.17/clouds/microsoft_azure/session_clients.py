from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.redhatopenshift import AzureRedHatOpenShiftClient


def azure_credentials(tenant_id: str, client_id: str, client_secret: str) -> ClientSecretCredential:
    return ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )


def aro_client(credential: ClientSecretCredential, subscription_id: str) -> AzureRedHatOpenShiftClient:
    return AzureRedHatOpenShiftClient(credential=credential, subscription_id=subscription_id)


def network_client(credential: ClientSecretCredential, subscription_id: str) -> NetworkManagementClient:
    return NetworkManagementClient(credential=credential, subscription_id=subscription_id)


def resource_client(credential: ClientSecretCredential, subscription_id: str) -> ResourceManagementClient:
    return ResourceManagementClient(credential=credential, subscription_id=subscription_id)


def subscription_client(credential: ClientSecretCredential) -> SubscriptionClient:
    return SubscriptionClient(credential=credential)
