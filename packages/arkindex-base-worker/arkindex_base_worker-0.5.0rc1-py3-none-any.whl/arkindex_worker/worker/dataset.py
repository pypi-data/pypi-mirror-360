"""
BaseWorker methods for datasets.
"""

import uuid
from argparse import ArgumentTypeError
from collections.abc import Iterator
from enum import Enum

from arkindex_worker import logger
from arkindex_worker.cache import unsupported_cache
from arkindex_worker.models import Dataset, Element, Set


class DatasetState(Enum):
    """
    State of a dataset.
    """

    Open = "open"
    """
    The dataset is open.
    """

    Building = "building"
    """
    The dataset is being built.
    """

    Complete = "complete"
    """
    The dataset is complete.
    """

    Error = "error"
    """
    The dataset is in error.
    """


class MissingDatasetArchive(Exception):
    """
    Exception raised when the compressed archive associated to
    a dataset isn't found in its task artifacts.
    """


def check_dataset_set(value: str) -> tuple[uuid.UUID, str]:
    """The `--set` argument should have the following format:
    <dataset_id>:<set_name>

    Args:
        value (str): Provided argument.

    Raises:
        ArgumentTypeError: When the value is invalid.

    Returns:
        tuple[uuid.UUID, str]: The ID of the dataset parsed as UUID and the name of the set.
    """
    values = value.split(":")
    if len(values) != 2:
        raise ArgumentTypeError(
            f"'{value}' is not in the correct format `<dataset_id>:<set_name>`"
        )

    dataset_id, set_name = values
    try:
        dataset_id = uuid.UUID(dataset_id)
        return (dataset_id, set_name)
    except (TypeError, ValueError) as e:
        raise ArgumentTypeError(f"'{dataset_id}' should be a valid UUID") from e


class DatasetMixin:
    def add_arguments(self) -> None:
        """Define specific ``argparse`` arguments for the worker using this mixin"""
        self.parser.add_argument(
            "--set",
            type=check_dataset_set,
            nargs="+",
            help="""
                One or more Arkindex dataset sets, format is <dataset_uuid>:<set_name>
                (e.g.: "12341234-1234-1234-1234-123412341234:train")
            """,
            default=[],
        )
        super().add_arguments()

    def list_process_sets(self) -> Iterator[Set]:
        """
        List dataset sets associated to the worker's process. This helper is not available in developer mode.

        :returns: An iterator of ``Set`` objects built from the ``ListProcessSets`` API endpoint.
        """
        assert not self.is_read_only, "This helper is not available in read-only mode."

        results = self.api_client.paginate(
            "ListProcessSets", id=self.process_information["id"]
        )

        return map(
            lambda result: Set(
                name=result["set_name"], dataset=Dataset(**result["dataset"])
            ),
            results,
        )

    def list_set_elements(self, dataset_set: Set) -> Iterator[Element]:
        """
        List elements in a dataset set.

        :param dataset_set: Set to find elements in.
        :returns: An iterator of Element built from the ``ListDatasetElements`` API endpoint.
        """
        assert dataset_set and isinstance(dataset_set, Set), (
            "dataset_set shouldn't be null and should be a Set"
        )

        results = self.api_client.paginate(
            "ListDatasetElements", id=dataset_set.dataset.id, set=dataset_set.name
        )

        return map(lambda result: Element(**result["element"]), results)

    def list_sets(self) -> Iterator[Set]:
        """
        List the sets to be processed, either from the CLI arguments or using the
        [list_process_sets][arkindex_worker.worker.dataset.DatasetMixin.list_process_sets] method.

        :returns: An iterator of ``Set`` objects.
        """
        if not self.is_read_only:
            yield from self.list_process_sets()

        datasets: dict[uuid.UUID, Dataset] = {}
        for dataset_id, set_name in self.args.set:
            # Retrieving dataset information if not already cached
            if dataset_id not in datasets:
                datasets[dataset_id] = Dataset(
                    **self.api_client.request("RetrieveDataset", id=dataset_id)
                )

            yield Set(name=set_name, dataset=datasets[dataset_id])

    @unsupported_cache
    def update_dataset_state(self, dataset: Dataset, state: DatasetState) -> Dataset:
        """
        Partially updates a dataset state through the API.

        :param dataset: The dataset to update.
        :param state: State of the dataset.
        :returns: The updated ``Dataset`` object from the ``PartialUpdateDataset`` API endpoint.
        """
        assert dataset and isinstance(dataset, Dataset), (
            "dataset shouldn't be null and should be a Dataset"
        )
        assert state and isinstance(state, DatasetState), (
            "state shouldn't be null and should be a str from DatasetState"
        )

        if self.is_read_only:
            logger.warning("Cannot update dataset as this worker is in read-only mode")
            return

        updated_dataset = self.api_client.request(
            "PartialUpdateDataset",
            id=dataset.id,
            body={"state": state.value},
        )
        dataset.update(updated_dataset)

        return dataset
