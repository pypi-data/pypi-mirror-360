import re
import uuid

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.worker.corpus import CorpusExportState
from tests import CORPUS_ID
from tests.test_elements_worker import BASE_API_CALLS


def test_download_export_not_a_uuid(responses, mock_elements_worker):
    with pytest.raises(ValueError, match="export_id is not a valid uuid."):
        mock_elements_worker.download_export("mon export")


def test_download_export(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        "http://testserver/api/v1/export/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff/",
        status=302,
        body=b"some SQLite export",
        content_type="application/x-sqlite3",
        stream=True,
    )

    export = mock_elements_worker.download_export(
        "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff"
    )
    assert export.name == "/tmp/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff"

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/export/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeffff/",
        ),
    ]


def mock_list_exports_call(responses, export_id):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/",
        status=200,
        json={
            "count": len(CorpusExportState),
            "next": None,
            "results": [
                {
                    "id": str(uuid.uuid4())
                    if state != CorpusExportState.Done
                    else export_id,
                    "created": "2019-08-24T14:15:22Z",
                    "updated": "2019-08-24T14:15:22Z",
                    "corpus_id": CORPUS_ID,
                    "user": {
                        "id": 0,
                        "email": "user@example.com",
                        "display_name": "User",
                    },
                    "state": state.value,
                    "source": "default",
                }
                for state in CorpusExportState
            ],
        },
    )


def test_download_latest_export_list_error(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        mock_elements_worker.download_latest_export()

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # The API call is retried 5 times
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
    ]


def test_download_latest_export_no_available_exports(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/",
        status=200,
        json={
            "count": 0,
            "next": None,
            "results": [],
        },
    )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f'No available exports found for the corpus ({CORPUS_ID}) with state "Done".'
        ),
    ):
        mock_elements_worker.download_latest_export()

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
    ]


def test_download_latest_export_download_error(responses, mock_elements_worker):
    export_id = str(uuid.uuid4())
    mock_list_exports_call(responses, export_id)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/export/{export_id}/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.download_latest_export()

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
        ("GET", f"http://testserver/api/v1/export/{export_id}/"),
    ]


def test_download_latest_export(responses, mock_elements_worker):
    export_id = str(uuid.uuid4())
    mock_list_exports_call(responses, export_id)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/export/{export_id}/",
        status=302,
        body=b"some SQLite export",
        content_type="application/x-sqlite3",
        stream=True,
    )

    export = mock_elements_worker.download_latest_export()
    assert export.name == f"/tmp/{export_id}"

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/export/"),
        ("GET", f"http://testserver/api/v1/export/{export_id}/"),
    ]
