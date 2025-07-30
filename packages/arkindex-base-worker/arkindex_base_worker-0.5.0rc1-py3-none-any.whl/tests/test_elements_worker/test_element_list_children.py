from uuid import UUID

import pytest

from arkindex_worker.cache import (
    CachedElement,
)
from arkindex_worker.models import Element

from . import BASE_API_CALLS


def test_list_elements_wrong_folder(mock_elements_worker):
    with pytest.raises(AssertionError, match="folder should be of type bool"):
        mock_elements_worker.list_elements(folder="not bool")


def test_list_elements_wrong_name(mock_elements_worker):
    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_elements(name=1234)


def test_list_elements_wrong_top_level(mock_elements_worker):
    with pytest.raises(AssertionError, match="top_level should be of type bool"):
        mock_elements_worker.list_elements(top_level="not bool")


def test_list_elements_wrong_type(mock_elements_worker):
    with pytest.raises(AssertionError, match="type should be of type str"):
        mock_elements_worker.list_elements(type=1234)


def test_list_elements_wrong_with_classes(mock_elements_worker):
    with pytest.raises(AssertionError, match="with_classes should be of type bool"):
        mock_elements_worker.list_elements(with_classes="not bool")


def test_list_elements_wrong_with_corpus(mock_elements_worker):
    with pytest.raises(AssertionError, match="with_corpus should be of type bool"):
        mock_elements_worker.list_elements(with_corpus="not bool")


def test_list_elements_wrong_with_has_children(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="with_has_children should be of type bool"
    ):
        mock_elements_worker.list_elements(with_has_children="not bool")


def test_list_elements_wrong_with_zone(mock_elements_worker):
    with pytest.raises(AssertionError, match="with_zone should be of type bool"):
        mock_elements_worker.list_elements(with_zone="not bool")


def test_list_elements_wrong_with_metadata(mock_elements_worker):
    with pytest.raises(AssertionError, match="with_metadata should be of type bool"):
        mock_elements_worker.list_elements(with_metadata="not bool")


@pytest.mark.parametrize(
    ("param", "value"),
    [
        ("worker_run", 1234),
        ("transcription_worker_run", 1234),
    ],
)
def test_list_elements_wrong_worker_run(mock_elements_worker, param, value):
    with pytest.raises(AssertionError, match=f"{param} should be of type str or bool"):
        mock_elements_worker.list_elements(**{param: value})


@pytest.mark.parametrize(
    ("param", "alternative", "value"),
    [
        ("worker_version", "worker_run", 1234),
        ("transcription_worker_version", "transcription_worker_run", 1234),
    ],
)
def test_list_elements_wrong_worker_version(
    mock_elements_worker, param, alternative, value
):
    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(AssertionError, match=f"{param} should be of type str or bool"),
    ):
        mock_elements_worker.list_elements(**{param: value})


@pytest.mark.parametrize(
    "param",
    [
        "worker_run",
        "transcription_worker_run",
    ],
)
def test_list_elements_wrong_bool_worker_run(mock_elements_worker, param):
    with pytest.raises(
        AssertionError, match=f"if of type bool, {param} can only be set to False"
    ):
        mock_elements_worker.list_elements(**{param: True})


@pytest.mark.parametrize(
    ("param", "alternative"),
    [
        ("worker_version", "worker_run"),
        ("transcription_worker_version", "transcription_worker_run"),
    ],
)
def test_list_elements_wrong_bool_worker_version(
    mock_elements_worker, param, alternative
):
    # WARNING: pytest.deprecated_call must be placed BEFORE pytest.raises, otherwise `match` argument won't be checked
    with (
        pytest.deprecated_call(
            match=f"`{param}` usage is deprecated. Consider using `{alternative}` instead."
        ),
        pytest.raises(
            AssertionError, match=f"if of type bool, {param} can only be set to False"
        ),
    ):
        mock_elements_worker.list_elements(**{param: True})


def test_list_elements_api_error(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_elements())

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        ),
    ]


def test_list_elements(responses, mock_elements_worker):
    expected_children = [
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
        f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(mock_elements_worker.list_elements()):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/",
        ),
    ]


def test_list_elements_manual_worker_version(responses, mock_elements_worker):
    expected_children = [
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
        f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/?worker_version=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_children,
        },
    )

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        for idx, child in enumerate(
            mock_elements_worker.list_elements(worker_version=False)
        ):
            assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/?worker_version=False",
        ),
    ]


def test_list_elements_manual_worker_run(responses, mock_elements_worker):
    expected_children = [
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
        f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/?worker_run=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(mock_elements_worker.list_elements(worker_run=False)):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{mock_elements_worker.corpus_id}/elements/?worker_run=False",
        ),
    ]


def test_list_elements_with_cache_unhandled_param(mock_elements_worker_with_cache):
    with pytest.raises(
        AssertionError,
        match="When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'",
    ):
        mock_elements_worker_with_cache.list_elements(with_corpus=True)


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element should give all elements inserted
        (
            {},
            (
                "99999999-9999-9999-9999-999999999999",
                "12341234-1234-1234-1234-123412341234",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
        # Filter on element and page should give the second element
        (
            {"type": "page"},
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element and worker run should give second
        (
            {
                "worker_run": "56785678-5678-5678-5678-567856785678",
            },
            (
                "12341234-1234-1234-1234-123412341234",
                "22222222-2222-2222-2222-222222222222",
            ),
        ),
        # Filter on element, manual worker run should give first and third
        (
            {"worker_run": False},
            (
                "99999999-9999-9999-9999-999999999999",
                "11111111-1111-1111-1111-111111111111",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
    ],
)
def test_list_elements_with_cache(
    responses, mock_elements_worker_with_cache, filters, expected_ids
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    # Query database through cache
    elements = mock_elements_worker_with_cache.list_elements(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids, strict=True):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element and worker version
        (
            {
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            (
                "12341234-1234-1234-1234-123412341234",
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ),
        ),
        # Filter on element, type double_page and worker version
        (
            {"type": "page", "worker_version": "56785678-5678-5678-5678-567856785678"},
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element, manual worker version
        (
            {"worker_version": False},
            (
                "99999999-9999-9999-9999-999999999999",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
    ],
)
def test_list_elements_with_cache_deprecation(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_ids,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        # Query database through cache
        elements = mock_elements_worker_with_cache.list_elements(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids, strict=True):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_list_element_children_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_children(element=None)

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.list_element_children(element="not element type")


def test_list_element_children_wrong_folder(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="folder should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            folder="not bool",
        )


def test_list_element_children_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="name should be of type str"):
        mock_elements_worker.list_element_children(
            element=elt,
            name=1234,
        )


def test_list_element_children_wrong_recursive(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="recursive should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            recursive="not bool",
        )


def test_list_element_children_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="type should be of type str"):
        mock_elements_worker.list_element_children(
            element=elt,
            type=1234,
        )


def test_list_element_children_wrong_with_classes(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_classes should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_classes="not bool",
        )


def test_list_element_children_wrong_with_corpus(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_corpus should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_corpus="not bool",
        )


def test_list_element_children_wrong_with_has_children(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="with_has_children should be of type bool"
    ):
        mock_elements_worker.list_element_children(
            element=elt,
            with_has_children="not bool",
        )


def test_list_element_children_wrong_with_zone(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_zone should be of type bool"):
        mock_elements_worker.list_element_children(
            element=elt,
            with_zone="not bool",
        )


def test_list_element_children_wrong_with_metadata(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match="with_metadata should be of type bool"):
        mock_elements_worker.list_element_children(
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
def test_list_element_children_wrong_worker_run(mock_elements_worker, param, value):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError, match=f"{param} should be of type str or bool"):
        mock_elements_worker.list_element_children(
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
def test_list_element_children_wrong_worker_version(
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
        mock_elements_worker.list_element_children(
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
def test_list_element_children_wrong_bool_worker_run(mock_elements_worker, param):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match=f"if of type bool, {param} can only be set to False"
    ):
        mock_elements_worker.list_element_children(
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
def test_list_element_children_wrong_bool_worker_version(
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
        mock_elements_worker.list_element_children(
            element=elt,
            **{param: True},
        )


def test_list_element_children_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.GET,
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_elements_worker.list_element_children(element=elt))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
    ]


def test_list_element_children(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
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
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(
        mock_elements_worker.list_element_children(element=elt)
    ):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/",
        ),
    ]


def test_list_element_children_manual_worker_version(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
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
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_version=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_children,
        },
    )

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        for idx, child in enumerate(
            mock_elements_worker.list_element_children(
                element=elt, worker_version=False
            )
        ):
            assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_version=False",
        ),
    ]


def test_list_element_children_manual_worker_run(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    expected_children = [
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
        "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_run=False",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": expected_children,
        },
    )

    for idx, child in enumerate(
        mock_elements_worker.list_element_children(element=elt, worker_run=False)
    ):
        assert child == expected_children[idx]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            "http://testserver/api/v1/elements/12341234-1234-1234-1234-123412341234/children/?worker_run=False",
        ),
    ]


def test_list_element_children_with_cache_unhandled_param(
    mock_elements_worker_with_cache,
):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError,
        match="When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'",
    ):
        mock_elements_worker_with_cache.list_element_children(
            element=elt, with_corpus=True
        )


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element should give all elements inserted
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
        # Filter on element and page should give the second element
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "type": "page",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element and worker run should give second
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_run": "56785678-5678-5678-5678-567856785678",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element, manual worker run should give first and third
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_run": False,
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "33333333-3333-3333-3333-333333333333",
            ),
        ),
    ],
)
def test_list_element_children_with_cache(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_ids,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    # Query database through cache
    elements = mock_elements_worker_with_cache.list_element_children(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids, strict=True):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize(
    ("filters", "expected_ids"),
    [
        # Filter on element and worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            (
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ),
        ),
        # Filter on element, type double_page and worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "type": "page",
                "worker_version": "56785678-5678-5678-5678-567856785678",
            },
            ("22222222-2222-2222-2222-222222222222",),
        ),
        # Filter on element, manual worker version
        (
            {
                "element": CachedElement(id="12341234-1234-1234-1234-123412341234"),
                "worker_version": False,
            },
            ("33333333-3333-3333-3333-333333333333",),
        ),
    ],
)
def test_list_element_children_with_cache_deprecation(
    responses,
    mock_elements_worker_with_cache,
    filters,
    expected_ids,
):
    # Check we have 5 elements already present in database
    assert CachedElement.select().count() == 5

    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        # Query database through cache
        elements = mock_elements_worker_with_cache.list_element_children(**filters)
    assert elements.count() == len(expected_ids)
    for child, expected_id in zip(elements.order_by("id"), expected_ids, strict=True):
        assert child.id == UUID(expected_id)

    # Check the worker never hits the API for elements
    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS
