import logging

import pytest

from arkindex_worker.cache import unsupported_cache
from arkindex_worker.utils import (
    DEFAULT_BATCH_SIZE,
    batch_publication,
    close_delete_file,
    extract_tar_zst_archive,
    parse_source_id,
)
from tests import FIXTURES_DIR

ARCHIVE = FIXTURES_DIR / "archive.tar.zst"


@pytest.mark.parametrize(
    ("source_id", "expected"),
    [
        (None, None),
        ("", None),
        (
            "cafecafe-cafe-cafe-cafe-cafecafecafe",
            "cafecafe-cafe-cafe-cafe-cafecafecafe",
        ),
        ("manual", False),
    ],
)
def test_parse_source_id(source_id, expected):
    assert parse_source_id(source_id) == expected


def test_extract_tar_zst_archive(tmp_path):
    destination = tmp_path / "destination"
    _, archive_path = extract_tar_zst_archive(ARCHIVE, destination)

    assert archive_path.is_file()
    assert archive_path.suffix == ".tar"
    assert sorted(list(destination.rglob("*"))) == [
        destination / "archive.tar.zst",
        destination / "cache",
        destination / "cache/tables.sqlite",
        destination / "line_transcriptions_small.json",
        destination / "mirrored_image.jpg",
        destination / "page_element.json",
        destination / "rotated_image.jpg",
        destination / "rotated_mirrored_image.jpg",
        destination / "test_image.jpg",
        destination / "tiled_image.jpg",
        destination / "ufcn_line_historical_worker_version.json",
    ]


def test_close_delete_file(tmp_path):
    destination = tmp_path / "destination"
    archive_fd, archive_path = extract_tar_zst_archive(ARCHIVE, destination)
    close_delete_file(archive_fd, archive_path)

    assert not archive_path.exists()


class TestMixin:
    def __init__(self, use_cache: bool = False):
        """
        Args:
            use_cache (bool, optional): To mock BaseWorker.use_cache attribute. Defaults to False.
        """
        self.use_cache = use_cache

    @batch_publication
    def custom_publication_in_batches(self, batch_size: int = DEFAULT_BATCH_SIZE):
        return batch_size

    @unsupported_cache
    @batch_publication
    def custom_publication_in_batches_without_cache(
        self, batch_size: int = DEFAULT_BATCH_SIZE
    ):
        return batch_size


def test_batch_publication_decorator_no_parameter():
    assert TestMixin().custom_publication_in_batches() == DEFAULT_BATCH_SIZE


@pytest.mark.parametrize("wrong_batch_size", [None, "not an int", 0])
def test_batch_publication_decorator_wrong_parameter(wrong_batch_size):
    with pytest.raises(
        AssertionError,
        match="batch_size shouldn't be null and should be a strictly positive integer",
    ):
        TestMixin().custom_publication_in_batches(batch_size=wrong_batch_size)


@pytest.mark.parametrize("batch_size", [1, 10, DEFAULT_BATCH_SIZE])
def test_batch_publication_decorator_right_parameter(batch_size):
    assert (
        TestMixin().custom_publication_in_batches(batch_size=batch_size) == batch_size
    )


def test_batch_publication_decorator_alongside_unsupported_cache(caplog):
    # Capture log messages
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        # Call the helper
        assert (
            TestMixin(use_cache=True).custom_publication_in_batches_without_cache()
            == DEFAULT_BATCH_SIZE
        )

    # Check logs
    assert caplog.record_tuples == [
        (
            "arkindex_worker",
            logging.WARNING,
            "This API helper `custom_publication_in_batches_without_cache` did not update the cache database",
        ),
    ]
