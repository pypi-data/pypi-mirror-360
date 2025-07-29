from typing import Any, Dict, List

import boto3
import botocore
from simple_logger.logger import get_logger

LOGGER = get_logger(name=__name__)
DEFAULT_AWS_REGION: str = "us-east-1"


def iam_client(region: str = DEFAULT_AWS_REGION) -> "botocore.client.IAM":
    """Creates an IAM client.

    Args:
        region (str, default: "us-east-1"): Region to use for session, a client is associated with a single region.

    Returns:
        botocore.client.IAM: Service client instance.

    """
    LOGGER.info(f"Creating IAM client using region {region}.")
    return boto3.client(service_name="iam", region_name=region)


def get_roles(client: "botocore.client.IAM" = None) -> List[Dict[str, Any]]:
    """
    Get all IAM roles.

    Args:
        client (botocore.client.IAM, optional): A boto3 client for IAM. Defaults to None.

    Returns:
        List[Dict[str, Any]]: A list of IAM roles
    """
    LOGGER.info("Retrieving all roles from IAM.")

    iam_max_items = 1000
    client = client or iam_client()
    response = client.list_roles(MaxItems=iam_max_items)
    roles = response["Roles"]

    while response["IsTruncated"]:
        marker = response["Marker"]
        response = client.list_roles(Marker=marker, MaxItems=iam_max_items)
        roles.extend(response["Roles"])

    return roles


def create_or_update_role_policy(
    role_name: str,
    policy_name: str,
    policy_document: str,
    region: str = DEFAULT_AWS_REGION,
) -> None:
    """
    Create a new policy role or update an existing one.

    Args:
        role_name (str): role policy name
        policy_name (str): policy name
        policy_document (str): policy documents as Json file content
        region (str): aws region
    """
    client = iam_client(region=region)
    LOGGER.info(f"Create/Update role {role_name} for policy {policy_name} by documented policy.")
    client.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=policy_document,
    )
