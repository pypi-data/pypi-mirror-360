import pytest
from typing import Dict, List

from clouds.aws.aws_utils import (
    set_and_verify_aws_credentials,
    set_and_verify_aws_config,
    delete_all_objects_from_s3_folder,
    delete_bucket,
    aws_region_names,
    get_least_crowded_aws_vpc_region,
)

OS_ENVIRON_PATCH_STR = "clouds.aws.aws_utils.os.environ"
CONFIG_PARSER_PATCH_STR = "clouds.aws.aws_utils.ConfigParser"
EC2_CLIENT_PATCH_STR = "clouds.aws.aws_utils.ec2_client"
BOTOCORE_CLIENT_PATCH_STR = "clouds.aws.aws_utils.botocore.client"

DUMMY_BUCKET_NAME = "test_bucket"
US_EAST_REGION_STR = "us-east-1"
US_WEST_REGION_STR = "us-west-1"
DEFAULT_AWS_CONFIG_SECTION = "default"


@pytest.fixture
def mock_os_environ(mocker):
    return mocker.patch(OS_ENVIRON_PATCH_STR)


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.patch(CONFIG_PARSER_PATCH_STR)


@pytest.fixture
def mock_config_parser_instance(mock_config_parser, mocker):
    _mock_config_parser_instance = mocker.MagicMock()
    mock_config_parser.return_value = _mock_config_parser_instance
    return _mock_config_parser_instance


@pytest.fixture
def mock_ec2_client(mocker):
    return mocker.patch(EC2_CLIENT_PATCH_STR)


@pytest.fixture
def mock_ec2_client_instance(mock_ec2_client, mocker):
    mock_ec2_client_instance = mocker.MagicMock()
    mock_ec2_client.return_value = mock_ec2_client_instance
    return mock_ec2_client_instance


@pytest.fixture
def mock_s3_client(mocker):
    return mocker.patch(BOTOCORE_CLIENT_PATCH_STR)


@pytest.fixture
def mock_boto_client_instance(mock_s3_client, mocker):
    mock_boto_client_instance = mocker.MagicMock()
    mock_s3_client.return_value = mock_boto_client_instance
    return mock_boto_client_instance


def test_set_and_verify_aws_credentials(
    mock_os_environ, mock_config_parser_instance, mock_ec2_client, mock_ec2_client_instance
):
    aws_access_key_id_str: str = "aws_access_key_id"
    aws_secret_access_key_str: str = "aws_secret_access_key"

    mock_os_environ.get.return_value = None
    mock_config_parser_instance.get.side_effect = ["dummy_access_key", "dummy_secret_key"]
    mock_ec2_client_instance.describe_regions.return_value = {"Regions": [{"RegionName": US_EAST_REGION_STR}]}

    set_and_verify_aws_credentials(region_name=US_EAST_REGION_STR)

    mock_ec2_client.assert_called_once_with(region_name=US_EAST_REGION_STR)
    mock_config_parser_instance.get.assert_any_call(DEFAULT_AWS_CONFIG_SECTION, aws_access_key_id_str)
    mock_config_parser_instance.get.assert_any_call(DEFAULT_AWS_CONFIG_SECTION, aws_secret_access_key_str)

    mock_os_environ.get.assert_any_call(aws_access_key_id_str.upper(), None)
    mock_os_environ.get.assert_any_call(aws_secret_access_key_str.upper(), None)


def test_set_and_verify_aws_config(mock_os_environ, mock_config_parser_instance):
    mock_os_environ.get.return_value = None
    mock_config_parser_instance.get.return_value = US_EAST_REGION_STR

    set_and_verify_aws_config()

    mock_config_parser_instance.get.assert_called_once_with(DEFAULT_AWS_CONFIG_SECTION, "region")
    mock_os_environ.__setitem__.assert_any_call("AWS_REGION", US_EAST_REGION_STR)


def test_delete_all_objects_from_s3_folder(mock_boto_client_instance):
    s3_folder_objects_list: List[Dict[str, str]] = [{"Key": "file1"}, {"Key": "file2"}]

    mock_boto_client_instance.list_objects_v2.return_value = {"Contents": s3_folder_objects_list}
    mock_boto_client_instance.delete_objects.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    delete_all_objects_from_s3_folder(bucket_name=DUMMY_BUCKET_NAME, boto_client=mock_boto_client_instance)

    mock_boto_client_instance.list_objects_v2.assert_called_once_with(Bucket=DUMMY_BUCKET_NAME)
    mock_boto_client_instance.delete_objects.assert_called_once_with(
        Bucket=DUMMY_BUCKET_NAME,
        Delete={"Objects": s3_folder_objects_list, "Quiet": True},
    )


def test_delete_bucket(mock_boto_client_instance):
    mock_boto_client_instance.delete_bucket.return_value = {"ResponseMetadata": {"HTTPStatusCode": 204}}

    delete_bucket(bucket_name=DUMMY_BUCKET_NAME, boto_client=mock_boto_client_instance)

    mock_boto_client_instance.delete_bucket.assert_called_once_with(Bucket=DUMMY_BUCKET_NAME)


def test_aws_region_names(mock_ec2_client_instance):
    mock_ec2_client_instance.describe_regions.return_value = {"Regions": [{"RegionName": US_EAST_REGION_STR}]}

    regions = aws_region_names()

    assert regions == [US_EAST_REGION_STR]
    mock_ec2_client_instance.describe_regions.assert_called_once()


def test_get_least_crowded_aws_vpc_region(mock_ec2_client, mocker):
    mock_ec2_client_instance_east = mocker.MagicMock()
    mock_ec2_client_instance_west = mocker.MagicMock()

    def mock_ec2_client_side_effect(region_name=None):
        if region_name == US_EAST_REGION_STR:
            return mock_ec2_client_instance_east
        elif region_name == US_WEST_REGION_STR:
            return mock_ec2_client_instance_west
        return None

    mock_ec2_client.side_effect = mock_ec2_client_side_effect

    mock_ec2_client_instance_east.describe_vpcs.return_value = {"Vpcs": ["vpc-1"]}
    mock_ec2_client_instance_west.describe_vpcs.return_value = {"Vpcs": ["vpc-2", "vpc-3"]}

    least_crowded_region = get_least_crowded_aws_vpc_region(region_list=[US_EAST_REGION_STR, US_WEST_REGION_STR])

    assert least_crowded_region == US_EAST_REGION_STR
    mock_ec2_client_instance_east.describe_vpcs.assert_any_call()
    mock_ec2_client_instance_west.describe_vpcs.assert_any_call()
