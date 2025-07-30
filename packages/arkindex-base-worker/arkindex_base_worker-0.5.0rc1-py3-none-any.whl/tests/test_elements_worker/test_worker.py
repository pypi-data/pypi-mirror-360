import json
import logging
import sys
from argparse import Namespace
from uuid import UUID

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.cache import (
    SQL_VERSION,
    CachedElement,
    create_version_table,
    init_cache_db,
)
from arkindex_worker.models import Element
from arkindex_worker.worker import ActivityState, ElementsWorker
from arkindex_worker.worker.dataset import DatasetState
from arkindex_worker.worker.process import ProcessMode
from tests import PROCESS_ID

from . import BASE_API_CALLS


def test_database_arg(mocker, mock_elements_worker, tmp_path):
    database_path = tmp_path / "my_database.sqlite"
    init_cache_db(database_path)
    create_version_table()

    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=database_path,
            dev=False,
            set=[],
        ),
    )

    worker = ElementsWorker(support_cache=True)
    worker.configure()

    assert worker.use_cache is True
    assert worker.cache_path == database_path


def test_database_arg_cache_missing_version_table(
    mocker, mock_elements_worker, tmp_path
):
    database_path = tmp_path / "my_database.sqlite"
    database_path.touch()

    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            verbose=False,
            elements_list=None,
            database=database_path,
            dev=False,
            set=[],
        ),
    )

    worker = ElementsWorker(support_cache=True)
    with pytest.raises(
        AssertionError,
        match=f"The SQLite database {database_path} does not have the correct cache version, it should be {SQL_VERSION}",
    ):
        worker.configure()


def test_readonly(responses, mock_elements_worker):
    """Test readonly worker does not trigger any API calls"""

    # Setup the worker as read-only
    mock_elements_worker.worker_run_id = None
    assert mock_elements_worker.is_read_only is True

    out = mock_elements_worker.update_activity("1234-deadbeef", ActivityState.Processed)

    # update_activity returns False in very specific cases
    assert out is True
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_get_elements_elements_list_arg_wrong_type(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("{}")

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError, match="Elements list must be a list"):
        worker.get_elements()


def test_get_elements_elements_list_arg_empty_list(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text("[]")

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(AssertionError, match="No elements in elements list"):
        worker.get_elements()


def test_get_elements_elements_list_arg_missing_id(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text(json.dumps([{"type": "volume"}]))

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.get_elements()

    assert elt_list == []


def test_get_elements_elements_list_arg_not_uuid(
    monkeypatch, tmp_path, mock_elements_worker
):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text(
        json.dumps(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ]
        )
    )

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(
        Exception,
        match="These element IDs are invalid: volumeid, pageid, actid, surfaceid",
    ):
        worker.get_elements()


def test_get_elements_elements_list_arg(monkeypatch, tmp_path, mock_elements_worker):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text(
        json.dumps(
            [
                {"id": "11111111-1111-1111-1111-111111111111", "type": "volume"},
                {"id": "22222222-2222-2222-2222-222222222222", "type": "page"},
                {"id": "33333333-3333-3333-3333-333333333333", "type": "act"},
            ]
        )
    )

    monkeypatch.setenv("TASK_ELEMENTS", str(elements_path))
    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.get_elements()

    assert elt_list == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
    ]


def test_get_elements_element_arg_not_uuid(mocker, mock_elements_worker):
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["volumeid", "pageid"],
            config={},
            verbose=False,
            elements_list=None,
            database=None,
            dev=True,
            set=[],
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(
        Exception, match="These element IDs are invalid: volumeid, pageid"
    ):
        worker.get_elements()


def test_get_elements_element_arg(mocker, mock_elements_worker):
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=[
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
            config={},
            verbose=False,
            elements_list=None,
            database=None,
            dev=True,
            set=[],
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.get_elements()

    assert elt_list == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]


def test_get_elements_dataset_set_arg(responses, mocker, mock_elements_worker):
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=[],
            config={},
            verbose=False,
            elements_list=None,
            database=None,
            dev=True,
            set=[(UUID("11111111-1111-1111-1111-111111111111"), "train")],
        ),
    )

    # Mock RetrieveDataset call
    responses.add(
        responses.GET,
        "http://testserver/api/v1/datasets/11111111-1111-1111-1111-111111111111/",
        status=200,
        json={
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "My dataset",
            "description": "A dataset about cats.",
            "sets": ["train", "dev", "test"],
            "state": DatasetState.Complete.value,
        },
        content_type="application/json",
    )

    # Mock ListSetElements call
    element = {
        "id": "22222222-2222-2222-2222-222222222222",
        "type": "page",
        "name": "1",
        "corpus": {
            "id": "11111111-1111-1111-1111-111111111111",
        },
        "thumbnail_url": "http://example.com",
        "zone": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "polygon": [[0, 0], [0, 0], [0, 0]],
            "image": {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "path": "string",
                "width": 0,
                "height": 0,
                "url": "http://example.com",
                "s3_url": "string",
                "status": "checked",
                "server": {
                    "display_name": "string",
                    "url": "http://example.com",
                    "max_width": 2147483647,
                    "max_height": 2147483647,
                },
            },
            "url": "http://example.com",
        },
        "rotation_angle": 0,
        "mirrored": False,
        "created": "2019-08-24T14:15:22Z",
        "classes": [
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "ml_class": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "name": "string",
                },
                "state": "pending",
                "confidence": 0,
                "high_confidence": True,
                "worker_run": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "summary": "string",
                },
            }
        ],
        "metadata": [
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "type": "text",
                "name": "string",
                "value": "string",
                "dates": [{"type": "exact", "year": 0, "month": 1, "day": 1}],
            }
        ],
        "transcriptions": [
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "text": "string",
                "confidence": 0,
                "orientation": "horizontal-lr",
                "worker_run": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "summary": "string",
                },
            }
        ],
        "has_children": True,
        "worker_run": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "summary": "string",
        },
        "confidence": 1,
    }
    responses.add(
        responses.GET,
        "http://testserver/api/v1/datasets/11111111-1111-1111-1111-111111111111/elements/?set=train&with_count=true",
        status=200,
        json={
            "next": None,
            "previous": None,
            "results": [
                {
                    "set": "train",
                    "element": element,
                }
            ],
            "count": 1,
        },
        content_type="application/json",
    )

    worker = ElementsWorker()
    worker.configure()

    elt_list = worker.get_elements()

    assert elt_list == [
        Element(**element),
    ]


def test_get_elements_dataset_set_api(responses, mocker, mock_elements_worker):
    # Mock ListProcessSets call
    responses.add(
        responses.GET,
        "http://testserver/api/v1/process/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff/sets/",
        status=200,
        json={
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "dataset": {"id": "11111111-1111-1111-1111-111111111111"},
                    "set_name": "train",
                }
            ],
            "count": 1,
        },
        content_type="application/json",
    )

    # Mock ListSetElements call
    element = {
        "id": "22222222-2222-2222-2222-222222222222",
        "type": "page",
        "name": "1",
        "corpus": {
            "id": "11111111-1111-1111-1111-111111111111",
        },
        "thumbnail_url": "http://example.com",
        "zone": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "polygon": [[0, 0], [0, 0], [0, 0]],
            "image": {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "path": "string",
                "width": 0,
                "height": 0,
                "url": "http://example.com",
                "s3_url": "string",
                "status": "checked",
                "server": {
                    "display_name": "string",
                    "url": "http://example.com",
                    "max_width": 2147483647,
                    "max_height": 2147483647,
                },
            },
            "url": "http://example.com",
        },
        "rotation_angle": 0,
        "mirrored": False,
        "created": "2019-08-24T14:15:22Z",
        "classes": [
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "ml_class": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "name": "string",
                },
                "state": "pending",
                "confidence": 0,
                "high_confidence": True,
                "worker_run": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "summary": "string",
                },
            }
        ],
        "metadata": [
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "type": "text",
                "name": "string",
                "value": "string",
                "dates": [{"type": "exact", "year": 0, "month": 1, "day": 1}],
            }
        ],
        "transcriptions": [
            {
                "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                "text": "string",
                "confidence": 0,
                "orientation": "horizontal-lr",
                "worker_run": {
                    "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
                    "summary": "string",
                },
            }
        ],
        "has_children": True,
        "worker_run": {
            "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "summary": "string",
        },
        "confidence": 1,
    }
    responses.add(
        responses.GET,
        "http://testserver/api/v1/datasets/11111111-1111-1111-1111-111111111111/elements/?set=train&with_count=true",
        status=200,
        json={
            "next": None,
            "previous": None,
            "results": [
                {
                    "set": "train",
                    "element": element,
                }
            ],
            "count": 1,
        },
        content_type="application/json",
    )

    # Update ProcessMode to Dataset
    mock_elements_worker.process_information["mode"] = ProcessMode.Dataset

    elt_list = mock_elements_worker.get_elements()

    assert elt_list == [
        Element(**element),
    ]


def test_get_elements_both_args_error(mocker, mock_elements_worker, tmp_path):
    elements_path = tmp_path / "elements.json"
    elements_path.write_text(
        json.dumps(
            [
                {"id": "volumeid", "type": "volume"},
                {"id": "pageid", "type": "page"},
                {"id": "actid", "type": "act"},
                {"id": "surfaceid", "type": "surface"},
            ]
        )
    )
    mocker.patch(
        "arkindex_worker.worker.base.argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            element=["anotherid", "againanotherid"],
            verbose=False,
            elements_list=elements_path.open(),
            database=None,
            dev=False,
            set=[],
        ),
    )

    worker = ElementsWorker()
    worker.configure()

    with pytest.raises(
        AssertionError, match="elements-list and element CLI args shouldn't be both set"
    ):
        worker.get_elements()


def test_get_elements_export_process(mock_elements_worker, responses):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/process/{PROCESS_ID}/elements/?page_size=500&with_count=true&with_image=False",
        status=200,
        json={
            "count": 2,
            "next": None,
            "results": [
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "type_id": "baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "element 1",
                    "confidence": 1,
                    "image_id": None,
                    "image_width": None,
                    "image_height": None,
                    "image_url": None,
                    "polygon": None,
                    "rotation_angle": 0,
                    "mirrored": False,
                },
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa0",
                    "type_id": "baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "element 2",
                    "confidence": 1,
                    "image_id": None,
                    "image_width": None,
                    "image_height": None,
                    "image_url": None,
                    "polygon": None,
                    "rotation_angle": 0,
                    "mirrored": False,
                },
            ],
        },
    )
    mock_elements_worker.process_information["mode"] = "export"
    assert set(mock_elements_worker.get_elements()) == {
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa0",
    }


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_activities_disabled(responses, monkeypatch):
    """Test worker process elements without updating activities when they are disabled for the process"""
    monkeypatch.setattr(sys, "argv", ["worker"])
    worker = ElementsWorker()
    worker.configure()
    assert not worker.is_read_only

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_activities_dev_mode(mocker):
    """
    Worker activities are not stored in dev mode
    """
    worker = ElementsWorker()
    mocker.patch.object(sys, "argv", ["worker", "--dev"])
    worker.configure()

    assert worker.args.dev is True
    assert worker.process_information is None
    assert worker.is_read_only is True
    assert worker.store_activity is False


@pytest.mark.usefixtures("_mock_activity_calls")
@pytest.mark.parametrize(
    ("process_exception", "final_state"),
    [
        # Successful process_element
        (None, "processed"),
        # Failures in process_element
        (
            ErrorResponse(title="bad gateway", status_code=502, content="Bad gateway"),
            "error",
        ),
        (ValueError("Something bad"), "error"),
        (Exception("Any error"), "error"),
    ],
)
def test_run(
    monkeypatch,
    mock_elements_worker_with_list,
    responses,
    process_exception,
    final_state,
):
    """Check the normal runtime sends 2 API calls to update activity"""
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_list, "configure", lambda: None)
    assert mock_elements_worker_with_list.is_read_only is False
    # Mock exception in process_element
    if process_exception:

        def _err():
            raise process_exception

        monkeypatch.setattr(mock_elements_worker_with_list, "process_element", _err)

        # The worker stops because all elements failed !
        with pytest.raises(SystemExit):
            mock_elements_worker_with_list.run()
    else:
        # Simply run the process
        mock_elements_worker_with_list.run()

    assert len(responses.calls) == len(BASE_API_CALLS) + 3
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", "http://testserver/api/v1/element/1234-deadbeef/"),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        ),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        ),
    ]

    # Check the requests sent by worker
    assert json.loads(responses.calls[-2].request.body) == {
        "element_id": "1234-deadbeef",
        "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": "started",
    }
    assert json.loads(responses.calls[-1].request.body) == {
        "element_id": "1234-deadbeef",
        "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": final_state,
    }


@pytest.mark.usefixtures("_mock_cached_elements", "_mock_activity_calls")
def test_run_cache(monkeypatch, mocker, mock_elements_worker_with_cache):
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_cache, "configure", lambda: None)

    # Make all the cached elements from the fixture initial elements
    CachedElement.update(initial=True).execute()

    mock_elements_worker_with_cache.process_element = mocker.MagicMock()
    mock_elements_worker_with_cache.run()

    assert mock_elements_worker_with_cache.process_element.call_args_list == [
        # Called once for each cached element
        mocker.call(elt)
        for elt in CachedElement.select()
    ]


def test_start_activity_conflict(
    monkeypatch, responses, mock_elements_worker_with_list, caplog
):
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_list, "configure", lambda: None)

    # Mock a "normal" conflict during in activity update, which returns the Exception
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        body=ErrorResponse(
            title="conflict",
            status_code=409,
            content="Either this activity does not exists or this state is not allowed.",
        ),
    )

    mock_elements_worker_with_list.run()

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", "http://testserver/api/v1/element/1234-deadbeef/"),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        ),
    ]
    assert [(record.levelno, record.message) for record in caplog.records] == [
        (logging.INFO, "Processing page Test Page n°1 (1234-deadbeef) (1/1)"),
        (logging.INFO, "Skipping element 1234-deadbeef as it was already processed"),
        (logging.INFO, "Ran on 1 element: 1 completed, 0 failed"),
    ]


def test_start_activity_error(
    monkeypatch, responses, mock_elements_worker_with_list, caplog
):
    # Disable second configure call from run()
    monkeypatch.setattr(mock_elements_worker_with_list, "configure", lambda: None)

    # Mock a random error occurring during the activity update
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        body=Exception("A wild Petilil appears!"),
    )

    with pytest.raises(SystemExit):
        mock_elements_worker_with_list.run()

    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", "http://testserver/api/v1/element/1234-deadbeef/"),
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        ),
        # Activity is updated to the "error" state regardless of the Exception occurring during the call
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        ),
    ]
    assert [(record.levelno, record.message) for record in caplog.records] == [
        (logging.INFO, "Processing page Test Page n°1 (1234-deadbeef) (1/1)"),
        (
            logging.WARNING,
            "Failed running worker on element 1234-deadbeef: Exception('A wild Petilil appears!')",
        ),
        (logging.ERROR, "Ran on 1 element: 0 completed, 1 failed"),
    ]


@pytest.mark.usefixtures("_mock_worker_run_api")
def test_update_activity(responses, mock_elements_worker):
    """Test an update call with feature enabled triggers an API call"""
    responses.add(
        responses.PUT,
        "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        status=200,
        json={
            "element_id": "1234-deadbeef",
            "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
            "state": "processed",
        },
    )

    out = mock_elements_worker.update_activity("1234-deadbeef", ActivityState.Processed)

    # Check the response received by worker
    assert out is True

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PUT",
            "http://testserver/api/v1/workers/versions/56785678-5678-5678-5678-567856785678/activity/",
        ),
    ]

    # Check the request sent by worker
    assert json.loads(responses.calls[-1].request.body) == {
        "element_id": "1234-deadbeef",
        "process_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff",
        "state": "processed",
    }
