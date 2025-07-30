import json
import re
from uuid import UUID

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.cache import CachedClassification, CachedElement
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE
from tests import CORPUS_ID

from . import BASE_API_CALLS

# Special string used to know if the `arg_name` passed in
# `pytest.mark.parametrize` should be removed from the payload
DELETE_PARAMETER = "DELETE_PARAMETER"


def test_load_corpus_classes_api_error(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=418,
    )

    assert not mock_elements_worker.classes
    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        mock_elements_worker.load_corpus_classes()

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We do 5 retries
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
    ]
    assert not mock_elements_worker.classes


def test_load_corpus_classes(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": [
                {
                    "id": "0000",
                    "name": "good",
                },
                {
                    "id": "1111",
                    "name": "average",
                },
                {
                    "id": "2222",
                    "name": "bad",
                },
            ],
        },
    )

    assert not mock_elements_worker.classes
    mock_elements_worker.load_corpus_classes()

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
    ]
    assert mock_elements_worker.classes == {
        "good": "0000",
        "average": "1111",
        "bad": "2222",
    }


def test_get_ml_class_id_load_classes(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "0000",
                    "name": "good",
                }
            ],
        },
    )

    assert not mock_elements_worker.classes
    ml_class_id = mock_elements_worker.get_ml_class_id("good")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
    ]
    assert mock_elements_worker.classes == {"good": "0000"}
    assert ml_class_id == "0000"


def test_get_ml_class_id_inexistant_class(mock_elements_worker, responses):
    # A missing class is now created automatically
    mock_elements_worker.classes = {"good": "0000"}

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=201,
        json={"id": "new-ml-class-1234"},
    )

    # Missing class at first
    assert mock_elements_worker.classes == {"good": "0000"}

    ml_class_id = mock_elements_worker.get_ml_class_id("bad")
    assert ml_class_id == "new-ml-class-1234"

    # Now it's available
    assert mock_elements_worker.classes == {
        "good": "0000",
        "bad": "new-ml-class-1234",
    }


def test_get_ml_class_id(mock_elements_worker):
    mock_elements_worker.classes = {"good": "0000"}

    ml_class_id = mock_elements_worker.get_ml_class_id("good")
    assert ml_class_id == "0000"


def test_get_ml_class_reload(responses, mock_elements_worker):
    # Add some initial classes
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "class1_id",
                    "name": "class1",
                }
            ],
        },
    )

    # Invalid response when trying to create class2
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=400,
        json={"non_field_errors": "Already exists"},
    )

    # Add both classes (class2 is created by another process)
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        json={
            "count": 2,
            "next": None,
            "results": [
                {
                    "id": "class1_id",
                    "name": "class1",
                },
                {
                    "id": "class2_id",
                    "name": "class2",
                },
            ],
        },
    )

    # Simply request class 2, it should be reloaded
    assert mock_elements_worker.get_ml_class_id("class2") == "class2_id"

    assert len(responses.calls) == len(BASE_API_CALLS) + 3
    assert mock_elements_worker.classes == {
        "class1": "class1_id",
        "class2": "class2_id",
    }
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        (
            "POST",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
    ]


def test_retrieve_ml_class_in_cache(mock_elements_worker):
    """
    Look for a class that exists in cache -> No API Call
    """
    mock_elements_worker.classes = {"class1": "uuid1"}

    assert mock_elements_worker.retrieve_ml_class("uuid1") == "class1"


def test_retrieve_ml_class_not_in_cache(responses, mock_elements_worker):
    """
    Retrieve class not in cache -> Retrieve corpus ml classes via API
    """
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": [
                {
                    "id": "uuid1",
                    "name": "class1",
                },
            ],
        },
    )
    assert mock_elements_worker.retrieve_ml_class("uuid1") == "class1"
    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
    ]


@pytest.mark.parametrize(
    ("arg_name", "data", "error_message"),
    [
        # Wrong element
        (
            "element",
            None,
            "element shouldn't be null and should be an Element or CachedElement",
        ),
        (
            "element",
            "not element type",
            "element shouldn't be null and should be an Element or CachedElement",
        ),
        # Wrong ml_class
        (
            "ml_class",
            None,
            "ml_class shouldn't be null and should be of type str",
        ),
        (
            "ml_class",
            1234,
            "ml_class shouldn't be null and should be of type str",
        ),
        # Wrong confidence
        (
            "confidence",
            None,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            "wrong confidence",
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            0,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            2.00,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        # Wrong high_confidence
        (
            "high_confidence",
            None,
            "high_confidence shouldn't be null and should be of type bool",
        ),
        (
            "high_confidence",
            "wrong high_confidence",
            "high_confidence shouldn't be null and should be of type bool",
        ),
    ],
)
def test_create_classification_wrong_data(
    arg_name, data, error_message, mock_elements_worker
):
    mock_elements_worker.classes = {"a_class": "0000"}
    with pytest.raises(AssertionError, match=re.escape(error_message)):
        mock_elements_worker.create_classification(
            **{
                "element": Element({"id": "12341234-1234-1234-1234-123412341234"}),
                "ml_class": "a_class",
                "confidence": 0.42,
                "high_confidence": True,
                # Overwrite with wrong data
                arg_name: data,
            }
        )


def test_create_classification_api_error(responses, mock_elements_worker):
    mock_elements_worker.classes = {"a_class": "0000"}
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_classification(
            element=elt,
            ml_class="a_class",
            confidence=0.42,
            high_confidence=True,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/classifications/")]


def test_create_classification_create_ml_class(mock_elements_worker, responses):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # Automatically create a missing class!
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=201,
        json={"id": "new-ml-class-1234"},
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=201,
        json={"id": "new-classification-1234"},
    )
    mock_elements_worker.classes = {"another_class": "0000"}
    mock_elements_worker.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    # Check a class & classification has been created
    assert [
        (call.request.url, json.loads(call.request.body))
        for call in responses.calls[-2:]
    ] == [
        (
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
            {"name": "a_class"},
        ),
        (
            "http://testserver/api/v1/classifications/",
            {
                "element": "12341234-1234-1234-1234-123412341234",
                "ml_class": "new-ml-class-1234",
                "worker_run_id": "56785678-5678-5678-5678-567856785678",
                "confidence": 0.42,
                "high_confidence": True,
            },
        ),
    ]


def test_create_classification(responses, mock_elements_worker):
    mock_elements_worker.classes = {"a_class": "0000"}
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=200,
    )

    mock_elements_worker.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classifications/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element": "12341234-1234-1234-1234-123412341234",
        "ml_class": "0000",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
        "high_confidence": True,
    }


def test_create_classification_with_cache(responses, mock_elements_worker_with_cache):
    mock_elements_worker_with_cache.classes = {"a_class": "0000"}
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "element": "12341234-1234-1234-1234-123412341234",
            "ml_class": "0000",
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "confidence": 0.42,
            "high_confidence": True,
            "state": "pending",
        },
    )

    mock_elements_worker_with_cache.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classifications/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element": "12341234-1234-1234-1234-123412341234",
        "ml_class": "0000",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
        "high_confidence": True,
    }

    # Check that created classification was properly stored in SQLite cache
    assert list(CachedClassification.select()) == [
        CachedClassification(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            element_id=UUID(elt.id),
            class_name="a_class",
            confidence=0.42,
            state="pending",
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
    ]


def test_create_classification_duplicate_worker_run(responses, mock_elements_worker):
    mock_elements_worker.classes = {"a_class": "0000"}
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classifications/",
        status=400,
        json={
            "non_field_errors": [
                "The fields element, worker_run, ml_class must make a unique set."
            ]
        },
    )

    mock_elements_worker.create_classification(
        element=elt,
        ml_class="a_class",
        confidence=0.42,
        high_confidence=True,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/classifications/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "element": "12341234-1234-1234-1234-123412341234",
        "ml_class": "0000",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
        "high_confidence": True,
    }


@pytest.mark.parametrize(
    ("arg_name", "data", "error_message"),
    [
        (
            "element",
            None,
            "element shouldn't be null and should be an Element or CachedElement",
        ),
        (
            "element",
            "not element type",
            "element shouldn't be null and should be an Element or CachedElement",
        ),
        (
            "classifications",
            None,
            "classifications shouldn't be null and should be of type list",
        ),
        (
            "classifications",
            1234,
            "classifications shouldn't be null and should be of type list",
        ),
    ],
)
def test_create_classifications_wrong_data(
    arg_name, data, error_message, mock_elements_worker
):
    with pytest.raises(AssertionError, match=error_message):
        mock_elements_worker.create_classifications(
            **{
                "element": Element({"id": "12341234-1234-1234-1234-123412341234"}),
                "classifications": [
                    {
                        "ml_class": "cat",
                        "confidence": 0.75,
                        "high_confidence": False,
                    },
                    {
                        "ml_class": "dog",
                        "confidence": 0.25,
                        "high_confidence": False,
                    },
                ],
                # Overwrite with wrong data
                arg_name: data,
            },
        )


@pytest.mark.parametrize(
    ("arg_name", "data", "error_message"),
    [
        # Wrong classifications > ml_class
        (
            "ml_class",
            DELETE_PARAMETER,
            "ml_class shouldn't be null and should be of type str",
        ),
        (
            "ml_class",
            None,
            "ml_class shouldn't be null and should be of type str",
        ),
        (
            "ml_class",
            1234,
            "ml_class shouldn't be null and should be of type str",
        ),
        # Wrong classifications > confidence
        (
            "confidence",
            DELETE_PARAMETER,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            None,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            "wrong confidence",
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            0,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        (
            "confidence",
            2.00,
            "confidence shouldn't be null and should be a float in [0..1] range",
        ),
        # Wrong classifications > high_confidence
        (
            "high_confidence",
            "wrong high_confidence",
            "high_confidence should be of type bool",
        ),
    ],
)
def test_create_classifications_wrong_classifications_data(
    arg_name, data, error_message, mock_elements_worker
):
    all_data = {
        "element": Element({"id": "12341234-1234-1234-1234-123412341234"}),
        "classifications": [
            {
                "ml_class": "cat",
                "confidence": 0.75,
                "high_confidence": False,
            },
            {
                "ml_class": "dog",
                "confidence": 0.25,
                "high_confidence": False,
                # Overwrite with wrong data
                arg_name: data,
            },
        ],
    }
    if data == DELETE_PARAMETER:
        del all_data["classifications"][1][arg_name]

    with pytest.raises(
        AssertionError,
        match=re.escape(
            f"Classification at index 1 in classifications: {error_message}"
        ),
    ):
        mock_elements_worker.create_classifications(**all_data)


def test_create_classifications_api_error(responses, mock_elements_worker):
    mock_elements_worker.classes = {"cat": "0000", "dog": "1111"}
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classification/bulk/",
        status=418,
    )
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    classes = [
        {
            "ml_class": "cat",
            "confidence": 0.75,
            "high_confidence": False,
        },
        {
            "ml_class": "dog",
            "confidence": 0.25,
            "high_confidence": False,
        },
    ]

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_classifications(
            element=elt, classifications=classes
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/classification/bulk/")]


def test_create_classifications_create_ml_class(mock_elements_worker, responses):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    # Automatically create a missing class!
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        status=201,
        json={"id": "new-ml-class-1234"},
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classification/bulk/",
        status=201,
        json={
            "parent": str(elt.id),
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "classifications": [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "ml_class": "new-ml-class-1234",
                    "confidence": 0.75,
                    "high_confidence": False,
                    "state": "pending",
                },
            ],
        },
    )
    mock_elements_worker.classes = {"another_class": "0000"}
    mock_elements_worker.create_classifications(
        element=elt,
        classifications=[
            {
                "ml_class": "a_class",
                "confidence": 0.75,
                "high_confidence": False,
            }
        ],
    )

    # Check a class & classification has been created
    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            f"http://testserver/api/v1/corpus/{CORPUS_ID}/classes/",
        ),
        ("POST", "http://testserver/api/v1/classification/bulk/"),
    ]

    assert json.loads(responses.calls[-2].request.body) == {"name": "a_class"}
    assert json.loads(responses.calls[-1].request.body) == {
        "parent": "12341234-1234-1234-1234-123412341234",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "classifications": [
            {
                "ml_class": "new-ml-class-1234",
                "confidence": 0.75,
                "high_confidence": False,
            }
        ],
    }


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_classifications(batch_size, responses, mock_elements_worker):
    mock_elements_worker.classes = {"portrait": "0000", "landscape": "1111"}
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/classification/bulk/",
        status=200,
        json={"classifications": []},
    )

    mock_elements_worker.create_classifications(
        element=elt,
        classifications=[
            {
                "ml_class": "portrait",
                "confidence": 0.75,
                "high_confidence": False,
            },
            {
                "ml_class": "landscape",
                "confidence": 0.25,
                "high_confidence": False,
            },
        ],
        batch_size=batch_size,
    )

    bulk_api_calls = [("POST", "http://testserver/api/v1/classification/bulk/")]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(("POST", "http://testserver/api/v1/classification/bulk/"))

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_cl = {"confidence": 0.75, "high_confidence": False, "ml_class": "0000"}
    second_cl = {"confidence": 0.25, "high_confidence": False, "ml_class": "1111"}
    empty_payload = {
        "parent": str(elt.id),
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "classifications": [],
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "classifications": [first_cl, second_cl]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "classifications": [first_cl]})
        bodies.append({**empty_payload, "classifications": [second_cl]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_classifications_with_cache(
    batch_size, responses, mock_elements_worker_with_cache
):
    mock_elements_worker_with_cache.classes = {"portrait": "0000", "landscape": "1111"}
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")

    if batch_size > 1:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/classification/bulk/",
            status=200,
            json={
                "parent": str(elt.id),
                "worker_run_id": "56785678-5678-5678-5678-567856785678",
                "classifications": [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "ml_class": "0000",
                        "confidence": 0.75,
                        "high_confidence": False,
                        "state": "pending",
                    },
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "ml_class": "1111",
                        "confidence": 0.25,
                        "high_confidence": False,
                        "state": "pending",
                    },
                ],
            },
        )
    else:
        for cl_id, cl_class, cl_conf in [
            ("00000000-0000-0000-0000-000000000000", "0000", 0.75),
            ("11111111-1111-1111-1111-111111111111", "1111", 0.25),
        ]:
            responses.add(
                responses.POST,
                "http://testserver/api/v1/classification/bulk/",
                status=200,
                json={
                    "parent": str(elt.id),
                    "worker_run_id": "56785678-5678-5678-5678-567856785678",
                    "classifications": [
                        {
                            "id": cl_id,
                            "ml_class": cl_class,
                            "confidence": cl_conf,
                            "high_confidence": False,
                            "state": "pending",
                        },
                    ],
                },
            )

    mock_elements_worker_with_cache.create_classifications(
        element=elt,
        classifications=[
            {
                "ml_class": "portrait",
                "confidence": 0.75,
                "high_confidence": False,
            },
            {
                "ml_class": "landscape",
                "confidence": 0.25,
                "high_confidence": False,
            },
        ],
        batch_size=batch_size,
    )

    bulk_api_calls = [("POST", "http://testserver/api/v1/classification/bulk/")]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(("POST", "http://testserver/api/v1/classification/bulk/"))

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_cl = {"confidence": 0.75, "high_confidence": False, "ml_class": "0000"}
    second_cl = {"confidence": 0.25, "high_confidence": False, "ml_class": "1111"}
    empty_payload = {
        "parent": str(elt.id),
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "classifications": [],
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "classifications": [first_cl, second_cl]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "classifications": [first_cl]})
        bodies.append({**empty_payload, "classifications": [second_cl]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    # Check that created classifications were properly stored in SQLite cache
    assert list(CachedClassification.select()) == [
        CachedClassification(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            element_id=UUID(elt.id),
            class_name="portrait",
            confidence=0.75,
            state="pending",
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
        CachedClassification(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            element_id=UUID(elt.id),
            class_name="landscape",
            confidence=0.25,
            state="pending",
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
    ]
