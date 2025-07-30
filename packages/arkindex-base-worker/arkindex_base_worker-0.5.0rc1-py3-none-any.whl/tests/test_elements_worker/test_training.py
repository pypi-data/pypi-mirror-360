import logging
import sys

import pytest

from arkindex.mock import MockApiClient
from arkindex_worker.worker import BaseWorker
from arkindex_worker.worker.training import TrainingMixin, create_archive


@pytest.fixture
def mock_training_worker(monkeypatch):
    class TrainingWorker(BaseWorker, TrainingMixin):
        """
        This class is needed to run tests in the context of a training worker
        """

    monkeypatch.setattr(sys, "argv", ["worker"])
    training_worker = TrainingWorker()
    training_worker.api_client = MockApiClient()
    training_worker.args = training_worker.parser.parse_args()
    return training_worker


@pytest.fixture
def default_model_version():
    return {
        "id": "model_version_id",
        "model_id": "model_id",
        "state": "created",
        "parent": "42" * 16,
        "tag": "A simple tag",
        "description": "A description",
        "configuration": {"test": "value"},
        "s3_url": None,
        "s3_put_url": "http://upload.archive",
        "hash": None,
        "archive_hash": None,
        "size": None,
        "created": "2000-01-01T00:00:00Z",
    }


def test_create_archive(model_file_dir):
    """Create an archive with all base attributes"""

    with create_archive(path=model_file_dir) as (
        zst_archive_path,
        hash,
        size,
        archive_hash,
    ):
        assert zst_archive_path.exists(), "The archive was not created"
        assert hash == "c5aedde18a768757351068b840c8c8f9", (
            "Hash was not properly computed"
        )
        assert 300 < size < 700

    assert not zst_archive_path.exists(), "Auto removal failed"


def test_create_archive_with_subfolder(model_file_dir_with_subfolder):
    """Create an archive when the model's file is in a folder containing a subfolder"""

    with create_archive(path=model_file_dir_with_subfolder) as (
        zst_archive_path,
        hash,
        size,
        archive_hash,
    ):
        assert zst_archive_path.exists(), "The archive was not created"
        assert hash == "3e453881404689e6e125144d2db3e605", (
            "Hash was not properly computed"
        )
        assert 300 < size < 1500

    assert not zst_archive_path.exists(), "Auto removal failed"


def test_handle_s3_uploading_errors(responses, mock_training_worker, model_file_dir):
    s3_endpoint_url = "http://s3.localhost.com"
    responses.add_passthru(s3_endpoint_url)
    responses.add(responses.PUT, s3_endpoint_url, status=400)

    mock_training_worker.model_version = {
        "state": "Created",
        "s3_put_url": s3_endpoint_url,
    }

    file_path = model_file_dir / "model_file.pth"
    with pytest.raises(
        Exception,
        match="400 Client Error: Bad Request for url: http://s3.localhost.com/",
    ):
        mock_training_worker.upload_to_s3(file_path)


@pytest.mark.parametrize(
    "method",
    [
        "publish_model_version",
        "create_model_version",
        "update_model_version",
        "upload_to_s3",
        "validate_model_version",
    ],
)
def test_training_mixin_read_only(mock_training_worker, method, caplog):
    """All operations related to models versions returns early if the worker is configured as read only"""
    # Set worker in read_only mode
    mock_training_worker.worker_run_id = None
    assert mock_training_worker.is_read_only

    assert mock_training_worker.model_version is None
    getattr(mock_training_worker, method)()
    assert mock_training_worker.model_version is None
    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (
            logging.WARNING,
            "Cannot perform this operation as the worker is in read-only mode",
        ),
    ]


def test_create_model_version_already_created(mock_training_worker):
    mock_training_worker.model_version = {"id": "model_version_id"}
    with pytest.raises(
        AssertionError, match="A model version has already been created."
    ):
        mock_training_worker.create_model_version(model_id="model_id")


@pytest.mark.parametrize("set_tag", [True, False])
def test_create_model_version(mock_training_worker, default_model_version, set_tag):
    args = {
        "parent": "42" * 16,
        "tag": "A simple tag",
        "description": "A description",
        "configuration": {"test": "value"},
    }
    if not set_tag:
        del args["tag"]
        default_model_version["tag"] = None
    mock_training_worker.api_client.add_response(
        "CreateModelVersion",
        id="model_id",
        response=default_model_version,
        body=args,
    )
    assert mock_training_worker.model_version is None
    mock_training_worker.create_model_version(model_id="model_id", **args)
    assert mock_training_worker.model_version == default_model_version


def test_update_model_version_not_created(mock_training_worker):
    with pytest.raises(AssertionError, match="No model version has been created yet."):
        mock_training_worker.update_model_version()


def test_update_model_version(mock_training_worker, default_model_version):
    mock_training_worker.model_version = default_model_version
    args = {"tag": "A new tag"}
    new_model_version = {**default_model_version, "tag": "A new tag"}
    mock_training_worker.api_client.add_response(
        "UpdateModelVersion",
        id="model_version_id",
        response=new_model_version,
        body=args,
    )
    mock_training_worker.update_model_version(**args)
    assert mock_training_worker.model_version == new_model_version


def test_validate_model_version_not_created(mock_training_worker):
    with pytest.raises(
        AssertionError,
        match="You must create the model version and upload its archive before validating it.",
    ):
        mock_training_worker.validate_model_version(hash="a", size=1, archive_hash="b")


@pytest.mark.parametrize("deletion_failed", [True, False])
def test_validate_model_version_hash_conflict(
    mock_training_worker,
    default_model_version,
    caplog,
    deletion_failed,
):
    mock_training_worker.model_version = {"id": "another_id"}
    args = {
        "hash": "hash",
        "archive_hash": "archive_hash",
        "size": 30,
    }
    mock_training_worker.api_client.add_error_response(
        "PartialUpdateModelVersion",
        id="another_id",
        status_code=409,
        body={"state": "available", **args},
        content={"id": ["model_version_id"]},
    )
    if deletion_failed:
        mock_training_worker.api_client.add_error_response(
            "DestroyModelVersion",
            id="another_id",
            status_code=403,
            content="Not admin",
        )
    else:
        mock_training_worker.api_client.add_response(
            "DestroyModelVersion",
            id="another_id",
            response="No content",
        )
    mock_training_worker.api_client.add_response(
        "RetrieveModelVersion",
        id="model_version_id",
        response=default_model_version,
    )

    mock_training_worker.validate_model_version(**args)
    assert mock_training_worker.model_version == default_model_version
    error_msg = []
    if deletion_failed:
        error_msg = [
            (
                logging.ERROR,
                "An error occurred removing the pending version another_id: Not admin.",
            )
        ]
    assert [
        (level, message)
        for module, level, message in caplog.record_tuples
        if module == "arkindex_worker"
    ] == [
        (
            logging.WARNING,
            "An available model version exists with hash hash, using it instead of the pending version.",
        ),
        (logging.WARNING, "Removing the pending model version."),
        *error_msg,
        (logging.INFO, "Retrieving the existing model version."),
        (logging.INFO, "Model version model_version_id is now available."),
    ]


def test_validate_model_version(mock_training_worker, default_model_version, caplog):
    mock_training_worker.model_version = {"id": "model_version_id"}
    args = {
        "hash": "hash",
        "archive_hash": "archive_hash",
        "size": 30,
    }
    mock_training_worker.api_client.add_response(
        "PartialUpdateModelVersion",
        id="model_version_id",
        body={"state": "available", **args},
        response=default_model_version,
    )

    mock_training_worker.validate_model_version(**args)
    assert mock_training_worker.model_version == default_model_version
    assert [
        (level, message)
        for module, level, message in caplog.record_tuples
        if module == "arkindex_worker"
    ] == [
        (logging.INFO, "Model version model_version_id is now available."),
    ]
