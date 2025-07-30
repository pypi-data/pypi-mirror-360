import json
import re
from uuid import UUID

import pytest
from playhouse.shortcuts import model_to_dict

from arkindex.exceptions import ErrorResponse
from arkindex_worker.cache import CachedElement, CachedTranscription
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE
from arkindex_worker.worker.transcription import TextOrientation

from . import BASE_API_CALLS

TRANSCRIPTIONS_SAMPLE = [
    {
        "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
        "confidence": 0.5,
        "text": "The",
    },
    {
        "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
        "confidence": 0.75,
        "text": "first",
        "element_confidence": 0.75,
    },
    {
        "polygon": [[1000, 300], [1200, 300], [1200, 500], [1000, 500]],
        "confidence": 0.9,
        "text": "line",
    },
]


def test_create_element_transcriptions_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=None,
            sub_element_type="page",
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.create_element_transcriptions(
            element="not element type",
            sub_element_type="page",
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )


def test_create_element_transcriptions_wrong_sub_element_type(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(
        AssertionError,
        match="sub_element_type shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type=None,
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )

    with pytest.raises(
        AssertionError,
        match="sub_element_type shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type=1234,
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )


def test_create_element_transcriptions_wrong_transcriptions(mock_elements_worker):
    elt = Element({"zone": None})

    with pytest.raises(
        AssertionError,
        match="transcriptions shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=None,
        )

    with pytest.raises(
        AssertionError,
        match="transcriptions shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=1234,
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 0.5,
                    "text": None,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 0.5,
                    "text": 1234,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": None,
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": "a wrong confidence",
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 0,
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 2.00,
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {"confidence": 0.5, "text": "word"},
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {"polygon": None, "confidence": 0.5, "text": "word"},
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {"polygon": "not a polygon", "confidence": 0.5, "text": "word"},
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon should have at least three points",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {"polygon": [[1, 1], [2, 2]], "confidence": 0.5, "text": "word"},
            ],
        )
    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon points should be lists of two items",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]],
                    "confidence": 0.5,
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon points should be lists of two items",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {"polygon": [[1], [2], [2], [1]], "confidence": 0.5, "text": "word"},
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: polygon points should be lists of two numbers",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]],
                    "confidence": 0.5,
                    "text": "word",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: orientation shouldn't be null and should be of type TextOrientation",
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 0.35,
                    "text": "word",
                    "orientation": "uptown",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: element_confidence should be either null or a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=[
                {
                    "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                    "confidence": 0.75,
                    "text": "The",
                },
                {
                    "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                    "confidence": 0.75,
                    "text": "word",
                    "element_confidence": "not a confidence",
                },
            ],
        )


def test_create_element_transcriptions_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_element_transcriptions(
            element=elt,
            sub_element_type="page",
            transcriptions=TRANSCRIPTIONS_SAMPLE,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/")
    ]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 2])
def test_create_element_transcriptions(batch_size, responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    if batch_size > 2:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
            status=200,
            json=[
                {
                    "id": "56785678-5678-5678-5678-567856785678",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "created": True,
                },
                {
                    "id": "67896789-6789-6789-6789-678967896789",
                    "element_id": "22222222-2222-2222-2222-222222222222",
                    "created": False,
                },
                {
                    "id": "78907890-7890-7890-7890-789078907890",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "created": True,
                },
            ],
        )
    else:
        for transcriptions in [
            [
                ("56785678-5678-5678-5678-567856785678", True),
                ("67896789-6789-6789-6789-678967896789", False),
            ],
            [("78907890-7890-7890-7890-789078907890", True)],
        ]:
            responses.add(
                responses.POST,
                f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
                status=200,
                json=[
                    {
                        "id": tr_id,
                        "element_id": "11111111-1111-1111-1111-111111111111"
                        if created
                        else "22222222-2222-2222-2222-222222222222",
                        "created": created,
                    }
                    for tr_id, created in transcriptions
                ],
            )

    annotations = mock_elements_worker.create_element_transcriptions(
        element=elt,
        sub_element_type="page",
        transcriptions=TRANSCRIPTIONS_SAMPLE,
        batch_size=batch_size,
    )

    bulk_api_calls = [
        (
            "POST",
            f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_tr = {
        **TRANSCRIPTIONS_SAMPLE[0],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    second_tr = {
        **TRANSCRIPTIONS_SAMPLE[1],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    third_tr = {
        **TRANSCRIPTIONS_SAMPLE[2],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    empty_payload = {
        "element_type": "page",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "transcriptions": [],
        "return_elements": True,
    }

    bodies = []
    first_call_idx = None
    if batch_size > 2:
        first_call_idx = -1
        bodies.append(
            {**empty_payload, "transcriptions": [first_tr, second_tr, third_tr]}
        )
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "transcriptions": [first_tr, second_tr]})
        bodies.append({**empty_payload, "transcriptions": [third_tr]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    assert annotations == [
        {
            "id": "56785678-5678-5678-5678-567856785678",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
        {
            "id": "67896789-6789-6789-6789-678967896789",
            "element_id": "22222222-2222-2222-2222-222222222222",
            "created": False,
        },
        {
            "id": "78907890-7890-7890-7890-789078907890",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
    ]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 2])
def test_create_element_transcriptions_with_cache(
    batch_size, responses, mock_elements_worker_with_cache
):
    elt = CachedElement(id="12341234-1234-1234-1234-123412341234", type="thing")

    if batch_size > 2:
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
            status=200,
            json=[
                {
                    "id": "56785678-5678-5678-5678-567856785678",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "created": True,
                },
                {
                    "id": "67896789-6789-6789-6789-678967896789",
                    "element_id": "22222222-2222-2222-2222-222222222222",
                    "created": False,
                },
                {
                    "id": "78907890-7890-7890-7890-789078907890",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "created": True,
                },
            ],
        )
    else:
        for transcriptions in [
            [
                ("56785678-5678-5678-5678-567856785678", True),
                ("67896789-6789-6789-6789-678967896789", False),
            ],
            [("78907890-7890-7890-7890-789078907890", True)],
        ]:
            responses.add(
                responses.POST,
                f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
                status=200,
                json=[
                    {
                        "id": tr_id,
                        "element_id": "11111111-1111-1111-1111-111111111111"
                        if created
                        else "22222222-2222-2222-2222-222222222222",
                        "created": created,
                    }
                    for tr_id, created in transcriptions
                ],
            )

    annotations = mock_elements_worker_with_cache.create_element_transcriptions(
        element=elt,
        sub_element_type="page",
        transcriptions=TRANSCRIPTIONS_SAMPLE,
        batch_size=batch_size,
    )

    bulk_api_calls = [
        (
            "POST",
            f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_tr = {
        **TRANSCRIPTIONS_SAMPLE[0],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    second_tr = {
        **TRANSCRIPTIONS_SAMPLE[1],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
        "element_confidence": 0.75,
    }
    third_tr = {
        **TRANSCRIPTIONS_SAMPLE[2],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    empty_payload = {
        "element_type": "page",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "transcriptions": [],
        "return_elements": True,
    }

    bodies = []
    first_call_idx = None
    if batch_size > 2:
        first_call_idx = -1
        bodies.append(
            {**empty_payload, "transcriptions": [first_tr, second_tr, third_tr]}
        )
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "transcriptions": [first_tr, second_tr]})
        bodies.append({**empty_payload, "transcriptions": [third_tr]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    assert annotations == [
        {
            "id": "56785678-5678-5678-5678-567856785678",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
        {
            "id": "67896789-6789-6789-6789-678967896789",
            "element_id": "22222222-2222-2222-2222-222222222222",
            "created": False,
        },
        {
            "id": "78907890-7890-7890-7890-789078907890",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
    ]

    # Check that created transcriptions and elements were properly stored in SQLite cache
    assert list(CachedElement.select()) == [
        CachedElement(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="page",
            polygon="[[100, 150], [700, 150], [700, 200], [100, 200]]",
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
        CachedElement(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            parent_id=UUID("12341234-1234-1234-1234-123412341234"),
            type="page",
            polygon="[[0, 0], [2000, 0], [2000, 3000], [0, 3000]]",
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=0.75,
        ),
    ]
    assert list(CachedTranscription.select()) == [
        CachedTranscription(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="The",
            confidence=0.5,
            orientation=TextOrientation.HorizontalLeftToRight.value,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
        CachedTranscription(
            id=UUID("67896789-6789-6789-6789-678967896789"),
            element_id=UUID("22222222-2222-2222-2222-222222222222"),
            text="first",
            confidence=0.75,
            orientation=TextOrientation.HorizontalLeftToRight.value,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
        CachedTranscription(
            id=UUID("78907890-7890-7890-7890-789078907890"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="line",
            confidence=0.9,
            orientation=TextOrientation.HorizontalLeftToRight.value,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
    ]


def test_create_element_transcriptions_orientation_with_cache(
    responses, mock_elements_worker_with_cache
):
    elt = CachedElement(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcriptions/bulk/",
        status=200,
        json=[
            {
                "id": "56785678-5678-5678-5678-567856785678",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
            {
                "id": "67896789-6789-6789-6789-678967896789",
                "element_id": "22222222-2222-2222-2222-222222222222",
                "created": False,
            },
            {
                "id": "78907890-7890-7890-7890-789078907890",
                "element_id": "11111111-1111-1111-1111-111111111111",
                "created": True,
            },
        ],
    )

    oriented_transcriptions = [
        {
            "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
            "confidence": 0.5,
            "text": "Animula vagula blandula",
        },
        {
            "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
            "confidence": 0.75,
            "text": "Hospes comesque corporis",
            "orientation": TextOrientation.VerticalLeftToRight,
        },
        {
            "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
            "confidence": 0.9,
            "text": "Quae nunc abibis in loca",
            "orientation": TextOrientation.HorizontalRightToLeft,
        },
    ]

    annotations = mock_elements_worker_with_cache.create_element_transcriptions(
        element=elt,
        sub_element_type="page",
        transcriptions=oriented_transcriptions,
    )

    assert json.loads(responses.calls[-1].request.body) == {
        "element_type": "page",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "transcriptions": [
            {
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "confidence": 0.5,
                "text": "Animula vagula blandula",
                "orientation": TextOrientation.HorizontalLeftToRight.value,
            },
            {
                "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                "confidence": 0.75,
                "text": "Hospes comesque corporis",
                "orientation": TextOrientation.VerticalLeftToRight.value,
            },
            {
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "confidence": 0.9,
                "text": "Quae nunc abibis in loca",
                "orientation": TextOrientation.HorizontalRightToLeft.value,
            },
        ],
        "return_elements": True,
    }
    assert annotations == [
        {
            "id": "56785678-5678-5678-5678-567856785678",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
        {
            "id": "67896789-6789-6789-6789-678967896789",
            "element_id": "22222222-2222-2222-2222-222222222222",
            "created": False,
        },
        {
            "id": "78907890-7890-7890-7890-789078907890",
            "element_id": "11111111-1111-1111-1111-111111111111",
            "created": True,
        },
    ]

    # Check that the text orientation was properly stored in SQLite cache
    assert list(map(model_to_dict, CachedTranscription.select())) == [
        {
            "id": UUID("56785678-5678-5678-5678-567856785678"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": UUID(elt.id),
                "type": "page",
                "image": None,
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
                "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
                "confidence": None,
            },
            "text": "Animula vagula blandula",
            "confidence": 0.5,
            "orientation": TextOrientation.HorizontalLeftToRight.value,
            "worker_version_id": None,
            "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
        },
        {
            "id": UUID("67896789-6789-6789-6789-678967896789"),
            "element": {
                "id": UUID("22222222-2222-2222-2222-222222222222"),
                "parent_id": UUID(elt.id),
                "type": "page",
                "image": None,
                "polygon": [[0, 0], [2000, 0], [2000, 3000], [0, 3000]],
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
                "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
                "confidence": None,
            },
            "text": "Hospes comesque corporis",
            "confidence": 0.75,
            "orientation": TextOrientation.VerticalLeftToRight.value,
            "worker_version_id": None,
            "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
        },
        {
            "id": UUID("78907890-7890-7890-7890-789078907890"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": UUID(elt.id),
                "type": "page",
                "image": None,
                "polygon": [[100, 150], [700, 150], [700, 200], [100, 200]],
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
                "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
                "confidence": None,
            },
            "text": "Quae nunc abibis in loca",
            "confidence": 0.9,
            "orientation": TextOrientation.HorizontalRightToLeft.value,
            "worker_version_id": None,
            "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
        },
    ]
