from uuid import UUID

import pytest

from arkindex_worker.cache import (
    CachedElement,
)
from arkindex_worker.models import Element

from . import BASE_API_CALLS


def test_list_element_parents_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_parents(element=None)

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_parents(element="not element type")


def test_list_element_parents_wrong_folder(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="folder should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            folder="not bool",
        )


def test_list_element_parents_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_element_parents(
            element=elt,
            name=1234,
        )


def test_list_element_parents_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="recursive should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            recursive="not bool",
        )


def test_list_element_parents_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="type should be of type str"):
        mock_elements_worker.list_element_parents(
            element=elt,
            type=1234,
        )


def test_list_element_parents_wrong_with_classes(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_classes should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_classes="not bool",
        )


def test_list_element_parents_wrong_with_corpus(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_corpus should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_corpus="not bool",
        )


def test_list_element_parents_wrong_with_has_children(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="with_has_children should be of type bool"
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_has_children="not bool",
        )


def test_list_element_parents_wrong_with_zone(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_zone should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_zone="not bool",
        )


def test_list_element_parents_wrong_with_metadata(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_metadata should be of type bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            with_metadata="not bool",
        )


@pytest.mark.parametrize(
    ("param", "value"),
    [
        ("worker_run", 1234),
        ("transcription_worker_run", 1234),
    ],
)
def test_list_element_parents_wrong_worker_run(mock_elements_worker, param, value):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match=f"{param} should be of type str or bool"):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: value},
        )


@pytest.mark.parametrize(
    ("param", "alternative", "value"),
    [
        ("worker_version", "worker_run", 1234),
        ("transcription_worker_version", "transcription_worker_run", 1234),
    ],
)
def test_list_element_parents_wrong_worker_version(
    mock_elements_worker, param, alternative, value
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(AssertionError, match=f"{param} should be of type str or bool"),
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: value},
        )


@pytest.mark.parametrize(
    "param",
    [
        "worker_run",
        "transcription_worker_run",
    ],
)
def test_list_element_parents_wrong_bool_worker_run(mock_elements_worker, param):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match=f"if of type bool, {param} can only be set to False"
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: True},
        )


@pytest.mark.parametrize(
    ("param", "alternative"),
    [
        ("worker_version", "worker_run"),
        ("transcription_worker_version", "transcription_worker_run"),
    ],
)
def test_list_element_parents_wrong_bool_worker_version(
    mock_elements_worker, param, alternative
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(
            AssertionError, match=f"if of type bool, {param} can only be set to False"
        ),
    ):
        mock_elements_worker.list_element_parents(
            element=elt,
            **{param: True},
        )


def test_list_element_parents_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_element_parents(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
    ]


def test_list_element_parents(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_parents = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
        {
            "id": "1111",
            "type": "page",
            "name": "Test 2",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
        {
            "id": "2222",
            "type": "page",
            "name": "Test 3",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        },
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_parents,
        },
    )

    for idx, parent in enumerate(
        mock_elements_worker.list_element_parents(element=elt)
    ):
        assert parent == expected_parents[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/",
        ),
    ]


def test_list_element_parents_manual_worker_version(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_parents = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_version=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_parents,
        },
    )

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        for idx, parent in enumerate(
            mock_elements_worker.list_element_parents(element=elt, worker_version=False)
        ):
            assert parent == expected_parents[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_version=False",
        ),
    ]


def test_list_element_parents_manual_worker_run(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_parents = [
        {
            "id": "0000",
            "type": "page",
            "name": "Test",
            "corpus": {},
            "thumbnail_url": None,
            "zone": {},
            "best_classes": None,
            "has_children": None,
            "worker_version_id": None,
            "worker_run_id": None,
        }
    ]
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_run=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_parents,
        },
    )

    for idx, parent in enumerate(
        mock_elements_worker.list_element_parents(element=elt, worker_run=False)
    ):
        assert parent == expected_parents[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/parents/?worker_run=False",
        ),
    ]


def test_list_element_parents_with_cache_unhandled_param(
    mock_elements_worker_with_cache,
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError,
        match="When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'",
    ):
        mock_elements_worker_with_cache.list_element_parents(
            element=elt, with_corpus=True
        )


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_id"),
    [
        # Filter on element
        (
            {
                "element": CachedElement(id="11111111-1111-1111-1111-111111111111"),
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element and double_page
        (
            {
                "element": CachedElement(id="22222222-2222-2222-2222-222222222222"),
                "type": "double_page",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element and worker run
        (
            {
                "element": CachedElement(id="22222222-2222-2222-2222-222222222222"),
                "worker_run": "56785678-5678-5678-5678-567856785678",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element, manual worker run
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_run": False,
            },
            "99999999-9999-9999-9999-999999999999",
        ),
    ],
)
def test_list_element_parents_with_cache(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_id,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    # Query database through cache
    elements = mock_elements_worker_with_cache.list_element_parents(**filters)
    assert elements.count() == 1
    for parent in elements.order_by("id"):
        assert parent.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_id"),
    [
        # Filter on element and worker version
        (
            {
                "element": CachedElement(id="33333333-3333-3333-3333-333333333333"),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element, type double_page and worker version
        (
            {
                "element": CachedElement(id="11111111-1111-1111-1111-111111111111"),
                "type": "double_page",
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            "12341234-1234-1234-1234-123412341234",
        ),
        # Filter on element, manual worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": False,
            },
            "99999999-9999-9999-9999-999999999999",
        ),
    ],
)
def test_list_element_parents_with_cache_deprecation(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_id,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        # Query database through cache
        elements = mock_elements_worker_with_cache.list_element_parents(**filters)
    assert elements.count() == 1
    for parent in elements.order_by("id"):
        assert parent.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS
