import json
import re
from uuid import UUID

import pytest
from responses import matchers

from arkindex.exceptions import ErrorResponse
from arkindex_worker.cache import (
    CachedElement,
    CachedTranscription,
    CachedTranscriptionEntity,
)
from arkindex_worker.models import Transcription
from arkindex_worker.worker.entity import MissingEntityType
from arkindex_worker.worker.transcription import TextOrientation
from tests import CORPUS_ID

from . import BASE_API_CALLS


def test_create_entity_type_wrong_name(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity_type(name=None)

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_entity_type(name=1234)


def test_create_entity_type_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_entity_type(name="firstname")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/entity/types/")]


def test_create_entity_type_already_exists(responses, mock_elements_worker):
    assert mock_elements_worker.entity_types == {}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=400,
        match=[
            matchers.json_params_matcher({"name": "firstname", "corpus": CORPUS_ID})
        ],
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/entity-types/",
        status=200,
        json={
            "count": 1,
            "next": None,
            "results": [
                {"id": "lastname-id", "name": "lastname", "color": "ffd1b3"},
                {"id": "firstname-id", "name": "firstname", "color": "ffd1b3"},
            ],
        },
    )

    mock_elements_worker.create_entity_type(name="firstname")

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/entity/types/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/entity-types/"),
    ]

    # Make sure the entity_types attribute has been updated
    assert mock_elements_worker.entity_types == {
        "lastname": "lastname-id",
        "firstname": "firstname-id",
    }


def test_create_entity_type(responses, mock_elements_worker):
    assert mock_elements_worker.entity_types == {}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=200,
        match=[
            matchers.json_params_matcher({"name": "firstname", "corpus": CORPUS_ID})
        ],
        json={
            "id": "firstname-id",
            "name": "firstname",
            "corpus": CORPUS_ID,
            "color": "ffd1b3",
        },
    )

    mock_elements_worker.create_entity_type(name="firstname")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/entity/types/"),
    ]

    # Make sure the entity_types attribute has been updated
    assert mock_elements_worker.entity_types == {"firstname": "firstname-id"}


def test_check_required_entity_types_wrong_entity_types(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="entity_types shouldn't be null and should be of type list",
    ):
        mock_elements_worker.check_required_entity_types(entity_types=None)

    with pytest.raises(
        AssertionError,
        match="entity_types shouldn't be null and should be of type list",
    ):
        mock_elements_worker.check_required_entity_types(entity_types=1234)

    with pytest.raises(
        AssertionError,
        match="Entity type at index 1 in entity_types: Should be of type str",
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["firstname", 1234]
        )


def test_check_required_entity_types_wrong_create_missing(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="create_missing shouldn't be null and should be of type bool",
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["firstname"], create_missing=None
        )

    with pytest.raises(
        AssertionError,
        match="create_missing shouldn't be null and should be of type bool",
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["firstname"], create_missing=1234
        )


def test_check_required_entity_types_do_not_create_missing(
    responses, mock_elements_worker
):
    # Set one entity type
    mock_elements_worker.entity_types = {"lastname": "lastname-id"}

    with pytest.raises(
        MissingEntityType, match="Entity type `firstname` was not in the corpus."
    ):
        mock_elements_worker.check_required_entity_types(
            entity_types=["lastname", "firstname"], create_missing=False
        )

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_check_required_entity_types(responses, mock_elements_worker):
    # Set one entity type
    mock_elements_worker.entity_types = {"lastname": "lastname-id"}

    # Call to create a new entity type
    responses.add(
        responses.POST,
        "http://testserver/api/v1/entity/types/",
        status=200,
        match=[
            matchers.json_params_matcher({"name": "firstname", "corpus": CORPUS_ID})
        ],
        json={
            "id": "firstname-id",
            "name": "firstname",
            "corpus": CORPUS_ID,
            "color": "ffd1b3",
        },
    )

    mock_elements_worker.check_required_entity_types(
        entity_types=["lastname", "firstname"], create_missing=True
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/entity/types/",
        ),
    ]

    # Make sure the entity_types attribute has been updated
    assert mock_elements_worker.entity_types == {
        "lastname": "lastname-id",
        "firstname": "firstname-id",
    }


def test_create_transcription_entity_wrong_transcription(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="transcription shouldn't be null and should be a Transcription",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=None,
            type_id="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=10,
        )

    with pytest.raises(
        AssertionError,
        match="transcription shouldn't be null and should be a Transcription",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=1234,
            type_id="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=10,
        )


def test_create_transcription_entity_wrong_type_id(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="type_id shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id=None,
            offset=5,
            length=10,
        )

    with pytest.raises(
        AssertionError, match="type_id shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id=1234,
            offset=5,
            length=10,
        )


def test_create_transcription_entity_wrong_offset(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="offset shouldn't be null and should be a positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset=None,
            length=10,
        )

    with pytest.raises(
        AssertionError,
        match="offset shouldn't be null and should be a positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset="not an int",
            length=10,
        )

    with pytest.raises(
        AssertionError,
        match="offset shouldn't be null and should be a positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset=-1,
            length=10,
        )


def test_create_transcription_entity_wrong_length(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="length shouldn't be null and should be a strictly positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=None,
        )

    with pytest.raises(
        AssertionError,
        match="length shouldn't be null and should be a strictly positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset=5,
            length="not an int",
        )

    with pytest.raises(
        AssertionError,
        match="length shouldn't be null and should be a strictly positive integer",
    ):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=0,
        )


def test_create_transcription_entity_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_transcription_entity(
            transcription=Transcription(
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "element": {"id": "myelement"},
                }
            ),
            type_id="11111111-1111-1111-1111-111111111111",
            offset=5,
            length=10,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        )
    ]


def test_create_transcription_entity_no_confidence(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        status=200,
        json={
            "type": {"id": "11111111-1111-1111-1111-111111111111"},
            "offset": 5,
            "length": 10,
        },
    )

    mock_elements_worker.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        type_id="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type_id": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }


def test_create_transcription_entity_with_confidence(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        status=200,
        json={
            "type": {"id": "11111111-1111-1111-1111-111111111111"},
            "offset": 5,
            "length": 10,
            "confidence": 0.33,
        },
    )

    mock_elements_worker.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        type_id="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
        confidence=0.33,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type_id": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.33,
    }


def test_create_transcription_entity_confidence_none(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        status=200,
        json={
            "type": {"id": "11111111-1111-1111-1111-111111111111"},
            "offset": 5,
            "length": 10,
            "confidence": None,
        },
    )

    mock_elements_worker.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        type_id="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
        confidence=None,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type_id": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }


def test_create_transcription_entity_with_cache(
    responses, mock_elements_worker_with_cache
):
    CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="page",
    )
    CachedTranscription.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        element=UUID("12341234-1234-1234-1234-123412341234"),
        text="Hello, it's me.",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        status=200,
        json={
            "type": {"id": "11111111-1111-1111-1111-111111111111", "name": "Whatever"},
            "offset": 5,
            "length": 10,
        },
    )

    mock_elements_worker_with_cache.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        type_id="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type_id": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    # Check that created transcription entity was properly stored in SQLite cache
    assert list(CachedTranscriptionEntity.select()) == [
        CachedTranscriptionEntity(
            transcription=UUID("11111111-1111-1111-1111-111111111111"),
            type="Whatever",
            offset=5,
            length=10,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
        )
    ]


def test_create_transcription_entity_with_confidence_with_cache(
    responses, mock_elements_worker_with_cache
):
    CachedElement.create(
        id=UUID("12341234-1234-1234-1234-123412341234"),
        type="page",
    )
    CachedTranscription.create(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        element=UUID("12341234-1234-1234-1234-123412341234"),
        text="Hello, it's me.",
        confidence=0.42,
        orientation=TextOrientation.HorizontalLeftToRight,
        worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
    )

    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        status=200,
        json={
            "type": {"id": "11111111-1111-1111-1111-111111111111", "name": "Whatever"},
            "offset": 5,
            "length": 10,
            "confidence": 0.77,
        },
    )

    mock_elements_worker_with_cache.create_transcription_entity(
        transcription=Transcription(
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "element": {"id": "myelement"},
            }
        ),
        type_id="11111111-1111-1111-1111-111111111111",
        offset=5,
        length=10,
        confidence=0.77,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/11111111-1111-1111-1111-111111111111/entities/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type_id": "11111111-1111-1111-1111-111111111111",
        "offset": 5,
        "length": 10,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "confidence": 0.77,
    }

    # Check that created transcription entity was properly stored in SQLite cache
    assert list(CachedTranscriptionEntity.select()) == [
        CachedTranscriptionEntity(
            transcription=UUID("11111111-1111-1111-1111-111111111111"),
            type="Whatever",
            offset=5,
            length=10,
            worker_run_id=UUID("56785678-5678-5678-5678-567856785678"),
            confidence=0.77,
        )
    ]


@pytest.mark.parametrize("transcription", [None, "not a transcription", 1])
def test_create_transcription_entities_wrong_transcription(
    mock_elements_worker, transcription
):
    with pytest.raises(
        AssertionError,
        match="transcription shouldn't be null and should be of type Transcription",
    ):
        mock_elements_worker.create_transcription_entities(
            transcription=transcription,
            entities=[],
        )


@pytest.mark.parametrize(
    ("entities", "error"),
    [
        (None, "entities shouldn't be null and should be of type list"),
        (
            "not a list of entities",
            "entities shouldn't be null and should be of type list",
        ),
        (1, "entities shouldn't be null and should be of type list"),
        (
            [
                {
                    "type_id": "12341234-1234-1234-1234-123412341234",
                    "offset": 0,
                    "length": 1,
                    "confidence": 0.5,
                }
            ]
            * 2,
            "entities should be unique",
        ),
    ],
)
def test_create_transcription_entities_wrong_entities(
    mock_elements_worker, entities, error
):
    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.create_transcription_entities(
            transcription=Transcription(id="transcription_id"),
            entities=entities,
        )


def test_create_transcription_entities_wrong_entities_subtype(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="Entity at index 0 in entities: Should be of type dict"
    ):
        mock_elements_worker.create_transcription_entities(
            transcription=Transcription(id="transcription_id"),
            entities=["not a dict"],
        )


@pytest.mark.parametrize(
    ("entity", "error"),
    [
        (
            {"type_id": None, "offset": 0, "length": 1, "confidence": 0.5},
            "Entity at index 0 in entities: type_id shouldn't be null and should be of type str",
        ),
        (
            {"type_id": 0, "offset": 0, "length": 1, "confidence": 0.5},
            "Entity at index 0 in entities: type_id shouldn't be null and should be of type str",
        ),
        (
            {
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": None,
                "length": 1,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: offset shouldn't be null and should be a positive integer",
        ),
        (
            {
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": -2,
                "length": 1,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: offset shouldn't be null and should be a positive integer",
        ),
        (
            {
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": None,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: length shouldn't be null and should be a strictly positive integer",
        ),
        (
            {
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 0,
                "confidence": 0.5,
            },
            "Entity at index 0 in entities: length shouldn't be null and should be a strictly positive integer",
        ),
        (
            {
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 1,
                "confidence": "not None or a float",
            },
            "Entity at index 0 in entities: confidence should be None or a float in [0..1] range",
        ),
        (
            {
                "type_id": "12341234-1234-1234-1234-123412341234",
                "offset": 0,
                "length": 1,
                "confidence": 1.3,
            },
            "Entity at index 0 in entities: confidence should be None or a float in [0..1] range",
        ),
    ],
)
def test_create_transcription_entities_wrong_entity(
    mock_elements_worker, entity, error
):
    with pytest.raises(AssertionError, match=re.escape(error)):
        mock_elements_worker.create_transcription_entities(
            transcription=Transcription(id="transcription_id"),
            entities=[entity],
        )


def test_create_transcription_entities(responses, mock_elements_worker):
    transcription = Transcription(id="transcription-id")

    # Call to Transcription entities creation in bulk
    responses.add(
        responses.POST,
        "http://testserver/api/v1/transcription/transcription-id/entities/bulk/",
        status=201,
        match=[
            matchers.json_params_matcher(
                {
                    "worker_run_id": "56785678-5678-5678-5678-567856785678",
                    "transcription_entities": [
                        {
                            "type_id": "22222222-2222-2222-2222-222222222222",
                            "offset": 0,
                            "length": 6,
                            "confidence": 1.0,
                        },
                        {
                            "type_id": "22222222-2222-2222-2222-222222222222",
                            "offset": 7,
                            "length": 11,
                            "confidence": 1.0,
                        },
                    ],
                }
            )
        ],
        json={"transcription_entities": ["transc-entity-id", "transc-entity-id"]},
    )

    # Store entity type/slug correspondence on the worker
    mock_elements_worker.entity_types = {
        "22222222-2222-2222-2222-222222222222": "organization"
    }
    created_objects = mock_elements_worker.create_transcription_entities(
        transcription=transcription,
        entities=[
            {
                "type_id": "22222222-2222-2222-2222-222222222222",
                "offset": 0,
                "length": 6,
                "confidence": 1.0,
            },
            {
                "type_id": "22222222-2222-2222-2222-222222222222",
                "offset": 7,
                "length": 11,
                "confidence": 1.0,
            },
        ],
    )

    assert len(created_objects) == 2

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/transcription/transcription-id/entities/bulk/",
        )
    ]


def test_list_transcription_entities_deprecation(fake_dummy_worker):
    transcription = Transcription({"id": "fake_transcription_id"})
    worker_version = "worker_version_id"
    fake_dummy_worker.api_client.add_response(
        "ListTranscriptionEntities",
        id=transcription.id,
        worker_version=worker_version,
        response={"id": "entity_id"},
    )
    with pytest.deprecated_call(
        match="`worker_version` usage is deprecated. Consider using `worker_run` instead."
    ):
        assert fake_dummy_worker.list_transcription_entities(
            transcription, worker_version=worker_version
        ) == {"id": "entity_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_transcription_entities(fake_dummy_worker):
    transcription = Transcription({"id": "fake_transcription_id"})
    worker_run = "worker_run_id"
    fake_dummy_worker.api_client.add_response(
        "ListTranscriptionEntities",
        id=transcription.id,
        worker_run=worker_run,
        response={"id": "entity_id"},
    )
    assert fake_dummy_worker.list_transcription_entities(
        transcription, worker_run=worker_run
    ) == {"id": "entity_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0
