"""Standalone Python worker to create a transcription on Arkindex elements"""

import logging
import os
from argparse import ArgumentParser, Namespace
from typing import Any
from urllib.parse import urljoin

import requests

# Initialize the logger to provide feedback about the worker's execution to the final user
logging.basicConfig(
    format="%(asctime)s %(levelname)s/%(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Below are listed the environment variables which are mandatory to run this worker
ARKINDEX_API_URL = "ARKINDEX_API_URL"
"""URL that points to the root of the Arkindex instance.
"""
ARKINDEX_API_TOKEN = "ARKINDEX_API_TOKEN"
"""Personal token to authenticate to the Arkindex instance, useful when running locally.
"""
ARKINDEX_TASK_TOKEN = "ARKINDEX_TASK_TOKEN"
"""Machine token to authenticate to the Arkindex instance, useful when running from Arkindex.
"""
ARKINDEX_WORKER_RUN_ID = "ARKINDEX_WORKER_RUN_ID"
"""Identifier to publish worker results.
"""


def parse_args() -> Namespace:
    """Helper to parse command line arguments.
    This worker only supports one optional argument, a list of element IDs to process.

    :return Namespace: A namespace containing the provided command arguments and their value.
    """
    parser = ArgumentParser("python worker.py")
    parser.add_argument(
        "--element",
        nargs="+",
        help="One or more Arkindex element ID",
    )
    return parser.parse_args()


def arkindex_request(
    method: str, endpoint_path: str, body: dict[str, Any] | None = None
) -> dict:
    """Helper to query any endpoint from the Arkindex API.
    The environment variables named `ARKINDEX_API_URL` and `ARKINDEX_API_TOKEN` (or `ARKINDEX_TASK_TOKEN`) are required to use this helper.

    :param str method: The HTTP request method to use https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
    :param str endpoint_path: The path of the API endpoint to query
    :param dict[str, Any] | None body: A JSON body to send to the API, defaults to None
    :return dict: The JSON response from the API endpoint
    """
    if body is None:
        body = {}

    # Use the `ARKINDEX_API_URL` environment variable to define the full endpoint URL
    url = urljoin(os.getenv(ARKINDEX_API_URL), endpoint_path)

    # The authorization varies when running locally or in Arkindex
    if "ARKINDEX_TASK_TOKEN" in os.environ:
        authorization = f"Ponos {os.getenv(ARKINDEX_TASK_TOKEN)}"
    else:
        authorization = f"Token {os.getenv(ARKINDEX_API_TOKEN)}"

    # Query the endpoint URL using the `requests` Python package
    response = requests.request(
        method=method,
        url=url,
        headers={"Authorization": authorization},
        json=body,
    )

    # Raise an exception if anything went wrong while querying the endpoint
    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.error(
            f"Request `{endpoint_path}` failed with code {response.status_code}: {response.content}"
        )
        raise

    # Return the response in JSON format if it was successful
    return response.json()


def main() -> None:
    """Standalone Python worker to create a transcription on Arkindex elements"""
    # Check that the required environment variables are available
    for variable in (ARKINDEX_API_URL, ARKINDEX_WORKER_RUN_ID):
        assert os.getenv(variable), (
            f"Missing required variable `{variable}` in the environment."
        )

    assert os.getenv(ARKINDEX_API_TOKEN) or os.getenv(ARKINDEX_TASK_TOKEN), (
        f"Either `{ARKINDEX_API_TOKEN}` or `{ARKINDEX_TASK_TOKEN}` variable must be set in the environment."
    )

    # Retrieve the worker configuration from Arkindex
    # API endpoint: https://arkindex.teklia.com/api-docs/#tag/process/operation/RetrieveWorkerRun
    configuration = arkindex_request(
        method="get",
        endpoint_path=f"process/workers/{os.getenv(ARKINDEX_WORKER_RUN_ID)}/",
    )

    # Build the list of elements to process
    elements = []

    # Option 1: The worker is running locally, on your machine, we use the value of the `--element` command argument
    if configuration["process"]["mode"] == "local":
        # Parse the provided command arguments
        args = parse_args()

        # Retrieve the list of elements from the `--element` argument
        elements = args.element

        # Assert that at least one element was provided to run the worker on
        assert elements, (
            "Missing at least one element ID to process while running the worker locally."
        )

    # Option 2: The worker is running on Arkindex, in a process, we list process elements
    else:
        # Retrieve the list of elements from the process which is currently running
        # API endpoint: https://arkindex.teklia.com/api-docs/#tag/process/operation/ListProcessElements
        json_response = arkindex_request(
            method="get",
            endpoint_path=f"process/{configuration['process']['id']}/elements/",
        )

        # We only need the ID of each element to process, other information is not necessary
        elements = [element["id"] for element in json_response["results"]]

    total = len(elements)
    failed = 0
    # Iterate over all elements to create a basic transcription
    for element_id in elements:
        try:
            # Create the "Hello world!" transcription on the current element
            # API endpoint: https://arkindex.teklia.com/api-docs/#tag/transcriptions/operation/CreateTranscription
            transcription = arkindex_request(
                method="post",
                endpoint_path=f"element/{element_id}/transcription/",
                body={
                    "text": "Hello world!",
                    "worker_run_id": os.getenv(ARKINDEX_WORKER_RUN_ID),
                    "confidence": 1.0,
                },
            )

            # Output feedback when a transcription is successfully created
            logger.info(
                f"A transcription with the ID {transcription['id']} was successfully created on element {element_id}."
            )

        except Exception:
            # Output feedback when failing to create a transcription, and increment the `failed` counter
            logger.error(f"Failed to create a transcription on element {element_id}.")
            failed += 1

    completed = total - failed
    # Output a summary of the worker execution over all provided elements
    logger.info(f"Ran on {total} element(s): {completed} completed, {failed} error(s).")


if __name__ == "__main__":
    main()
