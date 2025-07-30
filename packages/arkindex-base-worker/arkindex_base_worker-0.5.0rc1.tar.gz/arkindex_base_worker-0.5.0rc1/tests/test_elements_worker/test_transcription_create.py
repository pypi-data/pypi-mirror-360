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


def test_create_transcription_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.create_transcription(
            element=None,
            text="i am a line",
            confidence=0.42,
        )

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be an Element or CachedElement",
    ):
        mock_elements_worker.create_transcription(
            element="not element type",
            text="i am a line",
            confidence=0.42,
        )


def test_create_transcription_wrong_text(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="text shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text=None,
            confidence=0.42,
        )

    with pytest.raises(
        AssertionError, match="text shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text=1234,
            confidence=0.42,
        )


def test_create_transcription_wrong_confidence(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            confidence=None,
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            confidence="wrong confidence",
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            confidence=0,
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            confidence=2.00,
        )


def test_create_transcription_default_orientation(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
        },
    )
    mock_elements_worker.create_transcription(
        element=elt,
        text="Animula vagula blandula",
        confidence=0.42,
    )
    assert json.loads(responses.calls[-1].request.body) == {
        "text": "Animula vagula blandula",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
        "orientation": "horizontal-lr",
    }


def test_create_transcription_orientation(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
        },
    )
    mock_elements_worker.create_transcription(
        element=elt,
        text="Animula vagula blandula",
        orientation=TextOrientation.VerticalLeftToRight,
        confidence=0.42,
    )
    assert json.loads(responses.calls[-1].request.body) == {
        "text": "Animula vagula blandula",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
        "orientation": "vertical-lr",
    }


def test_create_transcription_wrong_orientation(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    with pytest.raises(
        AssertionError,
        match="orientation shouldn't be null and should be of type TextOrientation",
    ):
        mock_elements_worker.create_transcription(
            element=elt,
            text="Animula vagula blandula",
            confidence=0.26,
            orientation="elliptical",
        )


def test_create_transcription_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_transcription(
            element=elt,
            text="i am a line",
            confidence=0.42,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/")
    ]


def test_create_transcription(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "i am a line",
            "confidence": 0.42,
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
        },
    )

    mock_elements_worker.create_transcription(
        element=elt,
        text="i am a line",
        confidence=0.42,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "text": "i am a line",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.42,
        "orientation": "horizontal-lr",
    }


def test_create_transcription_with_cache(responses, mock_elements_worker_with_cache):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")

    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "i am a line",
            "confidence": 0.42,
            "orientation": "horizontal-lr",
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
        },
    )

    mock_elements_worker_with_cache.create_transcription(
        element=elt,
        text="i am a line",
        confidence=0.42,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", f"http://testserver/api/v1/element/{elt.id}/transcription/"),
    ]

    assert json.loads(responses.calls[-1].request.body) == {
        "text": "i am a line",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "orientation": "horizontal-lr",
        "confidence": 0.42,
    }

    # Check that created transcription was properly stored in SQLite cache
    assert list(CachedTranscription.select()) == [
        CachedTranscription(
            id=UUID("56785678-5678-5678-5678-567856785678"),
            element_id=UUID(elt.id),
            text="i am a line",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_version_id=None,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
    ]


def test_create_transcription_orientation_with_cache(
    responses, mock_elements_worker_with_cache
):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")
    responses.add(
        responses.POST,
        f"http://testserver/api/v1/element/{elt.id}/transcription/",
        status=200,
        json={
            "id": "56785678-5678-5678-5678-567856785678",
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "orientation": "vertical-lr",
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
        },
    )
    mock_elements_worker_with_cache.create_transcription(
        element=elt,
        text="Animula vagula blandula",
        orientation=TextOrientation.VerticalLeftToRight,
        confidence=0.42,
    )
    assert json.loads(responses.calls[-1].request.body) == {
        "text": "Animula vagula blandula",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "orientation": "vertical-lr",
        "confidence": 0.42,
    }
    # Check that the text orientation was properly stored in SQLite cache
    assert list(map(model_to_dict, CachedTranscription.select())) == [
        {
            "id": UUID("56785678-5678-5678-5678-567856785678"),
            "element": {
                "id": UUID("12341234-1234-1234-1234-123412341234"),
                "parent_id": None,
                "type": "thing",
                "image": None,
                "polygon": None,
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
                "worker_run_id": None,
                "confidence": None,
            },
            "text": "Animula vagula blandula",
            "confidence": 0.42,
            "orientation": TextOrientation.VerticalLeftToRight.value,
            "worker_version_id": None,
            "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
        }
    ]


def test_create_transcriptions_wrong_transcriptions(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="transcriptions shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=None,
        )

    with pytest.raises(
        AssertionError,
        match="transcriptions shouldn't be null and should be of type list",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=1234,
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: element_id shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "text": "word",
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: element_id shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": None,
                    "text": "word",
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: element_id shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": 1234,
                    "text": "word",
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": None,
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: text shouldn't be null and should be of type str",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": 1234,
                    "confidence": 0.5,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
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
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "confidence": None,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "confidence": "a wrong confidence",
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "confidence": 0,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match=re.escape(
            "Transcription at index 1 in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
        ),
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "confidence": 2.00,
                },
            ],
        )

    with pytest.raises(
        AssertionError,
        match="Transcription at index 1 in transcriptions: orientation shouldn't be null and should be of type TextOrientation",
    ):
        mock_elements_worker.create_transcriptions(
            transcriptions=[
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "The",
                    "confidence": 0.75,
                },
                {
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "word",
                    "confidence": 0.28,
                    "orientation": "wobble",
                },
            ],
        )


def test_create_transcriptions_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/bulk/",
        status=418,
    )
    trans = [
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "The",
            "confidence": 0.75,
        },
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "word",
            "confidence": 0.42,
        },
    ]

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_transcriptions(transcriptions=trans)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/transcription/bulk/")]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_transcriptions(batch_size, responses, mock_elements_worker_with_cache):
    CachedElement.create(id="11111111-1111-1111-1111-111111111111", type="thing")
    transcriptions = [
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "The",
            "confidence": 0.75,
        },
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "word",
            "confidence": 0.42,
        },
    ]

    if batch_size > 1:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/transcription/bulk/",
            status=200,
            json={
                "worker_run_id": "56785678-5678-5678-5678-567856785678",
                "transcriptions": [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "element_id": "11111111-1111-1111-1111-111111111111",
                        "text": "The",
                        "orientation": "horizontal-lr",
                        "confidence": 0.75,
                    },
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "element_id": "11111111-1111-1111-1111-111111111111",
                        "text": "word",
                        "orientation": "horizontal-lr",
                        "confidence": 0.42,
                    },
                ],
            },
        )
    else:
        for tr, tr_id in zip(
            transcriptions,
            [
                "00000000-0000-0000-0000-000000000000",
                "11111111-1111-1111-1111-111111111111",
            ],
            strict=False,
        ):
            responses.add(
                responses.POST,
                "http://testserver/api/v1/transcription/bulk/",
                status=200,
                json={
                    "worker_run_id": "56785678-5678-5678-5678-567856785678",
                    "transcriptions": [
                        {
                            "id": tr_id,
                            "element_id": tr["element_id"],
                            "text": tr["text"],
                            "orientation": "horizontal-lr",
                            "confidence": tr["confidence"],
                        }
                    ],
                },
            )

    mock_elements_worker_with_cache.create_transcriptions(
        transcriptions=transcriptions,
        batch_size=batch_size,
    )

    bulk_api_calls = [
        (
            "POST",
            "http://testserver/api/v1/transcription/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                "http://testserver/api/v1/transcription/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_tr = {
        **transcriptions[0],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    second_tr = {
        **transcriptions[1],
        "orientation": TextOrientation.HorizontalLeftToRight.value,
    }
    empty_payload = {
        "transcriptions": [],
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "transcriptions": [first_tr, second_tr]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "transcriptions": [first_tr]})
        bodies.append({**empty_payload, "transcriptions": [second_tr]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    # Check that created transcriptions were properly stored in SQLite cache
    assert list(CachedTranscription.select()) == [
        CachedTranscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="The",
            confidence=0.75,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
        CachedTranscription(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            element_id=UUID("11111111-1111-1111-1111-111111111111"),
            text="word",
            confidence=0.42,
            orientation=TextOrientation.HorizontalLeftToRight,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        ),
    ]


def test_create_transcriptions_orientation(responses, mock_elements_worker_with_cache):
    CachedElement.create(id="11111111-1111-1111-1111-111111111111", type="thing")
    trans = [
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "Animula vagula blandula",
            "confidence": 0.12,
            "orientation": TextOrientation.HorizontalRightToLeft,
        },
        {
            "element_id": "11111111-1111-1111-1111-111111111111",
            "text": "Hospes comesque corporis",
            "confidence": 0.21,
            "orientation": TextOrientation.VerticalLeftToRight,
        },
    ]

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/bulk/",
        status=200,
        json={
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "transcriptions": [
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "Animula vagula blandula",
                    "orientation": "horizontal-rl",
                    "confidence": 0.12,
                },
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element_id": "11111111-1111-1111-1111-111111111111",
                    "text": "Hospes comesque corporis",
                    "orientation": "vertical-lr",
                    "confidence": 0.21,
                },
            ],
        },
    )

    mock_elements_worker_with_cache.create_transcriptions(
        transcriptions=trans,
    )

    assert json.loads(responses.calls[-1].request.body) == {
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "transcriptions": [
            {
                "element_id": "11111111-1111-1111-1111-111111111111",
                "text": "Animula vagula blandula",
                "confidence": 0.12,
                "orientation": TextOrientation.HorizontalRightToLeft.value,
            },
            {
                "element_id": "11111111-1111-1111-1111-111111111111",
                "text": "Hospes comesque corporis",
                "confidence": 0.21,
                "orientation": TextOrientation.VerticalLeftToRight.value,
            },
        ],
    }

    # Check that oriented transcriptions were properly stored in SQLite cache
    assert list(map(model_to_dict, CachedTranscription.select())) == [
        {
            "id": UUID("00000000-0000-0000-0000-000000000000"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": None,
                "type": "thing",
                "image": None,
                "polygon": None,
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
                "worker_run_id": None,
                "confidence": None,
            },
            "text": "Animula vagula blandula",
            "confidence": 0.12,
            "orientation": TextOrientation.HorizontalRightToLeft.value,
            "worker_version_id": None,
            "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
        },
        {
            "id": UUID("11111111-1111-1111-1111-111111111111"),
            "element": {
                "id": UUID("11111111-1111-1111-1111-111111111111"),
                "parent_id": None,
                "type": "thing",
                "image": None,
                "polygon": None,
                "rotation_angle": 0,
                "mirrored": False,
                "initial": False,
                "worker_version_id": None,
                "worker_run_id": None,
                "confidence": None,
            },
            "text": "Hospes comesque corporis",
            "confidence": 0.21,
            "orientation": TextOrientation.VerticalLeftToRight.value,
            "worker_version_id": None,
            "worker_run_id": UUID("56785678-5678-5678-5678-567856785678"),
        },
    ]
