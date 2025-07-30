from collections.abc import Iterator
from enum import Enum

from arkindex_worker.cache import unsupported_cache

# Increases the number of elements returned per page by the API
PROCESS_ELEMENTS_PAGE_SIZE = 500


class ActivityState(Enum):
    """
    Processing state of an element.
    """

    Queued = "queued"
    """
    The element has not yet been processed by a worker.
    """

    Started = "started"
    """
    The element is being processed by a worker.
    """

    Processed = "processed"
    """
    The element has been successfully processed by a worker.
    """

    Error = "error"
    """
    An error occurred while processing this element.
    """


class ProcessMode(Enum):
    """
    Mode of the process of the worker.
    """

    Files = "files"
    """
    Processes of files (images, PDFs, IIIF, ...) imports.
    """

    Workers = "workers"
    """
    Processes of worker executions.
    """

    Template = "template"
    """
    Process templates.
    """

    S3 = "s3"
    """
    Processes of imports from an S3-compatible storage.
    """

    Local = "local"
    """
    Local processes.
    """

    Dataset = "dataset"
    """
    Dataset processes.
    """

    Export = "export"
    """
    Export processes.
    """


class ProcessMixin:
    @unsupported_cache
    def list_process_elements(self, with_image: bool = False) -> Iterator[dict]:
        """
        List the elements of a process.

        :param with_image: whether or not to include zone and image information in the elements response.
        :returns: the process' elements.
        """
        return self.api_client.paginate(
            "ListProcessElements",
            id=self.process_information["id"],
            with_image=with_image,
            allow_missing_data=True,
            page_size=PROCESS_ELEMENTS_PAGE_SIZE,
        )
