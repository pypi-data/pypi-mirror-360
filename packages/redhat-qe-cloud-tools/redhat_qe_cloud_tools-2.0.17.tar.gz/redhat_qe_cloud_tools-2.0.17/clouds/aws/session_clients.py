from __future__ import annotations

from typing import Any

import boto3
import botocore


def aws_session(**kwargs: Any) -> boto3.session.Session:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html#boto3.session.Session.client
    return boto3.session.Session(**kwargs)


def iam_client(**kwargs: Any) -> "botocore.client.IAM":
    return aws_session(**kwargs).client(service_name="iam")


def ec2_client(**kwargs: Any) -> "botocore.client.EC2":
    return aws_session(**kwargs).client(service_name="ec2")


def s3_client(**kwargs: Any) -> "botocore.client.S3":
    return aws_session(**kwargs).client(service_name="s3")


def rds_client(**kwargs: Any) -> "botocore.client.RDS":
    return aws_session(**kwargs).client(service_name="rds")
