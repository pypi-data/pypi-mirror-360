import json
import sys
import tempfile
from pathlib import Path

import pytest

from arkindex_worker.worker import ElementsWorker


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_default(monkeypatch):
    _, path = tempfile.mkstemp()
    path = Path(path)
    path.write_text(
        json.dumps(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
        )
    )

    monkeypatch.setenv("TASK_ELEMENTS", str(path))
    monkeypatch.setattr(sys, "argv", ["worker"])
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.elements_list.name == str(path)
    assert not worker.args.element
    path.unlink()


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_arg_elements_list_given(mocker):
    _, path = tempfile.mkstemp()
    path = Path(path)
    path.write_text(
        json.dumps(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ],
        )
    )

    mocker.patch.object(sys, "argv", ["worker", "--elements-list", str(path)])
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.elements_list.name == str(path)
    assert not worker.args.element
    path.unlink()


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_arg_element_one_given(mocker):
    mocker.patch.object(
        sys, "argv", ["worker", "--element", "12341234-1234-1234-1234-123412341234"]
    )
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.element == ["12341234-1234-1234-1234-123412341234"]
    # elements_list is None because TASK_ELEMENTS environment variable isn't set
    assert not worker.args.elements_list


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_cli_arg_element_many_given(mocker):
    mocker.patch.object(
        sys,
        "argv",
        [
            "worker",
            "--element",
            "12341234-1234-1234-1234-123412341234",
            "43214321-4321-4321-4321-432143214321",
        ],
    )
    worker = ElementsWorker()
    worker.configure()

    assert worker.args.element == [
        "12341234-1234-1234-1234-123412341234",
        "43214321-4321-4321-4321-432143214321",
    ]
    # elements_list is None because TASK_ELEMENTS environment variable isn't set
    assert not worker.args.elements_list
