import logging
import uuid
from argparse import ArgumentTypeError

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.models import Dataset, Set
from arkindex_worker.worker.dataset import (
    DatasetState,
    MissingDatasetArchive,
    check_dataset_set,
)
from tests import FIXTURES_DIR, PROCESS_ID
from tests.test_elements_worker import BASE_API_CALLS

RANDOM_UUID = uuid.uuid4()


@pytest.fixture
def tmp_archive(tmp_path):
    archive = tmp_path / "test_archive.tar.zst"
    archive.touch()

    yield archive

    archive.unlink(missing_ok=True)


@pytest.mark.parametrize(
    ("value", "error"),
    [("train", ""), (f"{RANDOM_UUID}:train:val", ""), ("not_uuid:train", "")],
)
def test_check_dataset_set_errors(value, error):
    with pytest.raises(ArgumentTypeError, match=error):
        check_dataset_set(value)


def test_check_dataset_set():
    assert check_dataset_set(f"{RANDOM_UUID}:train") == (RANDOM_UUID, "train")


def test_cleanup_downloaded_artifact_no_download(mock_dataset_worker):
    assert not mock_dataset_worker.downloaded_dataset_artifact
    # Do nothing
    mock_dataset_worker.cleanup_downloaded_artifact()


def test_cleanup_downloaded_artifact(mock_dataset_worker, tmp_archive):
    mock_dataset_worker.downloaded_dataset_artifact = tmp_archive

    assert mock_dataset_worker.downloaded_dataset_artifact.exists()
    # Unlink the downloaded archive
    mock_dataset_worker.cleanup_downloaded_artifact()
    assert not mock_dataset_worker.downloaded_dataset_artifact.exists()

    # Unlinking again does not raise an error even if the archive no longer exists
    mock_dataset_worker.cleanup_downloaded_artifact()


def test_download_dataset_artifact_list_api_error(
    responses, mock_dataset_worker, default_dataset
):
    task_id = default_dataset.task_id

    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{task_id}/artifacts/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_dataset_worker.download_dataset_artifact(default_dataset)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{task_id}/artifacts/")
    ]


def test_download_dataset_artifact_download_api_error(
    responses, mock_dataset_worker, default_dataset
):
    task_id = default_dataset.task_id

    expected_results = [
        {
            "id": "artifact_1",
            "path": "dataset_id.tar.zst",
            "size": 42,
            "content_type": "application/zstd",
            "s3_put_url": None,
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        },
        {
            "id": "artifact_2",
            "path": "logs.log",
            "size": 42,
            "content_type": "text/plain",
            "s3_put_url": None,
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        },
    ]
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{task_id}/artifacts/",
        status=200,
        json=expected_results,
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{task_id}/artifact/dataset_id.tar.zst",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_dataset_worker.download_dataset_artifact(default_dataset)

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{task_id}/artifacts/"),
        ("GET", f"http://testserver/api/v1/task/{task_id}/artifact/dataset_id.tar.zst"),
    ]


def test_download_dataset_artifact_no_archive(
    responses, mock_dataset_worker, default_dataset
):
    task_id = default_dataset.task_id

    expected_results = [
        {
            "id": "artifact_id",
            "path": "logs.log",
            "size": 42,
            "content_type": "text/plain",
            "s3_put_url": None,
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        },
    ]
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{task_id}/artifacts/",
        status=200,
        json=expected_results,
    )

    with pytest.raises(
        MissingDatasetArchive,
        match="The dataset compressed archive artifact was not found.",
    ):
        mock_dataset_worker.download_dataset_artifact(default_dataset)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{task_id}/artifacts/"),
    ]


@pytest.mark.parametrize("downloaded_cache", [False, True])
def test_download_dataset_artifact(
    mocker,
    tmp_path,
    responses,
    mock_dataset_worker,
    default_dataset,
    downloaded_cache,
    tmp_archive,
):
    task_id = default_dataset.task_id
    archive_path = (
        FIXTURES_DIR
        / "extract_parent_archives"
        / "first_parent"
        / "arkindex_data.tar.zst"
    )
    mocker.patch(
        "arkindex_worker.worker.base.BaseWorker.find_extras_directory",
        return_value=tmp_path,
    )

    expected_results = [
        {
            "id": "artifact_1",
            "path": "dataset_id.tar.zst",
            "size": 42,
            "content_type": "application/zstd",
            "s3_put_url": None,
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        },
        {
            "id": "artifact_2",
            "path": "logs.log",
            "size": 42,
            "content_type": "text/plain",
            "s3_put_url": None,
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        },
    ]
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{task_id}/artifacts/",
        status=200,
        json=expected_results,
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{task_id}/artifact/dataset_id.tar.zst",
        status=200,
        body=archive_path.read_bytes(),
        content_type="application/zstd",
    )

    if downloaded_cache:
        mock_dataset_worker.downloaded_dataset_artifact = tmp_archive
    previous_artifact = mock_dataset_worker.downloaded_dataset_artifact

    mock_dataset_worker.download_dataset_artifact(default_dataset)

    # We removed the artifact that was downloaded previously
    if previous_artifact:
        assert not previous_artifact.exists()

    assert (
        mock_dataset_worker.downloaded_dataset_artifact
        == tmp_path / "dataset_id.tar.zst"
    )
    assert (
        mock_dataset_worker.downloaded_dataset_artifact.read_bytes()
        == archive_path.read_bytes()
    )
    mock_dataset_worker.downloaded_dataset_artifact.unlink()

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{task_id}/artifacts/"),
        ("GET", f"http://testserver/api/v1/task/{task_id}/artifact/dataset_id.tar.zst"),
    ]


def test_download_dataset_artifact_already_exists(
    mocker, tmp_path, responses, mock_dataset_worker, default_dataset
):
    mocker.patch(
        "arkindex_worker.worker.base.BaseWorker.find_extras_directory",
        return_value=tmp_path,
    )
    already_downloaded = tmp_path / "dataset_id.tar.zst"
    already_downloaded.write_bytes(b"Some content")
    mock_dataset_worker.downloaded_dataset_artifact = already_downloaded

    mock_dataset_worker.download_dataset_artifact(default_dataset)

    assert mock_dataset_worker.downloaded_dataset_artifact == already_downloaded
    already_downloaded.unlink()

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_list_sets_api_error(responses, mock_dataset_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/process/{PROCESS_ID}/sets/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_dataset_worker.list_sets())

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # The API call is retried 5 times
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
    ]


def test_list_sets(responses, mock_dataset_worker):
    expected_results = [
        {
            "id": "set_1",
            "dataset": {
                "id": "dataset_1",
                "name": "Dataset 1",
                "description": "My first great dataset",
                "sets": [
                    {"id": "set_1", "name": "train"},
                    {"id": "set_2", "name": "val"},
                ],
                "state": "open",
                "corpus_id": "corpus_id",
                "creator": "test@teklia.com",
                "task_id": "task_id_1",
            },
            "set_name": "train",
        },
        {
            "id": "set_2",
            "dataset": {
                "id": "dataset_1",
                "name": "Dataset 1",
                "description": "My first great dataset",
                "sets": [
                    {"id": "set_1", "name": "train"},
                    {"id": "set_2", "name": "val"},
                ],
                "state": "open",
                "corpus_id": "corpus_id",
                "creator": "test@teklia.com",
                "task_id": "task_id_1",
            },
            "set_name": "val",
        },
        {
            "id": "set_3",
            "dataset": {
                "id": "dataset_2",
                "name": "Dataset 2",
                "description": "My second great dataset",
                "sets": [{"id": "set_3", "name": "my_set"}],
                "state": "complete",
                "corpus_id": "corpus_id",
                "creator": "test@teklia.com",
                "task_id": "task_id_2",
            },
            "set_name": "my_set",
        },
    ]
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/process/{PROCESS_ID}/sets/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_results,
        },
    )

    for idx, dataset_set in enumerate(mock_dataset_worker.list_process_sets()):
        assert isinstance(dataset_set, Set)
        assert dataset_set.name == expected_results[idx]["set_name"]

        assert isinstance(dataset_set.dataset, Dataset)
        assert dataset_set.dataset == expected_results[idx]["dataset"]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
    ]


def test_list_sets_retrieve_dataset_api_error(
    responses, mock_dev_dataset_worker, default_dataset
):
    mock_dev_dataset_worker.args.set = [
        (default_dataset.id, "train"),
        (default_dataset.id, "val"),
    ]

    responses.add(
        responses.GET,
        f"http://testserver/api/v1/datasets/{default_dataset.id}/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        next(mock_dev_dataset_worker.list_sets())

    assert len(responses.calls) == 1
    assert [(call.request.method, call.request.url) for call in responses.calls] == [
        ("GET", f"http://testserver/api/v1/datasets/{default_dataset.id}/")
    ]


def test_list_sets_read_only(responses, mock_dev_dataset_worker, default_dataset):
    mock_dev_dataset_worker.args.set = [
        (default_dataset.id, "train"),
        (default_dataset.id, "val"),
    ]

    responses.add(
        responses.GET,
        f"http://testserver/api/v1/datasets/{default_dataset.id}/",
        status=200,
        json=default_dataset,
    )

    assert list(mock_dev_dataset_worker.list_sets()) == [
        Set(name="train", dataset=default_dataset),
        Set(name="val", dataset=default_dataset),
    ]

    assert len(responses.calls) == 1
    assert [(call.request.method, call.request.url) for call in responses.calls] == [
        ("GET", f"http://testserver/api/v1/datasets/{default_dataset.id}/"),
    ]


def test_run_no_sets(mocker, caplog, mock_dataset_worker):
    mocker.patch("arkindex_worker.worker.DatasetWorker.list_sets", return_value=[])

    with pytest.raises(SystemExit):
        mock_dataset_worker.run()

    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (logging.INFO, "Loaded Worker Fake worker @ 123412 from API"),
        (logging.WARNING, "No sets to process, stopping."),
    ]


def test_run_initial_dataset_state_error(
    mocker, responses, caplog, mock_dataset_worker, default_dataset
):
    default_dataset.state = DatasetState.Building.value
    mocker.patch(
        "arkindex_worker.worker.DatasetWorker.list_sets",
        return_value=[Set(name="train", dataset=default_dataset)],
    )

    with pytest.raises(SystemExit):
        mock_dataset_worker.run()

    assert len(responses.calls) == len(BASE_API_CALLS) * 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS * 2

    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (logging.INFO, "Loaded Worker Fake worker @ 123412 from API"),
        (
            logging.WARNING,
            "Failed running worker on Set (train) from Dataset (dataset_id): AssertionError('When processing a set, its dataset state should be Complete.')",
        ),
        (logging.ERROR, "Ran on 1 set: 0 completed, 1 failed"),
    ]


def test_run_download_dataset_artifact_api_error(
    mocker,
    tmp_path,
    responses,
    caplog,
    mock_dataset_worker,
    default_dataset,
):
    default_dataset.state = DatasetState.Complete.value
    mocker.patch(
        "arkindex_worker.worker.DatasetWorker.list_sets",
        return_value=[Set(name="train", dataset=default_dataset)],
    )
    mocker.patch(
        "arkindex_worker.worker.base.BaseWorker.find_extras_directory",
        return_value=tmp_path,
    )

    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/",
        status=418,
    )

    with pytest.raises(SystemExit):
        mock_dataset_worker.run()

    assert len(responses.calls) == len(BASE_API_CALLS) * 2 + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS * 2 + [
        ("GET", f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/")
    ]

    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (logging.INFO, "Loaded Worker Fake worker @ 123412 from API"),
        (
            logging.INFO,
            "Retrieving data for Set (train) from Dataset (dataset_id) (1/1)",
        ),
        (logging.INFO, "Downloading artifact for Dataset (dataset_id)"),
        (
            logging.WARNING,
            "An API error occurred while processing Set (train) from Dataset (dataset_id): 418 I'm a Teapot - None",
        ),
        (
            logging.ERROR,
            "Ran on 1 set: 0 completed, 1 failed",
        ),
    ]


def test_run_no_downloaded_dataset_artifact_error(
    mocker,
    tmp_path,
    responses,
    caplog,
    mock_dataset_worker,
    default_dataset,
):
    default_dataset.state = DatasetState.Complete.value
    mocker.patch(
        "arkindex_worker.worker.DatasetWorker.list_sets",
        return_value=[Set(name="train", dataset=default_dataset)],
    )
    mocker.patch(
        "arkindex_worker.worker.base.BaseWorker.find_extras_directory",
        return_value=tmp_path,
    )

    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/",
        status=200,
        json={},
    )

    with pytest.raises(SystemExit):
        mock_dataset_worker.run()

    assert len(responses.calls) == len(BASE_API_CALLS) * 2 + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS * 2 + [
        ("GET", f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/"),
    ]

    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (logging.INFO, "Loaded Worker Fake worker @ 123412 from API"),
        (
            logging.INFO,
            "Retrieving data for Set (train) from Dataset (dataset_id) (1/1)",
        ),
        (logging.INFO, "Downloading artifact for Dataset (dataset_id)"),
        (
            logging.WARNING,
            "Failed running worker on Set (train) from Dataset (dataset_id): MissingDatasetArchive('The dataset compressed archive artifact was not found.')",
        ),
        (
            logging.ERROR,
            "Ran on 1 set: 0 completed, 1 failed",
        ),
    ]


def test_run(
    mocker,
    tmp_path,
    responses,
    caplog,
    mock_dataset_worker,
    default_dataset,
    default_artifact,
):
    default_dataset.state = DatasetState.Complete.value
    mocker.patch(
        "arkindex_worker.worker.DatasetWorker.list_sets",
        return_value=[Set(name="train", dataset=default_dataset)],
    )
    mocker.patch(
        "arkindex_worker.worker.base.BaseWorker.find_extras_directory",
        return_value=tmp_path,
    )
    mock_process = mocker.patch("arkindex_worker.worker.DatasetWorker.process_set")

    archive_path = (
        FIXTURES_DIR
        / "extract_parent_archives"
        / "first_parent"
        / "arkindex_data.tar.zst"
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/",
        status=200,
        json=[default_artifact],
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{default_dataset.task_id}/artifact/dataset_id.tar.zst",
        status=200,
        body=archive_path.read_bytes(),
        content_type="application/zstd",
    )

    mock_dataset_worker.run()

    assert mock_process.call_count == 1

    assert len(responses.calls) == len(BASE_API_CALLS) * 2 + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS * 2 + [
        (
            "GET",
            f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/task/{default_dataset.task_id}/artifact/dataset_id.tar.zst",
        ),
    ]

    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (logging.INFO, "Loaded Worker Fake worker @ 123412 from API"),
        (
            logging.INFO,
            "Retrieving data for Set (train) from Dataset (dataset_id) (1/1)",
        ),
        (logging.INFO, "Downloading artifact for Dataset (dataset_id)"),
        (logging.INFO, "Processing Set (train) from Dataset (dataset_id) (1/1)"),
        (logging.INFO, "Ran on 1 set: 1 completed, 0 failed"),
    ]


def test_run_read_only(
    mocker,
    tmp_path,
    responses,
    caplog,
    mock_dev_dataset_worker,
    default_dataset,
    default_artifact,
):
    default_dataset.state = DatasetState.Complete.value
    mocker.patch(
        "arkindex_worker.worker.DatasetWorker.list_sets",
        return_value=[Set(name="train", dataset=default_dataset)],
    )
    mocker.patch(
        "arkindex_worker.worker.base.BaseWorker.find_extras_directory",
        return_value=tmp_path,
    )
    mock_process = mocker.patch("arkindex_worker.worker.DatasetWorker.process_set")

    archive_path = (
        FIXTURES_DIR
        / "extract_parent_archives"
        / "first_parent"
        / "arkindex_data.tar.zst"
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/",
        status=200,
        json=[default_artifact],
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{default_dataset.task_id}/artifact/dataset_id.tar.zst",
        status=200,
        body=archive_path.read_bytes(),
        content_type="application/zstd",
    )

    mock_dev_dataset_worker.run()

    assert mock_process.call_count == 1

    assert len(responses.calls) == 2
    assert [(call.request.method, call.request.url) for call in responses.calls] == [
        (
            "GET",
            f"http://testserver/api/v1/task/{default_dataset.task_id}/artifacts/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/task/{default_dataset.task_id}/artifact/dataset_id.tar.zst",
        ),
    ]

    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (logging.WARNING, "Running without any extra configuration"),
        (
            logging.INFO,
            "Retrieving data for Set (train) from Dataset (dataset_id) (1/1)",
        ),
        (logging.INFO, "Downloading artifact for Dataset (dataset_id)"),
        (logging.INFO, "Processing Set (train) from Dataset (dataset_id) (1/1)"),
        (logging.INFO, "Ran on 1 set: 1 completed, 0 failed"),
    ]
