import json
import re
from uuid import UUID

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.cache import (
    CachedElement,
    CachedImage,
)
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE

from . import BASE_API_CALLS


def test_create_elements_wrong_parent(mock_elements_worker):
    with pytest.raises(
        TypeError, match="Parent element should be an Element or CachedElement instance"
    ):
        mock_elements_worker.create_elements(
            parent=None,
            elements=[],
        )

    with pytest.raises(
        TypeError, match="Parent element should be an Element or CachedElement instance"
    ):
        mock_elements_worker.create_elements(
            parent="not element type",
            elements=[],
        )


def test_create_elements_no_zone(mock_elements_worker):
    elt = Element({"zone": None})
    with pytest.raises(
        AssertionError, match="create_elements cannot be used on parents without zones"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )

    elt = CachedElement(
        id="11111111-1111-1111-1111-1111111111", name="blah", type="blah"
    )
    with pytest.raises(
        AssertionError, match="create_elements cannot be used on parents without images"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )


def test_create_elements_wrong_elements(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError, match="elements shouldn't be null and should be of type list"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=None,
        )

    with pytest.raises(
        AssertionError, match="elements shouldn't be null and should be of type list"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements="not a list",
        )


def test_create_elements_wrong_elements_instance(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError, match="Element at index 0 in elements: Should be of type dict"
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=["not a dict"],
        )


def test_create_elements_wrong_elements_name(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: name shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": None,
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: name shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": 1234,
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )


def test_create_elements_wrong_elements_type(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: type shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": None,
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: type shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": 1234,
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )


def test_create_elements_wrong_elements_polygon(mock_elements_worker):
    elt = Element({"zone": {"image": {"id": "image_id"}}})

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": None,
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": "not a polygon",
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon should have at least three points",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1], [2, 2]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon points should be lists of two items",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon points should be lists of two items",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1], [2], [2], [1]],
                }
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Element at index 0 in elements: polygon points should be lists of two numbers",
    ):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )


@pytest.mark.parametrize("confidence", ["lol", "0.2", -1.0, 1.42, float("inf")])
def test_create_elements_wrong_elements_confidence(mock_elements_worker, confidence):
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Element at index 0 in elements: confidence should be None or a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_elements(
            parent=Element({"zone": {"image": {"id": "image_id"}}}),
            elements=[
                {
                    "name": "a",
                    "type": "something",
                    "polygon": [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
                    "confidence": confidence,
                }
            ],
        )


def test_create_elements_api_error(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_elements(
            parent=elt,
            elements=[
                {
                    "name": "0",
                    "type": "something",
                    "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                }
            ],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        )
    ]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_elements_cached_element(
    batch_size, responses, mock_elements_worker_with_cache
):
    image = CachedImage.create(
        id=UUID("c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe"),
        width=42,
        height=42,
        url="http://aaaa",
    )
    elt = CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="parent",
        image_id=image.id,
        polygon="[[0, 0], [0, 1000], [1000, 1000], [1000, 0], [0, 0]]",
    )

    if batch_size > 1:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
            status=200,
            json=[
                {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
                {"id": "5468c358-b9c4-499d-8b92-d6349c58e88d"},
            ],
        )
    else:
        for elt_id in [
            "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "5468c358-b9c4-499d-8b92-d6349c58e88d",
        ]:
            responses.add(
                responses.POST,
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
                status=200,
                json=[{"id": elt_id}],
            )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            },
            {
                "name": "1",
                "type": "something",
                "polygon": [[4, 4], [5, 5], [5, 4], [4, 5]],
            },
        ],
        batch_size=batch_size,
    )

    bulk_api_calls = [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_elt = {
        "name": "0",
        "type": "something",
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
    }
    second_elt = {
        "name": "1",
        "type": "something",
        "polygon": [[4, 4], [5, 5], [5, 4], [4, 5]],
    }
    empty_payload = {
        "elements": [],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "elements": [first_elt, second_elt]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "elements": [first_elt]})
        bodies.append({**empty_payload, "elements": [second_elt]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    assert created_ids == [
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        {"id": "5468c358-b9c4-499d-8b92-d6349c58e88d"},
    ]

    # Check that created elements were properly stored in SQLite cache
    assert list(CachedElement.select().order_by(CachedElement.id)) == [
        elt,
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=elt.id,
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=None,
        ),
        CachedElement(
            id=UUID("5468c358-b9c4-499d-8b92-d6349c58e88d"),
            parent_id=elt.id,
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[4, 4], [5, 5], [5, 4], [4, 5]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=None,
        ),
    ]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_elements(
    batch_size, responses, mock_elements_worker_with_cache, tmp_path
):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )

    if batch_size > 1:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
            status=200,
            json=[
                {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
                {"id": "5468c358-b9c4-499d-8b92-d6349c58e88d"},
            ],
        )
    else:
        for elt_id in [
            "497f6eca-6276-4993-bfeb-53cbbbba6f08",
            "5468c358-b9c4-499d-8b92-d6349c58e88d",
        ]:
            responses.add(
                responses.POST,
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
                status=200,
                json=[{"id": elt_id}],
            )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
            },
            {
                "name": "1",
                "type": "something",
                "polygon": [[4, 4], [5, 5], [5, 4], [4, 5]],
            },
        ],
        batch_size=batch_size,
    )

    bulk_api_calls = [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_elt = {
        "name": "0",
        "type": "something",
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
    }
    second_elt = {
        "name": "1",
        "type": "something",
        "polygon": [[4, 4], [5, 5], [5, 4], [4, 5]],
    }
    empty_payload = {
        "elements": [],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "elements": [first_elt, second_elt]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "elements": [first_elt]})
        bodies.append({**empty_payload, "elements": [second_elt]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    assert created_ids == [
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        {"id": "5468c358-b9c4-499d-8b92-d6349c58e88d"},
    ]

    # Check that created elements were properly stored in SQLite cache
    assert (tmp_path / "db.sqlite").is_file()

    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=None,
        ),
        CachedElement(
            id=UUID("5468c358-b9c4-499d-8b92-d6349c58e88d"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[4, 4], [5, 5], [5, 4], [4, 5]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=None,
        ),
    ]


def test_create_elements_confidence(
    responses, mock_elements_worker_with_cache, tmp_path
):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}],
    )

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=[
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                "confidence": 0.42,
            }
        ],
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "elements": [
            {
                "name": "0",
                "type": "something",
                "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
                "confidence": 0.42,
            }
        ],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert created_ids == [{"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"}]

    # Check that created elements were properly stored in SQLite cache
    assert (tmp_path / "db.sqlite").is_file()

    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("497f6eca-6276-4993-bfeb-53cbbbba6f08"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="something",
            image_id="c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=0.42,
        )
    ]


def test_create_elements_integrity_error(
    responses, mock_elements_worker_with_cache, caplog
):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "zone": {
                "image": {
                    "id": "c0fec0fe-c0fe-c0fe-c0fe-c0fec0fec0fe",
                    "width": 42,
                    "height": 42,
                    "url": "http://aaaa",
                }
            },
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/children/bulk/",
        status=200,
        json=[
            # Duplicate IDs, which will cause an IntegrityError when stored in the cache
            {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
            {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        ],
    )

    elements = [
        {
            "name": "0",
            "type": "something",
            "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        },
        {
            "name": "1",
            "type": "something",
            "polygon": [[1, 1], [3, 3], [3, 1], [1, 3]],
        },
    ]

    created_ids = mock_elements_worker_with_cache.create_elements(
        parent=elt,
        elements=elements,
    )

    assert created_ids == [
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
        {"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"},
    ]

    assert len(caplog.records) == 3
    assert caplog.records[-1].levelname == "WARNING"
    assert caplog.records[-1].message.startswith(
        "Couldn't save created elements in local cache:"
    )

    assert list(CachedElement.select()) == []
