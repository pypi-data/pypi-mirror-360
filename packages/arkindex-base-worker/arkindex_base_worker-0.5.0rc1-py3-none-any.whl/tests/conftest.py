import hashlib
import json
import os
import sys
import time
from uuid import UUID

import pytest
import yaml
from peewee import SqliteDatabase

from arkindex.mock import MockApiClient
from arkindex_worker.cache import (
    MODELS,
    SQL_VERSION,
    CachedElement,
    CachedImage,
    CachedTranscription,
    Version,
    create_tables,
    create_version_table,
    init_cache_db,
)
from arkindex_worker.models import Artifact, Dataset, Set
from arkindex_worker.worker import (
    BaseWorker,
    DatasetWorker,
    ElementsWorker,
    ProcessMode,
)
from arkindex_worker.worker.dataset import DatasetState
from arkindex_worker.worker.transcription import TextOrientation
from tests import CORPUS_ID, SAMPLES_DIR

__yaml_cache = {}


@pytest.fixture(autouse=True)
def _disable_sleep(monkeypatch):
    """
    Do not sleep at all in between API executions
    when errors occur in unit tests.
    This speeds up the test execution a lot
    """
    monkeypatch.setattr(time, "sleep", lambda x: None)


@pytest.fixture
def _cache_yaml(monkeypatch):
    """
    Cache all calls to yaml.safe_load in order to speedup
    every test cases that load the OpenAPI schema
    """
    # Keep a reference towards the original function
    _original_yaml_load = yaml.safe_load

    def _cached_yaml_load(yaml_payload):
        # Create a unique cache key for direct YAML strings
        # and file descriptors
        if isinstance(yaml_payload, str):
            yaml_payload = yaml_payload.encode("utf-8")
        if isinstance(yaml_payload, bytes):
            key = hashlib.md5(yaml_payload).hexdigest()
        else:
            key = yaml_payload.name

        # Cache result
        if key not in __yaml_cache:
            __yaml_cache[key] = _original_yaml_load(yaml_payload)

        return __yaml_cache[key]

    monkeypatch.setattr(yaml, "safe_load", _cached_yaml_load)


@pytest.fixture(autouse=True)
def _setup_api(responses, monkeypatch, _cache_yaml):
    # Always use the environment variable first
    schema_url = os.environ.get("ARKINDEX_API_SCHEMA_URL")

    # Fallback to prod environment
    if schema_url is None:
        schema_url = "https://arkindex.teklia.com/api/v1/openapi/?format=json"
        monkeypatch.setenv("ARKINDEX_API_SCHEMA_URL", schema_url)

    # Allow accessing remote API schemas
    responses.add_passthru(schema_url)

    # Force api requests on a dummy server with dummy credentials
    monkeypatch.setenv("ARKINDEX_API_URL", "http://testserver/api/v1")
    monkeypatch.setenv("ARKINDEX_API_TOKEN", "unittest1234")


@pytest.fixture(autouse=True)
def _give_env_variable(monkeypatch):
    """Defines required environment variables"""
    monkeypatch.setenv("ARKINDEX_WORKER_RUN_ID", "56785678-5678-5678-5678-567856785678")


@pytest.fixture
def _mock_worker_run_api(responses):
    """Provide a mock API response to get worker run information"""
    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker": {
            "id": "deadbeef-1234-5678-1234-worker",
            "name": "Fake worker",
            "slug": "fake_worker",
            "type": "classifier",
        },
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "configuration": {
                "docker": {"image": "python:3"},
                "configuration": {"someKey": "someValue"},
                "secrets": [],
            },
            "revision": {
                "hash": "deadbeef1234",
                "name": "some git revision",
            },
            "version": None,
            "docker_image": None,
            "docker_image_iid": "python:3",
            "docker_image_name": None,
            "state": "created",
            "gpu_usage": "disabled",
            "model_usage": "disabled",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
        },
        "configuration": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "name": "string",
            "configuration": {},
            "archived": False,
        },
        "model_version": None,
        "process": {
            "name": None,
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "state": "running",
            "mode": "workers",
            "corpus": CORPUS_ID,
            "use_cache": False,
            "activity_state": "ready",
            "model_id": None,
            "train_folder_id": None,
            "validation_folder_id": None,
            "test_folder_id": None,
        },
        "summary": "Worker Fake worker @ 123412",
    }

    responses.add(
        responses.GET,
        "http://testserver/api/v1/process/workers/56785678-5678-5678-5678-567856785678/",
        status=200,
        body=json.dumps(payload),
        content_type="application/json",
    )


@pytest.fixture
def _mock_worker_run_no_revision_api(responses):
    """Provide a mock API response to get worker run not linked to a revision information"""
    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker": {
            "id": "deadbeef-1234-5678-1234-worker",
            "name": "Fake worker",
            "slug": "fake_worker",
            "type": "classifier",
        },
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "configuration": {
                "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
                "docker": {"image": "python:3"},
                "configuration": {"someKey": "someValue"},
                "secrets": [],
            },
            "revision": None,
            "version": 1,
            "docker_image": None,
            "docker_image_iid": "python:3",
            "docker_image_name": None,
            "state": "created",
            "gpu_usage": "disabled",
            "model_usage": "disabled",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
        },
        "configuration": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "name": "string",
            "configuration": {},
            "archived": False,
        },
        "model_version": None,
        "process": {
            "name": None,
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "state": "running",
            "mode": "workers",
            "corpus": CORPUS_ID,
            "use_cache": False,
            "activity_state": "ready",
            "model_id": None,
            "train_folder_id": None,
            "validation_folder_id": None,
            "test_folder_id": None,
        },
        "summary": "Worker Fake worker @ 1",
    }

    responses.add(
        responses.GET,
        "http://testserver/api/v1/process/workers/56785678-5678-5678-5678-567856785678/",
        status=200,
        body=json.dumps(payload),
        content_type="application/json",
    )


@pytest.fixture
def _mock_activity_calls(responses):
    """
    Mock responses when updating the activity state for multiple element of the same version
    """
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        status=200,
    )


@pytest.fixture
def mock_elements_worker(monkeypatch, _mock_worker_run_api):
    """Build and configure an ElementsWorker with fixed CLI parameters to avoid issues with pytest"""
    monkeypatch.setattr(sys, "argv", ["worker"])
    worker = ElementsWorker()
    worker.configure()
    return worker


@pytest.fixture
def mock_elements_worker_read_only(monkeypatch):
    """Build and configure an ElementsWorker with fixed CLI parameters to avoid issues with pytest"""
    monkeypatch.setattr(sys, "argv", ["worker", "--dev"])
    worker = ElementsWorker()
    worker.configure()
    return worker


@pytest.fixture
def mock_elements_worker_with_list(monkeypatch, responses, mock_elements_worker):
    """
    Mock a worker instance to list and retrieve a single element
    """
    monkeypatch.setattr(mock_elements_worker, "get_elements", lambda: ["1234-deadbeef"])
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/1234-deadbeef/",
        status=200,
        json={
            "id": "1234-deadbeef",
            "type": "page",
            "name": "Test Page n°1",
        },
    )
    return mock_elements_worker


@pytest.fixture
def mock_cache_db(tmp_path):
    cache_path = tmp_path / "db.sqlite"

    init_cache_db(cache_path)
    create_version_table()
    create_tables()

    return cache_path


@pytest.fixture
def mock_base_worker_with_cache(monkeypatch, _mock_worker_run_api):
    """Build a BaseWorker using SQLite cache, also mocking a PONOS_TASK"""
    monkeypatch.setattr(sys, "argv", ["worker"])

    monkeypatch.setenv("PONOS_TASK", "my_task")
    worker = BaseWorker(support_cache=True)
    worker.setup_api_client()
    return worker


@pytest.fixture
def mock_elements_worker_with_cache(monkeypatch, mock_cache_db, _mock_worker_run_api):
    """Build and configure an ElementsWorker using SQLite cache with fixed CLI parameters to avoid issues with pytest"""
    monkeypatch.setattr(sys, "argv", ["worker", "-d", str(mock_cache_db)])

    worker = ElementsWorker(support_cache=True)
    worker.configure()
    worker.configure_cache()
    return worker


@pytest.fixture
def model_file_dir():
    return SAMPLES_DIR / "model_files"


@pytest.fixture
def model_file_dir_with_subfolder():
    return SAMPLES_DIR / "root_folder"


@pytest.fixture
def fake_dummy_worker():
    api_client = MockApiClient()
    worker = ElementsWorker()
    worker.api_client = api_client
    return worker


@pytest.fixture
def _mock_cached_elements(mock_cache_db):
    """Insert few elements in local cache"""
    CachedElement.create(
        id=UUID("99999999-9999-9999-9999-999999999999"),
        parent_id=None,
        type="something",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=None,
        worker_run_id=None,
    )
    CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        parent_id=UUID("99999999-9999-9999-9999-999999999999"),
        type="double_page",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        parent_id=UUID("12341234-1234-1234-1234-123412341234"),
        type="something",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        parent_id=UUID("12341234-1234-1234-1234-123412341234"),
        type="page",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        parent_id=UUID("12341234-1234-1234-1234-123412341234"),
        type="paragraph",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=None,
        worker_run_id=None,
    )
    assert CachedElement.select().count() == 5


@pytest.fixture
def _mock_cached_images(mock_cache_db):
    """Insert few elements in local cache"""
    CachedImage.create(
        id=UUID("99999999-9999-9999-9999-999999999999"),
        width=1250,
        height=2500,
        url="http://testserver/iiif/3/image",
    )
    assert CachedImage.select().count() == 1


@pytest.fixture
def _mock_cached_transcriptions(mock_cache_db):
    """Insert few transcriptions in local cache, on a shared element"""
    CachedElement.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        type="page",
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        type="something_else",
        parent_id=UUID("11111111-1111-1111-1111-111111111111"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        type="page",
        parent_id=UUID("11111111-1111-1111-1111-111111111111"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        type="something_else",
        parent_id=UUID("22222222-2222-2222-2222-222222222222"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedElement.create(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        type="something_else",
        parent_id=UUID("44444444-4444-4444-4444-444444444444"),
        polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedTranscription.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        element_id=UUID("11111111-1111-1111-1111-111111111111"),
        text="This",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )
    CachedTranscription.create(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        element_id=UUID("22222222-2222-2222-2222-222222222222"),
        text="is",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        element_id=UUID("33333333-3333-3333-3333-333333333333"),
        text="a",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        element_id=UUID("44444444-4444-4444-4444-444444444444"),
        text="good",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        element_id=UUID("55555555-5555-5555-5555-555555555555"),
        text="test",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=UUID("90129012-9012-9012-9012-901290129012"),
    )
    CachedTranscription.create(
        id=UUID("66666666-6666-6666-6666-666666666666"),
        element_id=UUID("11111111-1111-1111-1111-111111111111"),
        text="This is a manual one",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_version_id=None,
        worker_run_id=None,
    )


@pytest.fixture
def mock_databases(tmp_path):
    """
    Initialize several temporary databases
    to help testing the merge algorithm
    """
    out = {}
    for name in ("target", "first", "second", "conflict", "chunk_42"):
        # Build a local database in sub directory
        # for each name required
        filename = "db_42.sqlite" if name == "chunk_42" else "db.sqlite"
        path = tmp_path / name / filename
        (tmp_path / name).mkdir()
        local_db = SqliteDatabase(path)
        with local_db.bind_ctx(MODELS + [Version]):
            # Create tables on the current local database
            # by binding temporarily the models on that database
            local_db.create_tables([Version])
            Version.create(version=SQL_VERSION)
            local_db.create_tables(MODELS)
        out[name] = {"path": path, "db": local_db}

    # Add an element in first parent database
    with out["first"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("12341234-1234-1234-1234-123412341234"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
        CachedElement.create(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )

    # Add another element with a transcription in second parent database
    with out["second"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("42424242-4242-4242-4242-424242424242"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
        CachedTranscription.create(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            element_id=UUID("42424242-4242-4242-4242-424242424242"),
            text="Hello!",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )

    # Add a conflicting element
    with out["conflict"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("42424242-4242-4242-4242-424242424242"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            initial=True,
        )
        CachedTranscription.create(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            element_id=UUID("42424242-4242-4242-4242-424242424242"),
            text="Hello again neighbor !",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=UUID("56785678-5678-5678-5678-567856785678"),
        )

    # Add an element in chunk parent database
    with out["chunk_42"]["db"].bind_ctx(MODELS):
        CachedElement.create(
            id=UUID("42424242-4242-4242-4242-424242424242"),
            type="page",
            polygon="[[1, 1], [2, 2], [2, 1], [1, 2]]",
            initial=True,
        )

    return out


@pytest.fixture
def default_dataset():
    return Dataset(
        {
            "id": "dataset_id",
            "name": "My dataset",
            "description": "A super dataset built by me",
            "sets": ["set_1", "set_2", "set_3", "set_4"],
            "state": DatasetState.Open.value,
            "corpus_id": "corpus_id",
            "creator": "creator@teklia.com",
            "task_id": "11111111-1111-1111-1111-111111111111",
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        }
    )


@pytest.fixture
def default_train_set(default_dataset):
    return Set(name="train", dataset=default_dataset)


@pytest.fixture
def mock_dataset_worker(monkeypatch, mocker, _mock_worker_run_api):
    monkeypatch.setenv("PONOS_TASK", "my_task")
    mocker.patch.object(sys, "argv", ["worker"])

    dataset_worker = DatasetWorker()
    dataset_worker.configure()

    # Update process mode
    dataset_worker.process_information["mode"] = ProcessMode.Dataset

    assert not dataset_worker.is_read_only

    return dataset_worker


@pytest.fixture
def mock_dev_dataset_worker(mocker):
    mocker.patch.object(
        sys,
        "argv",
        [
            "worker",
            "--dev",
            "--set",
            "11111111-1111-1111-1111-111111111111:train",
            "11111111-1111-1111-1111-111111111111:val",
            "22222222-2222-2222-2222-222222222222:my_set",
        ],
    )

    dataset_worker = DatasetWorker()
    dataset_worker.configure()

    assert dataset_worker.args.dev is True
    assert dataset_worker.process_information is None
    assert dataset_worker.is_read_only is True

    return dataset_worker


@pytest.fixture
def default_artifact():
    return Artifact(
        **{
            "id": "artifact_id",
            "path": "dataset_id.tar.zst",
            "size": 42,
            "content_type": "application/zstd",
            "s3_put_url": None,
            "created": "2000-01-01T00:00:00Z",
            "updated": "2000-01-01T00:00:00Z",
        }
    )
