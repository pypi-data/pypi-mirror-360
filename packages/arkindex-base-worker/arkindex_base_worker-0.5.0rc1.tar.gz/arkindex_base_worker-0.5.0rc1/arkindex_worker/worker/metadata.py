"""
ElementsWorker methods for metadata.
"""

from enum import Enum

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement, unsupported_cache
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE, batch_publication, make_batches


class MetaType(Enum):
    """
    Type of a metadata.
    """

    Text = "text"
    """
    A regular string with no special interpretation.
    """

    HTML = "html"
    """
    A metadata with a string value that should be interpreted as HTML content.
    The allowed HTML tags are restricted for security reasons.
    """

    Date = "date"
    """
    A metadata with a string value that should be interpreted as a date.
    The date should be formatted as an ISO 8601 date (``YYYY-MM-DD``).
    """

    Location = "location"
    """
    A metadata with a string value that should be interpreted as a location.
    """

    Reference = "reference"
    """
    A metadata with a string value that should be interpreted as an external identifier
    to this element, for example to preserve a link to the original data before it was
    imported into Arkindex.
    """

    Numeric = "numeric"
    """
    A metadata with a floating point value.
    """

    URL = "url"
    """
    A metadata with a string value that should be interpreted as a URL.
    Only the ``http`` and ``https`` schemes are allowed.
    """


class MetaDataMixin:
    @unsupported_cache
    def create_metadata(
        self,
        element: Element | CachedElement,
        type: MetaType,
        name: str,
        value: str,
    ) -> str:
        """
        Create a metadata on the given element through API.

        :param element: The element to create a metadata on.
        :param type: Type of the metadata.
        :param name: Name of the metadata.
        :param value: Value of the metadata.
        :returns: UUID of the created metadata.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be of type Element or CachedElement"
        )
        assert type and isinstance(type, MetaType), (
            "type shouldn't be null and should be of type MetaType"
        )
        assert name and isinstance(name, str), (
            "name shouldn't be null and should be of type str"
        )
        assert value and isinstance(value, str), (
            "value shouldn't be null and should be of type str"
        )
        if self.is_read_only:
            logger.warning("Cannot create metadata as this worker is in read-only mode")
            return

        metadata = self.api_client.request(
            "CreateMetaData",
            id=element.id,
            body={
                "type": type.value,
                "name": name,
                "value": value,
                "worker_run_id": self.worker_run_id,
            },
        )

        return metadata["id"]

    @unsupported_cache
    @batch_publication
    def create_metadata_bulk(
        self,
        element: Element | CachedElement,
        metadata_list: list[dict[str, MetaType | str | int | float | None]],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[dict[str, str]]:
        """
        Create multiple metadata on an existing element.
        This method does not support cache.

        :param element: The element to create multiple metadata on.
        :param metadata_list: The list of dict whose keys are the following:
            - type: MetaType
            - name: str
            - value: str | int | float
        :param batch_size: The size of each batch, which will be used to split the publication to avoid API errors.

        :returns: A list of dicts as returned in the ``metadata_list`` field by the ``CreateMetaDataBulk`` API endpoint.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be of type Element or CachedElement"
        )

        assert metadata_list and isinstance(metadata_list, list), (
            "metadata_list shouldn't be null and should be of type list of dict"
        )

        # Make a copy to avoid modifying the metadata_list argument
        metas = []
        for index, metadata in enumerate(metadata_list):
            assert isinstance(metadata, dict), (
                f"Element at index {index} in metadata_list: Should be of type dict"
            )

            assert metadata.get("type") and isinstance(
                metadata.get("type"), MetaType
            ), "type shouldn't be null and should be of type MetaType"

            assert metadata.get("name") and isinstance(metadata.get("name"), str), (
                "name shouldn't be null and should be of type str"
            )

            assert metadata.get("value") is not None and isinstance(
                metadata.get("value"), str | float | int
            ), "value shouldn't be null and should be of type (str or float or int)"

            metas.append(
                {
                    "type": metadata.get("type").value,
                    "name": metadata.get("name"),
                    "value": metadata.get("value"),
                }
            )

        if self.is_read_only:
            logger.warning("Cannot create metadata as this worker is in read-only mode")
            return

        created_metadata_list = [
            created_metadata
            for batch in make_batches(metas, "metadata", batch_size)
            for created_metadata in self.api_client.request(
                "CreateMetaDataBulk",
                id=element.id,
                body={
                    "worker_run_id": self.worker_run_id,
                    "metadata_list": batch,
                },
            )["metadata_list"]
        ]

        return created_metadata_list

    def list_element_metadata(
        self, element: Element | CachedElement, load_parents: bool | None = None
    ) -> list[dict[str, str]]:
        """
        List all metadata linked to an element.
        This method does not support cache.

        :param element: The element to list metadata on.
        :param load_parents: Also include all metadata from the element's parents in the response.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be of type Element or CachedElement"
        )

        query_params = {}
        if load_parents is not None:
            assert isinstance(load_parents, bool), "load_parents should be of type bool"
            query_params["load_parents"] = load_parents

        return self.api_client.paginate(
            "ListElementMetaData", id=element.id, **query_params
        )
