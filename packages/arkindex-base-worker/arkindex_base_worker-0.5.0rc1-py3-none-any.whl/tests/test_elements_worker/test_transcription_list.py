from uuid import UUID

import pytest

from arkindex_worker.cache import CachedElement, CachedTranscription
from arkindex_worker.models import Element

from . import BASE_API_CALLS


def test_list_transcriptions_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_transcriptions(element=None)

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_transcriptions(element="not element type")


def test_list_transcriptions_wrong_element_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="element_type should be of type str"):
        mock_elements_worker.list_transcriptions(
            element=elt,
            element_type=1234,
        )


def test_list_transcriptions_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="recursive should be of type bool"):
        mock_elements_worker.list_transcriptions(
            element=elt,
            recursive="not bool",
        )


def test_list_transcriptions_wrong_worker_run(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="worker_run should be of type str or bool"
    ):
        mock_elements_worker.list_transcriptions(
            element=elt,
            worker_run=1234,
        )


def test_list_transcriptions_wrong_worker_version(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
        ),
        pytest.raises(
            AssertionError, match="worker_version should be of type str or bool"
        ),
    ):
        mock_elements_worker.list_transcriptions(
            element=elt,
            worker_version=1234,
        )


def test_list_transcriptions_wrong_bool_worker_run(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="if of type bool, worker_run can only be set to False"
    ):
        mock_elements_worker.list_transcriptions(
            element=elt,
            worker_run=True,
        )


def test_list_transcriptions_wrong_bool_worker_version(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
        ),
        pytest.raises(
            AssertionError,
            match="if of type bool, worker_version can only be set to False",
        ),
    ):
        mock_elements_worker.list_transcriptions(
            element=elt,
            worker_version=True,
        )


def test_list_transcriptions_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_transcriptions(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
    ]


def test_list_transcriptions(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    trans = [
        {
            "id": "0000",
            "text": "hey",
            "confidence": 0.42,
            "worker_version_id": "56785678-5678-5678-5678-567856785678",
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "element": None,
        },
        {
            "id": "1111",
            "text": "it's",
            "confidence": 0.42,
            "worker_version_id": "56785678-5678-5678-5678-567856785678",
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "element": None,
        },
        {
            "id": "2222",
            "text": "me",
            "confidence": 0.42,
            "worker_version_id": "56785678-5678-5678-5678-567856785678",
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "element": None,
        },
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": trans,
        },
    )

    for idx, transcription in enumerate(
        mock_elements_worker.list_transcriptions(element=elt)
    ):
        assert transcription == trans[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/",
        ),
    ]


def test_list_transcriptions_manual_worker_version(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    trans = [
        {
            "id": "0000",
            "text": "hey",
            "confidence": 0.42,
            "worker_version_id": None,
            "worker_run_id": None,
            "element": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/?worker_version=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": trans,
        },
    )

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        for idx, transcription in enumerate(
            mock_elements_worker.list_transcriptions(element=elt, worker_version=False)
        ):
            assert transcription == trans[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/?worker_version=False",
        ),
    ]


def test_list_transcriptions_manual_worker_run(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    trans = [
        {
            "id": "0000",
            "text": "hey",
            "confidence": 0.42,
            "worker_version_id": None,
            "worker_run_id": None,
            "element": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/?worker_run=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": trans,
        },
    )

    for idx, transcription in enumerate(
        mock_elements_worker.list_transcriptions(element=elt, worker_run=False)
    ):
        assert transcription == trans[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/transcriptions/?worker_run=False",
        ),
    ]


@pytest.mark.usefixtures("_mock_cached_transcriptions")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element should give first and sixth transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "66666666-6666-6666-6666-666666666666",
            ),
        ),
        # Filter on element and element_type should give first and sixth transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "element_type": "page",
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "66666666-6666-6666-6666-666666666666",
            ),
        ),
        # Filter on element and worker run should give the first transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_run": "56785678-5678-5678-5678-567856785678",
            },
            ("11111111-1111-1111-1111-111111111111",),
        ),
        # Filter on element, manual worker run should give the sixth transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_run": False,
            },
            ("66666666-6666-6666-6666-666666666666",),
        ),
        # Filter recursively on element should give all transcriptions inserted
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "recursive": True,
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-5555-5555-555555555555",
                "66666666-6666-6666-6666-666666666666",
            ),
        ),
        # Filter recursively on element and element_type should give three transcriptions
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "element_type": "something_else",
                "recursive": True,
            },
            (
                "22222222-2222-2222-2222-222222222222",
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-5555-5555-555555555555",
            ),
        ),
    ],
)
def test_list_transcriptions_with_cache(
    responses, mock_elements_worker_with_cache, filters, expected_ids
):
    # Check we have 5 elements already present in database
    assert CachedTranscription.select().count() == 6

    # Query database through cache
    transcriptions = mock_elements_worker_with_cache.list_transcriptions(**filters)
    assert transcriptions.count() == len(expected_ids)
    for transcription, expected_id in zip(
        transcriptions.order_by(CachedTranscription.id), expected_ids, strict=True
    ):
        assert transcription.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.usefixtures("_mock_cached_transcriptions")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element and worker_version should give first transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            ("11111111-1111-1111-1111-111111111111",),
        ),
        # Filter recursively on element and worker_version should give four transcriptions
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_version": "90129012-9012-9012-9012-901290129012",
                "recursive": True,
            },
            (
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
                "44444444-4444-4444-4444-444444444444",
                "55555555-5555-5555-5555-555555555555",
            ),
        ),
        # Filter on element with manually created transcription should give sixth transcription
        (
            {
                "element": CachedElement(
                    id="11111111-1111-1111-1111-111111111111", type="page"
                ),
                "worker_version": False,
            },
            ("66666666-6666-6666-6666-666666666666",),
        ),
    ],
)
def test_list_transcriptions_with_cache_deprecation(
    responses, mock_elements_worker_with_cache, filters, expected_ids
):
    # Check we have 5 elements already present in database
    assert CachedTranscription.select().count() == 6

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        # Query database through cache
        transcriptions = mock_elements_worker_with_cache.list_transcriptions(**filters)
    assert transcriptions.count() == len(expected_ids)
    for transcription, expected_id in zip(
        transcriptions.order_by(CachedTranscription.id), expected_ids, strict=True
    ):
        assert transcription.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS
