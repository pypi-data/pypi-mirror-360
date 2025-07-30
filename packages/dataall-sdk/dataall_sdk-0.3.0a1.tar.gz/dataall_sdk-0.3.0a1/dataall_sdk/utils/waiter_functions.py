"""data.all sdk waiter helper function.

Source repository: TODO
Documentation: TODO

"""

import json
import logging
import re
import time
from functools import wraps
from typing import Any, Callable, List

import boto3
from dataall_core.base_client import BaseClient

logger: logging.Logger = logging.getLogger(__name__)

DA_OBJ_GET_FUNCTIONS = {
    "environment": ("get_environment", "environmentUri"),
    "dataset": ("get_dataset", "datasetUri"),
    "notebook": ("get_sagemaker_notebook", "notebookUri"),
    "mlstudio_user": ("get_sagemaker_studio_user", "sagemakerStudioUserUri"),
    "share_object": ("get_share_object", "shareUri"),
}


def poller(
    check_success: Callable[..., bool],
    timeout: float = float("inf"),
    sleep_time: float = 1.0,
) -> Callable[..., Callable[..., bool]]:
    """Poll until a condition is met.

    Args:
        check_success (Callable): Function that takes the output of a function and returns a boolean.
        timeout (float, optional): Timeout in seconds. Defaults to float("inf").
        sleep_time (float, optional): Sleep time in seconds. Defaults to 1.0.

    Returns
    -------
        Callable: Decorated function.
    """

    def decorator(function: Callable[..., bool]) -> Callable[..., bool]:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> bool:
            current_timeout = timeout
            while not check_success(retval := function(*args, **kwargs)):
                logger.info(f"polling {current_timeout} {retval}")
                time.sleep(sleep_time)
                current_timeout -= sleep_time
                if current_timeout <= 0:
                    raise TimeoutError(
                        "Timeout waiting for items to reach target status"
                    )
            return retval

        return wrapper

    return decorator


def _stack_status_in_progress_checker(stack_status: List[str]) -> bool:
    """Check if all stacks are in progress.

    Returns True if all stacks are in progress, False otherwise.
    """
    return all(
        re.match(r".*(IN_PROGRESS|PENDING|FAILED)", status, re.IGNORECASE)
        for status in stack_status
    )


def wait_stacks_are_in_progress(
    clients: List[BaseClient],
    targetUris: List[str],
    dataall_objects: List[str],
    timeout: float = 600.0,
    sleep_time: float = 10.0,
) -> bool:
    """Wait until stacks in progress."""

    @poller(
        check_success=_stack_status_in_progress_checker,
        timeout=timeout,
        sleep_time=sleep_time,
    )
    def _wait_stacks_are_in_progress() -> List[str]:
        stack_status = []
        for index, (uri, dataall_object) in enumerate(zip(targetUris, dataall_objects)):
            inputs = {DA_OBJ_GET_FUNCTIONS[dataall_object][1]: uri}
            current_stack = getattr(
                clients[index], DA_OBJ_GET_FUNCTIONS[dataall_object][0]
            )(**inputs)
            stack_status.append(current_stack.get("stack", {}).get("status", ""))
        return stack_status

    return _wait_stacks_are_in_progress()


def _stack_status_complete_checker(stack_status: List[str]) -> bool:
    """Check if all stacks are in progress.

    Returns True if all stacks are complete, False otherwise.
    """
    return all(
        re.match(r".*(COMPLETE$|FAILED)", status, re.IGNORECASE)
        for status in stack_status
    )


def wait_stacks_are_completed(
    clients: List[BaseClient],
    targetUris: List[str],
    dataall_objects: List[str],
    timeout: float = 600.0,
    sleep_time: float = 10.0,
) -> bool:
    """Wait until stacks completed."""

    @poller(
        check_success=_stack_status_complete_checker,
        timeout=timeout,
        sleep_time=sleep_time,
    )
    def _wait_stacks_are_completed() -> List[str]:
        stack_status = []
        for index, (uri, dataall_object) in enumerate(zip(targetUris, dataall_objects)):
            inputs = {DA_OBJ_GET_FUNCTIONS[dataall_object][1]: uri}
            current_stack = getattr(
                clients[index], DA_OBJ_GET_FUNCTIONS[dataall_object][0]
            )(**inputs)
            stack_status.append(current_stack.get("stack", {}).get("status", ""))
        return stack_status

    return _wait_stacks_are_completed()


def _share_status_processed_checker(share_status: List[str]) -> bool:
    """Check if all share requests are processed.

    Returns True if all share requests are processed, False otherwise.
    """
    return all(status == "Processed" for status in share_status)


def wait_share_requests_are_processed(
    clients: List[BaseClient],
    shareUris: List[str],
    timeout: float = 600.0,
    sleep_time: float = 20.0,
) -> bool:
    """Wait until share requests are in progress."""

    @poller(
        check_success=_share_status_processed_checker,
        timeout=timeout,
        sleep_time=sleep_time,
    )
    def _wait_share_requests_are_processed() -> List[str]:
        dataall_object = "share_object"
        share_status = []
        for index, uri in enumerate(shareUris):
            current_share = getattr(
                clients[index], DA_OBJ_GET_FUNCTIONS[dataall_object][0]
            )(shareUri=uri)
            share_status.append(current_share.get("status", ""))
        return share_status

    return _wait_share_requests_are_processed()


def _crawler_status_processed_checker(crawler_status: List[str]) -> bool:
    """Check if all crawlers are processed.

    Returns True if all crawlers are processed, False otherwise.
    """
    return all(
        re.match(r"(READY|STOPPING)", status, re.IGNORECASE)
        for status in crawler_status
    )


def wait_glue_crawlers_are_completed(
    clients: List[BaseClient],
    targetUris: List[str],
    regions: List[str],
    crawler_names: List[str],
    timeout: float = 600.0,
    sleep_time: float = 20.0,
) -> bool:
    """Wait until glue crawlers are complete."""

    @poller(
        check_success=_crawler_status_processed_checker,
        timeout=timeout,
        sleep_time=sleep_time,
    )
    def _wait_glue_crawlers_are_completed() -> List[str]:
        crawler_status: List[str] = []
        for index, uri in enumerate(targetUris):
            logger.info(
                f"checking crawler {crawler_names[index]} status of dataset uri: {uri}"
            )
            dataset_creds = json.loads(
                clients[index].generate_dataset_access_token(datasetUri=uri)
            )
            session = boto3.Session(
                aws_access_key_id=dataset_creds.get("AccessKey"),
                aws_secret_access_key=dataset_creds.get("SessionKey"),
                aws_session_token=dataset_creds.get("sessionToken"),
            )

            current_crawler = session.client(
                "glue", region_name=regions[index]
            ).get_crawler(Name=crawler_names[index])

            crawler_status.append(current_crawler.get("Crawler", {}).get("State", ""))
        return crawler_status

    return _wait_glue_crawlers_are_completed()
