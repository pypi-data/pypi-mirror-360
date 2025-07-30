import uuid

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.models import Artifact
from tests import FIXTURES_DIR
from tests.test_elements_worker import BASE_API_CALLS

TASK_ID = uuid.UUID("cafecafe-cafe-cafe-cafe-cafecafecafe")


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Task ID
        (
            {"task_id": None},
            "task_id shouldn't be null and should be an UUID",
        ),
        (
            {"task_id": "12341234-1234-1234-1234-123412341234"},
            "task_id shouldn't be null and should be an UUID",
        ),
    ],
)
def test_list_artifacts_wrong_param_task_id(mock_dataset_worker, payload, error):
    with pytest.raises(AssertionError, match=error):
        mock_dataset_worker.list_artifacts(**payload)


def test_list_artifacts_api_error(responses, mock_dataset_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{TASK_ID}/artifacts/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_dataset_worker.list_artifacts(task_id=TASK_ID)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{TASK_ID}/artifacts/")
    ]


def test_list_artifacts(
    responses,
    mock_dataset_worker,
):
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
        f"http://testserver/api/v1/task/{TASK_ID}/artifacts/",
        status=200,
        json=expected_results,
    )

    for idx, artifact in enumerate(mock_dataset_worker.list_artifacts(task_id=TASK_ID)):
        assert isinstance(artifact, Artifact)
        assert artifact == expected_results[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{TASK_ID}/artifacts/"),
    ]


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Task ID
        (
            {"task_id": None},
            "task_id shouldn't be null and should be an UUID",
        ),
        (
            {"task_id": "12341234-1234-1234-1234-123412341234"},
            "task_id shouldn't be null and should be an UUID",
        ),
    ],
)
def test_download_artifact_wrong_param_task_id(
    mock_dataset_worker, default_artifact, payload, error
):
    api_payload = {
        "task_id": TASK_ID,
        "artifact": default_artifact,
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_dataset_worker.download_artifact(**api_payload)


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Artifact
        (
            {"artifact": None},
            "artifact shouldn't be null and should be an Artifact",
        ),
        (
            {"artifact": "not artifact type"},
            "artifact shouldn't be null and should be an Artifact",
        ),
    ],
)
def test_download_artifact_wrong_param_artifact(
    mock_dataset_worker, default_artifact, payload, error
):
    api_payload = {
        "task_id": TASK_ID,
        "artifact": default_artifact,
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_dataset_worker.download_artifact(**api_payload)


def test_download_artifact_api_error(responses, mock_dataset_worker, default_artifact):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{TASK_ID}/artifact/dataset_id.tar.zst",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_dataset_worker.download_artifact(
            task_id=TASK_ID, artifact=default_artifact
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{TASK_ID}/artifact/dataset_id.tar.zst")
    ]


def test_download_artifact(
    responses,
    mock_dataset_worker,
    default_artifact,
):
    archive_path = (
        FIXTURES_DIR
        / "extract_parent_archives"
        / "first_parent"
        / "arkindex_data.tar.zst"
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/task/{TASK_ID}/artifact/dataset_id.tar.zst",
        status=200,
        body=archive_path.read_bytes(),
        content_type="application/zstd",
    )

    assert (
        mock_dataset_worker.download_artifact(
            task_id=TASK_ID, artifact=default_artifact
        ).read()
        == archive_path.read_bytes()
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/task/{TASK_ID}/artifact/dataset_id.tar.zst"),
    ]
