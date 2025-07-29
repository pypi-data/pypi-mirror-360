from collections.abc import Callable
from os import getenv
from typing import Any

import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

LOCAL_STAGE: str = "local"

STAGE: str = getenv("STAGE", LOCAL_STAGE)

LOCALSTACK_ENDPOINT: str = "http://localhost:4566"


def get_client(service: str, *, config: Config | None = None) -> BaseClient:
    return boto3.client(
        service,
        endpoint_url=(
            LOCALSTACK_ENDPOINT if STAGE == LOCAL_STAGE
            else None
        ),
        config=config,
    )


def get_service_resource(service: str) -> ServiceResource:
    return boto3.resource(
        service,
        endpoint_url=(
            LOCALSTACK_ENDPOINT if STAGE == LOCAL_STAGE
            else None
        ),
    )


class ClientErrorHandler:
    """
    Based on https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
    """

    def __init__(
        self,
        error_code: str,
        exception_class: type[Exception],
    ) -> None:
        self.__error_code = error_code
        self.__exception_class = exception_class

    def __call__(self, f: Callable[..., Any]) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except ClientError as e:
                error = e.response["Error"]
                # For SQS, somehow error code is found in
                # both `Code` and `QueryErrorCode` with different values
                # (`AWS.SimpleQueueService.NonExistentQueue` vs `QueueDoesNotExist`).
                # The value in `QueryErrorCode` seems to match public API doc.
                # https://github.com/aws/aws-sdk/issues/105
                if error.get("QueryErrorCode", error["Code"]) == self.__error_code:
                    raise self.__exception_class from e

                raise

        return wrapper


def get_account_id() -> str:
    return get_client("sts").get_caller_identity()["Account"]
