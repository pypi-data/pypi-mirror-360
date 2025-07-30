import json
import re

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE
from tests import CORPUS_ID

from . import BASE_API_CALLS


def test_create_sub_element_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="element shouldn't be null and should be of type Element"
    ):
        mock_elements_worker.create_sub_element(
            element=None,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    with pytest.raises(
        AssertionError, match="element shouldn't be null and should be of type Element"
    ):
        mock_elements_worker.create_sub_element(
            element="not element type",
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )


def test_create_sub_element_wrong_type(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type=None,
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type=1234,
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )


def test_create_sub_element_wrong_name(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name=None,
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name=1234,
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )


def test_create_sub_element_wrong_polygon(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(AssertionError, match="polygon should be None or a list"):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon="not a polygon",
        )

    with pytest.raises(
        AssertionError, match="polygon should have at least three points"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1, 1], [2, 2]],
        )

    with pytest.raises(
        AssertionError, match="polygon points should be lists of two items"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
        )

    with pytest.raises(
        AssertionError, match="polygon points should be lists of two items"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[[1], [2], [2], [1]],
        )

    with pytest.raises(
        AssertionError, match="polygon points should be lists of two numbers"
    ):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="O",
            polygon=[["not a coord", 1], [2, 2], [2, 1], [1, 2]],
        )


@pytest.mark.parametrize("confidence", ["lol", "0.2", -1.0, 1.42, float("inf")])
def test_create_sub_element_wrong_confidence(mock_elements_worker, confidence):
    with pytest.raises(
        AssertionError,
        match=re.escape("confidence should be None or a float in [0..1] range"),
    ):
        mock_elements_worker.create_sub_element(
            element=Element({"zone": None}),
            type="something",
            name="blah",
            polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            confidence=confidence,
        )


@pytest.mark.parametrize(
    ("image", "error_type", "error_message"),
    [
        (1, AssertionError, "image should be None or string"),
        ("not a uuid", ValueError, "image is not a valid uuid."),
    ],
)
def test_create_sub_element_wrong_image(
    mock_elements_worker, image, error_type, error_message
):
    with pytest.raises(error_type, match=re.escape(error_message)):
        mock_elements_worker.create_sub_element(
            element=Element({"zone": None}),
            type="something",
            name="blah",
            polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            image=image,
        )


def test_create_sub_element_wrong_image_and_polygon(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "An image or a parent with an image is required to create an element with a polygon."
        ),
    ):
        mock_elements_worker.create_sub_element(
            element=Element({"zone": None}),
            type="something",
            name="blah",
            polygon=[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]],
            image=None,
        )


def test_create_sub_element_api_error(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": CORPUS_ID},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_sub_element(
            element=elt,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/elements/create/")]


@pytest.mark.parametrize("slim_output", [True, False])
def test_create_sub_element(responses, mock_elements_worker, slim_output):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": CORPUS_ID},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    child_elt = {
        "id": "12345678-1234-1234-1234-123456789123",
        "corpus": {"id": CORPUS_ID},
        "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
    }
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=200,
        json=child_elt,
    )

    element_creation_response = mock_elements_worker.create_sub_element(
        element=elt,
        type="something",
        name="0",
        polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        slim_output=slim_output,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/elements/create/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "something",
        "name": "0",
        "image": None,
        "corpus": CORPUS_ID,
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        "parent": "12341234-1234-1234-1234-123412341234",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": None,
    }
    if slim_output:
        assert element_creation_response == "12345678-1234-1234-1234-123456789123"
    else:
        assert Element(element_creation_response) == Element(child_elt)


def test_create_sub_element_confidence(responses, mock_elements_worker):
    elt = Element(
        {
            "id": "12341234-1234-1234-1234-123412341234",
            "corpus": {"id": CORPUS_ID},
            "zone": {"image": {"id": "22222222-2222-2222-2222-222222222222"}},
        }
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/create/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    sub_element_id = mock_elements_worker.create_sub_element(
        element=elt,
        type="something",
        name="0",
        polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        confidence=0.42,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/elements/create/"),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "something",
        "name": "0",
        "image": None,
        "corpus": CORPUS_ID,
        "polygon": [[1, 1], [2, 2], [2, 1], [1, 2]],
        "parent": "12341234-1234-1234-1234-123412341234",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
    }
    assert sub_element_id == "12345678-1234-1234-1234-123456789123"


@pytest.mark.parametrize(
    ("params", "error_message"),
    [
        (
            {"parent": None, "child": None},
            "parent shouldn't be null and should be of type Element",
        ),
        (
            {"parent": "not an element", "child": None},
            "parent shouldn't be null and should be of type Element",
        ),
        (
            {"parent": Element(zone=None), "child": None},
            "child shouldn't be null and should be of type Element",
        ),
        (
            {"parent": Element(zone=None), "child": "not an element"},
            "child shouldn't be null and should be of type Element",
        ),
    ],
)
def test_create_element_parent_invalid_params(
    mock_elements_worker, params, error_message
):
    with pytest.raises(AssertionError, match=re.escape(error_message)):
        mock_elements_worker.create_element_parent(**params)


def test_create_element_parent_api_error(responses, mock_elements_worker):
    parent = Element({"id": "12341234-1234-1234-1234-123412341234"})
    child = Element({"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_element_parent(
            parent=parent,
            child=child,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        )
    ]


def test_create_element_parent(responses, mock_elements_worker):
    parent = Element({"id": "12341234-1234-1234-1234-123412341234"})
    child = Element({"id": "497f6eca-6276-4993-bfeb-53cbbbba6f08"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        status=200,
        json={
            "parent": "12341234-1234-1234-1234-123412341234",
            "child": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
        },
    )

    created_element_parent = mock_elements_worker.create_element_parent(
        parent=parent,
        child=child,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/497f6eca-6276-4993-bfeb-53cbbbba6f08/parent/12341234-1234-1234-1234-123412341234/",
        ),
    ]
    assert created_element_parent == {
        "parent": "12341234-1234-1234-1234-123412341234",
        "child": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
    }


@pytest.mark.parametrize(
    ("arg_name", "data", "error_message"),
    [
        (
            "parent",
            None,
            "parent shouldn't be null and should be of type Element",
        ),
        (
            "parent",
            "not element type",
            "parent shouldn't be null and should be of type Element",
        ),
        (
            "children",
            None,
            "children shouldn't be null and should be of type list",
        ),
        (
            "children",
            "not a list",
            "children shouldn't be null and should be of type list",
        ),
        (
            "children",
            [
                Element({"id": "11111111-1111-1111-1111-111111111111"}),
                "not element type",
            ],
            "Child at index 1 in children: Should be of type Element",
        ),
    ],
)
def test_create_element_children_wrong_params(
    arg_name, data, error_message, mock_elements_worker
):
    with pytest.raises(AssertionError, match=error_message):
        mock_elements_worker.create_element_children(
            **{
                "parent": Element({"id": "12341234-1234-1234-1234-123412341234"}),
                "children": [
                    Element({"id": "11111111-1111-1111-1111-111111111111"}),
                    Element({"id": "22222222-2222-2222-2222-222222222222"}),
                ],
                # Overwrite with wrong data
                arg_name: data,
            },
        )


def test_create_element_children_api_error(responses, mock_elements_worker):
    parent = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/parent/{parent.id}/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_element_children(
            parent=parent,
            children=[
                Element({"id": "11111111-1111-1111-1111-111111111111"}),
                Element({"id": "22222222-2222-2222-2222-222222222222"}),
            ],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            f"http://testserver/api/v1/element/parent/{parent.id}/",
        )
    ]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_element_children(batch_size, responses, mock_elements_worker):
    parent = Element({"id": "12341234-1234-1234-1234-123412341234"})

    first_child = Element({"id": "11111111-1111-1111-1111-111111111111"})
    second_child = Element({"id": "22222222-2222-2222-2222-222222222222"})

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/parent/{parent.id}/",
        status=200,
        json={"children": []},
    )

    mock_elements_worker.create_element_children(
        parent=parent,
        children=[first_child, second_child],
        batch_size=batch_size,
    )

    bulk_api_calls = [
        (
            "POST",
            f"http://testserver/api/v1/element/parent/{parent.id}/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                f"http://testserver/api/v1/element/parent/{parent.id}/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({"children": [first_child.id, second_child.id]})
    else:
        first_call_idx = -2
        bodies.append({"children": [first_child.id]})
        bodies.append({"children": [second_child.id]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies
