import json
import logging
import sys
import uuid
from pathlib import Path

import gnupg
import pytest

from arkindex.mock import MockApiClient
from arkindex_worker import logger
from arkindex_worker.worker import BaseWorker, ElementsWorker
from arkindex_worker.worker.base import ExtrasDirNotFoundError
from tests import CORPUS_ID, FIXTURES_DIR


def test_init_default_local_share():
    worker = BaseWorker()

    assert worker.work_dir == Path("~/.local/share/arkindex").expanduser()


def test_init_default_xdg_data_home(monkeypatch):
    path = str(Path(__file__).absolute().parent)
    monkeypatch.setenv("XDG_DATA_HOME", path)
    worker = BaseWorker()

    assert str(worker.work_dir) == f"{path}/arkindex"


def test_init_with_local_cache():
    worker = BaseWorker(support_cache=True)

    assert worker.work_dir == Path("~/.local/share/arkindex").expanduser()
    assert worker.support_cache is True


def test_init_var_ponos_data_given(monkeypatch):
    path = str(Path(__file__).absolute().parent)
    monkeypatch.setenv("PONOS_DATA", path)
    worker = BaseWorker()

    assert str(worker.work_dir) == f"{path}/current"


def test_init_var_worker_run_id_missing(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["worker"])
    monkeypatch.delenv("ARKINDEX_WORKER_RUN_ID")
    worker = BaseWorker()
    worker.args = worker.parser.parse_args()
    worker.configure_for_developers()
    assert worker.worker_run_id is None
    assert worker.is_read_only is True
    assert worker.config == {}  # default empty case


def test_init_var_worker_local_file(monkeypatch, tmp_path):
    # Build a dummy yaml config file
    config = tmp_path / "config.yml"
    config.write_text("---\nlocalKey: abcdef123")

    monkeypatch.setattr(sys, "argv", ["worker", "-c", str(config)])
    monkeypatch.delenv("ARKINDEX_WORKER_RUN_ID")
    worker = BaseWorker()
    worker.args = worker.parser.parse_args()
    worker.configure_for_developers()
    assert worker.worker_run_id is None
    assert worker.is_read_only is True
    assert worker.config == {"localKey": "abcdef123"}  # Use a local file for devs

    config.unlink()


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_default(mocker):
    worker = BaseWorker()
    assert logger.level == logging.NOTSET

    mocker.patch.object(sys, "argv", ["worker"])
    worker.args = worker.parser.parse_args()
    assert worker.is_read_only is False
    assert worker.worker_run_id == "56785678-5678-5678-5678-567856785678"

    worker.configure()
    assert not worker.args.verbose
    assert logger.level == logging.NOTSET
    assert worker.api_client
    assert worker.config == {"someKey": "someValue"}  # from API

    logger.setLevel(logging.NOTSET)


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_arg_verbose_given(mocker):
    worker = BaseWorker()
    assert logger.level == logging.NOTSET

    mocker.patch.object(sys, "argv", ["worker", "-v"])
    worker.args = worker.parser.parse_args()
    assert worker.is_read_only is False
    assert worker.worker_run_id == "56785678-5678-5678-5678-567856785678"

    worker.configure()
    assert worker.args.verbose
    assert logger.level == logging.DEBUG
    assert worker.api_client
    assert worker.config == {"someKey": "someValue"}  # from API

    logger.setLevel(logging.NOTSET)


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_envvar_debug_given(mocker, monkeypatch):
    worker = BaseWorker()

    assert logger.level == logging.NOTSET
    mocker.patch.object(sys, "argv", ["worker"])
    monkeypatch.setenv("ARKINDEX_DEBUG", "True")
    worker.args = worker.parser.parse_args()
    assert worker.is_read_only is False
    assert worker.worker_run_id == "56785678-5678-5678-5678-567856785678"

    worker.configure()
    assert logger.level == logging.DEBUG
    assert worker.api_client
    assert worker.config == {"someKey": "someValue"}  # from API

    logger.setLevel(logging.NOTSET)


def test_configure_dev_mode(mocker):
    """
    Configuring a worker in developer mode avoid retrieving process information
    """
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker", "--dev"])
    worker.args = worker.parser.parse_args()
    worker.configure_for_developers()

    assert worker.args.dev is True
    assert worker.process_information is None
    assert worker.is_read_only is True
    assert worker.user_configuration == {}


def test_configure_worker_run(mocker, responses, caplog):
    # Capture log messages
    caplog.set_level(logging.INFO)

    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])
    user_configuration = {
        "id": "bbbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "name": "BBB",
        "configuration": {"a": "b"},
    }
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
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
            "revision": {"hash": "deadbeef1234"},
            "configuration": {"configuration": {}},
        },
        "configuration": user_configuration,
        "model_version": None,
        "process": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "corpus": CORPUS_ID,
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
    worker.args = worker.parser.parse_args()
    assert worker.is_read_only is False
    assert worker.worker_run_id == "56785678-5678-5678-5678-567856785678"

    # Capture log messages
    caplog.clear()
    with caplog.at_level(logging.INFO):
        worker.configure()

    assert caplog.record_tuples == [
        (
            "arkindex_worker",
            logging.INFO,
            "Loaded Worker Fake worker @ 123412 from API",
        ),
        ("arkindex_worker", logging.INFO, "Loaded user configuration from WorkerRun"),
        ("arkindex_worker", logging.INFO, "User configuration retrieved"),
    ]

    assert worker.user_configuration == {"a": "b"}


@pytest.mark.usefixtures("_mock_worker_run_no_revision_api")
def test_configure_worker_run_no_revision(mocker, caplog):
    worker = BaseWorker()

    mocker.patch.object(sys, "argv", ["worker"])
    worker.args = worker.parser.parse_args()
    assert worker.is_read_only is False
    assert worker.worker_run_id == "56785678-5678-5678-5678-567856785678"

    # Capture log messages
    caplog.clear()
    with caplog.at_level(logging.INFO):
        worker.configure()

    assert caplog.record_tuples == [
        ("arkindex_worker", logging.INFO, "Loaded Worker Fake worker @ 1 from API")
    ]


def test_configure_user_configuration_defaults(mocker, responses):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv")
    worker.args = worker.parser.parse_args()

    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
            "revision": {"hash": "deadbeef1234"},
            "configuration": {
                "configuration": {"param_1": "/some/path/file.pth", "param_2": 12},
                "user_configuration": {
                    "integer_parameter": {
                        "type": "int",
                        "title": "Lambda",
                        "default": 0,
                        "required": False,
                    }
                },
            },
        },
        "configuration": {
            "id": "af0daaf4-983e-4703-a7ed-a10f146d6684",
            "name": "my-userconfig",
            "configuration": {
                "param_3": "Animula vagula blandula",
                "param_5": True,
            },
        },
        "model_version": None,
        "process": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "corpus": CORPUS_ID,
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

    worker.configure()

    assert worker.user_configuration == {
        "integer_parameter": 0,
        "param_3": "Animula vagula blandula",
        "param_5": True,
    }
    # All configurations are merged
    assert worker.config == {
        # Default config
        "param_1": "/some/path/file.pth",
        "param_2": 12,
        # User config
        "integer_parameter": 0,
        "param_3": "Animula vagula blandula",
        "param_5": True,
    }


@pytest.mark.parametrize("debug", [True, False])
def test_configure_user_config_debug(mocker, responses, debug):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])
    assert logger.level == logging.NOTSET
    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
            "revision": {"hash": "deadbeef1234"},
            "configuration": {"configuration": {}},
        },
        "model_version": None,
        "configuration": {
            "id": "af0daaf4-983e-4703-a7ed-a10f146d6684",
            "name": "BBB",
            "configuration": {"debug": debug},
        },
        "process": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "corpus": CORPUS_ID,
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
    worker.args = worker.parser.parse_args()
    worker.configure()

    assert worker.user_configuration == {"debug": debug}
    expected_log_level = logging.DEBUG if debug else logging.NOTSET
    assert logger.level == expected_log_level
    logger.setLevel(logging.NOTSET)


def test_configure_worker_run_missing_conf(mocker, responses):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])

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
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
            "revision": {"hash": "deadbeef1234"},
            "configuration": {"configuration": {}},
        },
        "model_version": None,
        "configuration": {"id": "bbbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "name": "BBB"},
        "process": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "corpus": CORPUS_ID,
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
    worker.args = worker.parser.parse_args()
    worker.configure()

    assert worker.user_configuration == {}


def test_configure_worker_run_no_worker_run_conf(mocker, responses):
    """
    No configuration is provided but should not crash
    """
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])

    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
            "revision": {"hash": "deadbeef1234"},
            "configuration": {},
        },
        "model_version": None,
        "configuration": None,
        "process": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "corpus": CORPUS_ID,
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
    worker.args = worker.parser.parse_args()
    worker.configure()

    assert worker.user_configuration == {}


def test_configure_load_model_configuration(mocker, responses):
    worker = BaseWorker()
    mocker.patch.object(sys, "argv", ["worker"])
    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
            "revision": {"hash": "deadbeef1234"},
            "configuration": {"configuration": {}},
        },
        "configuration": None,
        "model_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "model": {
                "id": "43214321-4321-4321-4321-432143214321",
                "name": "Model 1337",
            },
            "configuration": {
                "param1": "value1",
                "param2": 2,
                "param3": None,
            },
        },
        "process": {
            "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "corpus": CORPUS_ID,
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
    worker.args = worker.parser.parse_args()
    assert worker.is_read_only is False
    assert worker.worker_run_id == "56785678-5678-5678-5678-567856785678"
    assert worker.model_configuration == {}

    worker.configure()

    assert worker.model_configuration == {
        "param1": "value1",
        "param2": 2,
        "param3": None,
    }
    assert worker.model_version_id == "12341234-1234-1234-1234-123412341234"
    assert worker.model_details == {
        "id": "43214321-4321-4321-4321-432143214321",
        "name": "Model 1337",
    }


def test_load_missing_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()

    with pytest.raises(
        Exception, match="Secret missing/secret is not available on the API nor locally"
    ):
        worker.load_secret(Path("missing/secret"))


def test_load_remote_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()
    worker.api_client.add_response(
        "RetrieveSecret",
        name="testRemote",
        response={"content": "this is a secret value !"},
    )

    assert worker.load_secret(Path("testRemote")) == "this is a secret value !"

    # The one mocked call has been used
    assert len(worker.api_client.history) == 1
    assert len(worker.api_client.responses) == 0


def test_load_json_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()
    worker.api_client.add_response(
        "RetrieveSecret",
        name="path/to/file.json",
        response={"content": '{"key": "value", "number": 42}'},
    )

    assert worker.load_secret(Path("path/to/file.json")) == {
        "key": "value",
        "number": 42,
    }

    # The one mocked call has been used
    assert len(worker.api_client.history) == 1
    assert len(worker.api_client.responses) == 0


def test_load_yaml_secret():
    worker = BaseWorker()
    worker.api_client = MockApiClient()
    worker.api_client.add_response(
        "RetrieveSecret",
        name="path/to/file.yaml",
        response={
            "content": """---
somekey: value
aList:
  - A
  - B
  - C
struct:
 level:
   X
"""
        },
    )

    assert worker.load_secret(Path("path/to/file.yaml")) == {
        "aList": ["A", "B", "C"],
        "somekey": "value",
        "struct": {"level": "X"},
    }

    # The one mocked call has been used
    assert len(worker.api_client.history) == 1
    assert len(worker.api_client.responses) == 0


def test_load_local_secret(monkeypatch, tmp_path):
    # Setup arkindex config dir in a temp directory
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    # Write a dummy secret
    secrets_dir = tmp_path / "arkindex" / "secrets"
    secrets_dir.mkdir(parents=True)
    secret = secrets_dir / "testLocal"
    secret.write_text("this is a local secret value", encoding="utf-8")

    # Mock GPG decryption
    class GpgDecrypt:
        def __init__(self, fd):
            self.ok = True
            self.data = fd.read()

    monkeypatch.setattr(gnupg.GPG, "decrypt_file", lambda gpg, f: GpgDecrypt(f))

    worker = BaseWorker()
    worker.api_client = MockApiClient()

    assert worker.load_secret(Path("testLocal")) == "this is a local secret value"

    # The remote api is checked first
    assert len(worker.api_client.history) == 1
    assert worker.api_client.history[0].operation == "RetrieveSecret"


def test_find_extras_directory_ponos_no_extra_files(monkeypatch):
    monkeypatch.setenv("PONOS_TASK", "my_task")
    monkeypatch.setenv("PONOS_DATA", "/data")
    worker = BaseWorker()
    assert worker.find_extras_directory() == Path("/data/current")


def test_find_extras_directory_ponos_with_extra_files(monkeypatch):
    monkeypatch.setenv("PONOS_TASK", "my_task")
    monkeypatch.setenv("PONOS_DATA", "/data")
    # Make the `extra_files` folder exist
    monkeypatch.setattr("pathlib.Path.exists", lambda x: True)

    worker = BaseWorker()
    assert worker.find_extras_directory() == Path("/data/extra_files")


def test_find_extras_directory_from_cli(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["worker", "--extras-dir", "extra_files"])
    monkeypatch.setattr("pathlib.Path.exists", lambda x: True)
    worker = BaseWorker()
    worker.args = worker.parser.parse_args()
    worker.config = {}
    assert worker.find_extras_directory() == Path("extra_files")


def test_find_extras_directory_from_config(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["worker"])
    monkeypatch.setattr("pathlib.Path.exists", lambda x: True)
    worker = BaseWorker()
    worker.args = worker.parser.parse_args()
    worker.config = {"extras_dir": "extra_files"}
    assert worker.find_extras_directory() == Path("extra_files")


@pytest.mark.parametrize(
    ("extras_path", "exists", "error"),
    [
        (
            None,
            True,
            "No path to the directory for extra files was provided. Please provide extras_dir either through configuration or as CLI argument.",
        ),
        ("extra_files", False, "The path extra_files does not link to any directory"),
    ],
)
def test_find_extras_directory_not_found(monkeypatch, extras_path, exists, error):
    if extras_path:
        monkeypatch.setattr(sys, "argv", ["worker", "--extras-dir", extras_path])
    else:
        monkeypatch.setattr(sys, "argv", ["worker"])

    monkeypatch.setattr("pathlib.Path.exists", lambda x: exists)

    worker = BaseWorker()
    worker.args = worker.parser.parse_args()
    worker.config = {"extras_dir": extras_path}

    with pytest.raises(ExtrasDirNotFoundError, match=error):
        worker.find_extras_directory()


def test_find_parents_file_paths(responses, mock_base_worker_with_cache, tmp_path):
    responses.add(
        responses.GET,
        "http://testserver/api/v1/task/my_task/",
        status=200,
        json={"parents": ["first", "second", "third"]},
    )

    filename = Path("my_file.txt")
    for parent_id, content in zip(
        ["first", "third"], ["Some text", "Other text"], strict=True
    ):
        (tmp_path / parent_id).mkdir()
        file_path = tmp_path / parent_id / filename
        file_path.write_text(content)

    # Configure worker with a specific data directory
    mock_base_worker_with_cache.task_data_dir = tmp_path
    mock_base_worker_with_cache.args = mock_base_worker_with_cache.parser.parse_args()

    mock_base_worker_with_cache.configure()

    assert mock_base_worker_with_cache.find_parents_file_paths(filename) == [
        tmp_path / "first" / filename,
        tmp_path / "third" / filename,
    ]


def test_extract_parent_archives(tmp_path):
    worker = BaseWorker()

    # Mock task attributes
    worker.task_parents = [
        "invalid_id",
        "first_parent",
        str(uuid.uuid4()),
        "second_parent",
    ]
    worker.task_data_dir = FIXTURES_DIR / "extract_parent_archives"

    worker.extract_parent_archives("arkindex_data.tar.zst", tmp_path)

    extracted_files = [
        # Test
        tmp_path / "test/images/f2649ce7-333e-44d2-ae73-387f18aad1f6.png",
        tmp_path / "test/labels/f2649ce7-333e-44d2-ae73-387f18aad1f6.png",
        tmp_path / "test/labels_json/f2649ce7-333e-44d2-ae73-387f18aad1f6.json",
        # Train
        tmp_path / "train/images/98115546-df07-448c-a2f0-34aa24789b77.png",
        tmp_path / "train/images/ebeaa451-9287-4df7-9c40-07eb25cadb78.png",
        tmp_path / "train/labels/98115546-df07-448c-a2f0-34aa24789b77.png",
        tmp_path / "train/labels/ebeaa451-9287-4df7-9c40-07eb25cadb78.png",
        tmp_path / "train/labels_json/98115546-df07-448c-a2f0-34aa24789b77.json",
        tmp_path / "train/labels_json/ebeaa451-9287-4df7-9c40-07eb25cadb78.json",
        # Val
        tmp_path / "val/images/2987176d-4338-40f2-90d9-6d2cb4fd4a00.png",
        tmp_path / "val/images/e3f91312-9201-45b7-9c32-e04a97ff1334.png",
        tmp_path / "val/labels/2987176d-4338-40f2-90d9-6d2cb4fd4a00.png",
        tmp_path / "val/labels/e3f91312-9201-45b7-9c32-e04a97ff1334.png",
        tmp_path / "val/labels_json/2987176d-4338-40f2-90d9-6d2cb4fd4a00.json",
        tmp_path / "val/labels_json/e3f91312-9201-45b7-9c32-e04a97ff1334.json",
    ]
    assert (
        sorted([path for path in tmp_path.rglob("*") if path.is_file()])
        == extracted_files
    )

    for extracted_file in extracted_files:
        expected_file = (
            FIXTURES_DIR
            / "extract_parent_archives"
            / str(extracted_file).replace(str(tmp_path), "expected")
        )
        mode = "rb" if extracted_file.suffix == ".png" else "r"
        assert extracted_file.open(mode).read() == expected_file.open(mode).read()


def test_corpus_id_not_set_read_only_mode(
    mock_elements_worker_read_only: ElementsWorker,
):
    mock_elements_worker_read_only.configure()

    with pytest.raises(
        Exception, match="Missing ARKINDEX_CORPUS_ID environment variable"
    ):
        _ = mock_elements_worker_read_only.corpus_id


def test_corpus_id_set_read_only_mode(
    monkeypatch, mock_elements_worker_read_only: ElementsWorker
):
    corpus_id = str(uuid.uuid4())
    monkeypatch.setenv("ARKINDEX_CORPUS_ID", corpus_id)

    mock_elements_worker_read_only.configure()

    assert mock_elements_worker_read_only.corpus_id == corpus_id


@pytest.mark.parametrize(
    (
        "wk_version_config",
        "wk_version_user_config",
        "frontend_user_config",
        "model_config",
        "expected_config",
    ),
    [
        ({}, {}, {}, {}, {}),
        # Keep parameters from worker version configuration
        ({"parameter": 0}, {}, {}, {}, {"parameter": 0}),
        # Keep parameters from worker version configuration + user_config defaults
        (
            {"parameter": 0},
            {
                "parameter2": {
                    "type": "int",
                    "title": "Lambda",
                    "default": 0,
                    "required": False,
                }
            },
            {},
            {},
            {"parameter": 0, "parameter2": 0},
        ),
        # Keep parameters from worker version configuration + user_config no defaults
        (
            {"parameter": 0},
            {
                "parameter2": {
                    "type": "int",
                    "title": "Lambda",
                    "required": False,
                }
            },
            {},
            {},
            {"parameter": 0, "parameter2": None},
        ),
        # Keep parameters from worker version configuration but user_config defaults overrides
        (
            {"parameter": 0},
            {
                "parameter": {
                    "type": "int",
                    "title": "Lambda",
                    "default": 1,
                    "required": False,
                }
            },
            {},
            {},
            {"parameter": 1},
        ),
        # Keep parameters from worker version configuration + frontend config
        (
            {"parameter": 0},
            {},
            {"parameter2": 0},
            {},
            {"parameter": 0, "parameter2": 0},
        ),
        # Keep parameters from worker version configuration + frontend config overrides
        ({"parameter": 0}, {}, {"parameter": 1}, {}, {"parameter": 1}),
        # Keep parameters from worker version configuration + model config
        (
            {"parameter": 0},
            {},
            {},
            {"parameter2": 0},
            {"parameter": 0, "parameter2": 0},
        ),
        # Keep parameters from worker version configuration + model config overrides
        ({"parameter": 0}, {}, {}, {"parameter": 1}, {"parameter": 1}),
        # Keep parameters from worker version configuration + user_config default + model config overrides
        (
            {"parameter": 0},
            {
                "parameter": {
                    "type": "int",
                    "title": "Lambda",
                    "default": 1,
                    "required": False,
                }
            },
            {},
            {"parameter": 2},
            {"parameter": 2},
        ),
        # Keep parameters from worker version configuration + model config + frontend config overrides
        ({"parameter": 0}, {}, {"parameter": 2}, {"parameter": 1}, {"parameter": 2}),
        # Keep parameters from worker version configuration + user_config default + model config + frontend config overrides all
        (
            {"parameter": 0},
            {
                "parameter": {
                    "type": "int",
                    "title": "Lambda",
                    "default": 1,
                    "required": False,
                }
            },
            {"parameter": 3},
            {"parameter": 2},
            {"parameter": 3},
        ),
    ],
)
def test_worker_config_multiple_source(
    monkeypatch,
    responses,
    wk_version_config,
    wk_version_user_config,
    frontend_user_config,
    model_config,
    expected_config,
):
    # Compute WorkerRun info
    payload = {
        "id": "56785678-5678-5678-5678-567856785678",
        "parents": [],
        "worker_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "configuration": {
                "docker": {"image": "python:3"},
                "configuration": wk_version_config,
                "secrets": [],
                "user_configuration": wk_version_user_config,
            },
            "revision": {
                "hash": "deadbeef1234",
                "name": "some git revision",
            },
            "docker_image": "python:3",
            "docker_image_name": "python:3",
            "state": "created",
            "worker": {
                "id": "deadbeef-1234-5678-1234-worker",
                "name": "Fake worker",
                "slug": "fake_worker",
                "type": "classifier",
            },
        },
        "configuration": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "name": "Configuration entered by user",
            "configuration": frontend_user_config,
        },
        "model_version": {
            "id": "12341234-1234-1234-1234-123412341234",
            "name": "Model version 1337",
            "configuration": model_config,
            "model": {
                "id": "hahahaha-haha-haha-haha-hahahahahaha",
                "name": "My model",
            },
        },
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

    # Create and configure a worker
    monkeypatch.setattr(sys, "argv", ["worker"])
    worker = BaseWorker()
    worker.configure()

    # Check final config
    assert worker.config == expected_config
