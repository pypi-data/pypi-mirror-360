import os
import click
import shutil
from simple_logger.logger import get_logger
from clouds.cli.aws.aws_cli import clean_aws_resources
from pyhelper_utils.runners import function_runner_with_pdb
from clouds.cli.microsoft_azure.microsoft_azure_cli import nuke_all_azure_resources
from clouds.aws.aws_utils import set_and_verify_aws_credentials, aws_region_names

LOGGER = get_logger(name="cloud-cli")


class CloudCLIError(Exception):
    pass


@click.group()
@click.option(
    "--pdb",
    help="Drop to `ipdb` shell on exception",
    is_flag=True,
    show_default=True,
)
def cloud_cli(pdb: bool) -> None:
    # This command is only to group aws and azure sub commands
    pass


@cloud_cli.command()
@click.option(
    "--aws-regions",
    help="""
        \b
        Comma-separated string of AWS regions to delete resources from.
        """,
)
@click.option(
    "--all-aws-regions",
    help="""
        \b
        Run on all AWS regions.
        """,
    is_flag=True,
)
def aws_nuke(aws_regions: str, all_aws_regions: bool) -> None:
    """
    Nuke all AWS cloud resources in given/all regions
    """

    if not shutil.which("cloud-nuke"):
        raise CloudCLIError("cloud-nuke is not installed; install from: https://github.com/gruntwork-io/cloud-nuke")

    if all_aws_regions and aws_regions or not (all_aws_regions or aws_regions):
        raise CloudCLIError("Either pass --all-aws-regions or --aws-regions to run cleanup")

    _aws_regions = aws_region_names() if all_aws_regions else aws_regions.split(",")

    set_and_verify_aws_credentials(region_name=_aws_regions[0])

    clean_aws_resources(aws_regions=_aws_regions)


@cloud_cli.command()
@click.option(
    "--azure-tenant-id",
    help="Azure's managed identity tenant ID, needed for Azure API clients.",
    type=str,
    default=os.environ.get("AZURE_TENANT_ID"),
)
@click.option(
    "--azure-client-id",
    help="Azure's managed identity client ID, needed for Azure API clients.",
    type=str,
    default=os.environ.get("AZURE_CLIENT_ID"),
)
@click.option(
    "--azure-client-secret",
    help="Azure's managed identity client secret, needed for Azure API clients.",
    type=str,
    default=os.environ.get("AZURE_CLIENT_SECRET"),
)
@click.option(
    "--azure-subscription-id",
    help="Azure subscription ID, needed for Azure API clients.",
    type=str,
    default=os.environ.get("AZURE_SUBSCRIPTION_ID"),
)
def azure_nuke(
    azure_tenant_id: str, azure_client_id: str, azure_client_secret: str, azure_subscription_id: str
) -> None:
    """
    Nuke all Microsoft Azure cloud resources.
    """
    nuke_all_azure_resources(
        tenant_id=azure_tenant_id,
        client_id=azure_client_id,
        client_secret=azure_client_secret,
        subscription_id=azure_subscription_id,
    )


if __name__ == "__main__":
    function_runner_with_pdb(func=cloud_cli)
