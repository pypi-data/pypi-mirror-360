import json
import re

import pytest
from responses import matchers

from arkindex.exceptions import ErrorResponse
from arkindex_worker.cache import (
    CachedElement,
    CachedImage,
)
from arkindex_worker.models import Element
from arkindex_worker.worker.element import MissingElementType
from tests import CORPUS_ID

from . import BASE_API_CALLS


def test_list_corpus_types(responses, mock_elements_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/",
        json={
            "id": CORPUS_ID,
            "types": [{"slug": "folder"}, {"slug": "page"}],
        },
    )

    mock_elements_worker.list_corpus_types()

    assert mock_elements_worker.corpus_types == {
        "folder": {"slug": "folder"},
        "page": {"slug": "page"},
    }


def test_create_element_type_wrong_slug(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="slug shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_element_type(slug=None, name="page")

    with pytest.raises(
        AssertionError, match="slug shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_element_type(slug=1234, name="page")


def test_create_element_type_wrong_name(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_element_type(slug="page", name=None)

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_element_type(slug="page", name=1234)


def test_create_element_type_wrong_is_folder(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="is_folder shouldn't be null and should be of type bool"
    ):
        mock_elements_worker.create_element_type(
            slug="page", name="page", is_folder=None
        )

    with pytest.raises(
        AssertionError, match="is_folder shouldn't be null and should be of type bool"
    ):
        mock_elements_worker.create_element_type(
            slug="page", name="page", is_folder=1234
        )


def test_create_element_type_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/type/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_element_type(slug="page", name="page")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/elements/type/")]


def test_create_element_type_already_exists(responses, mock_elements_worker):
    assert mock_elements_worker.corpus_types == {}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/type/",
        status=400,
        match=[
            matchers.json_params_matcher(
                {
                    "slug": "page",
                    "display_name": "page",
                    "folder": False,
                    "corpus": CORPUS_ID,
                }
            )
        ],
    )
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/corpus/{CORPUS_ID}/",
        status=200,
        json={
            "id": CORPUS_ID,
            "types": [{"slug": "folder"}, {"slug": "page"}],
        },
    )

    mock_elements_worker.create_element_type(slug="page", name="page")

    assert len(responses.calls) == len(BASE_API_CALLS) + 2
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/elements/type/"),
        ("GET", f"http://testserver/api/v1/corpus/{CORPUS_ID}/"),
    ]

    # Make sure the corpus_types attribute has been updated
    assert mock_elements_worker.corpus_types == {
        "folder": {"slug": "folder"},
        "page": {"slug": "page"},
    }


def test_create_element_type(responses, mock_elements_worker):
    assert mock_elements_worker.corpus_types == {}

    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/type/",
        status=200,
        match=[
            matchers.json_params_matcher(
                {
                    "slug": "page",
                    "display_name": "page",
                    "folder": False,
                    "corpus": CORPUS_ID,
                }
            )
        ],
        json={"id": "page-id", "slug": "page", "display_name": "page", "folder": False},
    )

    mock_elements_worker.create_element_type(slug="page", name="page")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("POST", "http://testserver/api/v1/elements/type/"),
    ]

    # Make sure the corpus_types attribute has been updated
    assert mock_elements_worker.corpus_types == {
        "page": {
            "id": "page-id",
            "slug": "page",
            "display_name": "page",
            "folder": False,
        }
    }


def test_check_required_types_wrong_type_slugs(mock_elements_worker):
    with pytest.raises(
        AssertionError, match="type_slugs shouldn't be null and should be of type list"
    ):
        mock_elements_worker.check_required_types(type_slugs=None)

    with pytest.raises(
        AssertionError, match="type_slugs shouldn't be null and should be of type list"
    ):
        mock_elements_worker.check_required_types(type_slugs=1234)

    with pytest.raises(
        AssertionError,
        match="Element type at index 1 in type_slugs: Should be of type str",
    ):
        mock_elements_worker.check_required_types(type_slugs=["page", 1234])


def test_check_required_types_wrong_create_missing(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="create_missing shouldn't be null and should be of type bool",
    ):
        mock_elements_worker.check_required_types(
            type_slugs=["page"], create_missing=None
        )

    with pytest.raises(
        AssertionError,
        match="create_missing shouldn't be null and should be of type bool",
    ):
        mock_elements_worker.check_required_types(
            type_slugs=["page"], create_missing=1234
        )


def test_check_required_types_do_not_create_missing(responses, mock_elements_worker):
    # Set one element type
    mock_elements_worker.corpus_types = {"folder": {"slug": "folder"}}

    with pytest.raises(
        MissingElementType, match="Element type `page` was not in the corpus."
    ):
        mock_elements_worker.check_required_types(
            type_slugs=["folder", "page"], create_missing=False
        )

    assert len(responses.calls) == len(BASE_API_CALLS)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS


def test_check_required_types(responses, mock_elements_worker):
    # Set one element type
    mock_elements_worker.corpus_types = {"folder": {"slug": "folder"}}

    # Call to create a new element type
    responses.add(
        responses.POST,
        "http://testserver/api/v1/elements/type/",
        status=200,
        match=[
            matchers.json_params_matcher(
                {
                    "slug": "page",
                    "display_name": "page",
                    "folder": False,
                    "corpus": CORPUS_ID,
                }
            )
        ],
        json={"id": "page-id", "slug": "page", "display_name": "page", "folder": False},
    )

    mock_elements_worker.check_required_types(
        type_slugs=["folder", "page"], create_missing=True
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/elements/type/",
        ),
    ]

    # Make sure the element_types attribute has been updated
    assert mock_elements_worker.corpus_types == {
        "folder": {"slug": "folder"},
        "page": {
            "id": "page-id",
            "slug": "page",
            "display_name": "page",
            "folder": False,
        },
    }


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Element
        (
            {"element": None},
            "element shouldn't be null and should be an Element or CachedElement",
        ),
        (
            {"element": "not element type"},
            "element shouldn't be null and should be an Element or CachedElement",
        ),
    ],
)
def test_partial_update_element_wrong_param_element(
    mock_elements_worker, payload, error
):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Type
        ({"type": 1234}, "type should be a str"),
        ({"type": None}, "type should be a str"),
    ],
)
def test_partial_update_element_wrong_param_type(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Name
        ({"name": 1234}, "name should be a str"),
        ({"name": None}, "name should be a str"),
    ],
)
def test_partial_update_element_wrong_param_name(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Polygon
        ({"polygon": "not a polygon"}, "polygon should be a list"),
        ({"polygon": None}, "polygon should be a list"),
        ({"polygon": [[1, 1], [2, 2]]}, "polygon should have at least three points"),
        (
            {"polygon": [[1, 1, 1], [2, 2, 1], [2, 1, 1], [1, 2, 1]]},
            "polygon points should be lists of two items",
        ),
        (
            {"polygon": [[1], [2], [2], [1]]},
            "polygon points should be lists of two items",
        ),
        (
            {"polygon": [["not a coord", 1], [2, 2], [2, 1], [1, 2]]},
            "polygon points should be lists of two numbers",
        ),
    ],
)
def test_partial_update_element_wrong_param_polygon(
    mock_elements_worker, payload, error
):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Confidence
        ({"confidence": "lol"}, "confidence should be None or a float in [0..1] range"),
        ({"confidence": "0.2"}, "confidence should be None or a float in [0..1] range"),
        ({"confidence": -1.0}, "confidence should be None or a float in [0..1] range"),
        ({"confidence": 1.42}, "confidence should be None or a float in [0..1] range"),
        (
            {"confidence": float("inf")},
            "confidence should be None or a float in [0..1] range",
        ),
    ],
)
def test_partial_update_element_wrong_param_conf(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=re.escape(error)):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Rotation angle
        ({"rotation_angle": "lol"}, "rotation_angle should be a positive integer"),
        ({"rotation_angle": -1}, "rotation_angle should be a positive integer"),
        ({"rotation_angle": 0.5}, "rotation_angle should be a positive integer"),
        ({"rotation_angle": None}, "rotation_angle should be a positive integer"),
    ],
)
def test_partial_update_element_wrong_param_rota(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Mirrored
        ({"mirrored": "lol"}, "mirrored should be a boolean"),
        ({"mirrored": 1234}, "mirrored should be a boolean"),
        ({"mirrored": None}, "mirrored should be a boolean"),
    ],
)
def test_partial_update_element_wrong_param_mir(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Image
        ({"image": "lol"}, "image should be a UUID"),
        ({"image": 1234}, "image should be a UUID"),
        ({"image": None}, "image should be a UUID"),
    ],
)
def test_partial_update_element_wrong_param_image(mock_elements_worker, payload, error):
    api_payload = {
        "element": Element({"zone": None}),
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_elements_worker.partial_update_element(
            **api_payload,
        )


def test_partial_update_element_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/element/{elt.id}/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.partial_update_element(
            element=elt,
            type="something",
            name="0",
            polygon=[[1, 1], [2, 2], [2, 1], [1, 2]],
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("PATCH", f"http://testserver/api/v1/element/{elt.id}/")]


@pytest.mark.usefixtures("_mock_cached_elements", "_mock_cached_images")
@pytest.mark.parametrize(
    "payload",
    [
        (
            {
                "polygon": [[10, 10], [20, 20], [20, 10], [10, 20]],
                "confidence": None,
            }
        ),
        (
            {
                "rotation_angle": 45,
                "mirrored": False,
            }
        ),
        (
            {
                "polygon": [[10, 10], [20, 20], [20, 10], [10, 20]],
                "confidence": None,
                "rotation_angle": 45,
                "mirrored": False,
            }
        ),
    ],
)
def test_partial_update_element(responses, mock_elements_worker_with_cache, payload):
    elt = CachedElement.select().first()
    new_image = CachedImage.select().first()

    elt_response = {
        "image": str(new_image.id),
        **payload,
    }
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/element/{elt.id}/",
        status=200,
        # UUID not allowed in JSON
        json=elt_response,
    )

    element_update_response = mock_elements_worker_with_cache.partial_update_element(
        element=elt,
        **{**elt_response, "image": new_image.id},
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PATCH",
            f"http://testserver/api/v1/element/{elt.id}/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == elt_response
    assert element_update_response == elt_response

    cached_element = CachedElement.get(CachedElement.id == elt.id)
    # Always present in payload
    assert str(cached_element.image_id) == elt_response["image"]
    # Optional params
    if "polygon" in payload:
        # Cast to string as this is the only difference compared to model
        elt_response["polygon"] = str(elt_response["polygon"])

    for param in payload:
        assert getattr(cached_element, param) == elt_response[param]


@pytest.mark.usefixtures("_mock_cached_elements")
@pytest.mark.parametrize("confidence", [None, 0.42])
def test_partial_update_element_confidence(
    responses, mock_elements_worker_with_cache, confidence
):
    elt = CachedElement.select().first()
    elt_response = {
        "polygon": [[10, 10], [20, 20], [20, 10], [10, 20]],
        "confidence": confidence,
    }
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/element/{elt.id}/",
        status=200,
        json=elt_response,
    )

    element_update_response = mock_elements_worker_with_cache.partial_update_element(
        element=elt,
        **elt_response,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PATCH",
            f"http://testserver/api/v1/element/{elt.id}/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == elt_response
    assert element_update_response == elt_response

    cached_element = CachedElement.get(CachedElement.id == elt.id)
    assert cached_element.polygon == str(elt_response["polygon"])
    assert cached_element.confidence == confidence
