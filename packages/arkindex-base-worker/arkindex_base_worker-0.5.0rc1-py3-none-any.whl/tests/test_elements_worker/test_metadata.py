import json
import re

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex.mock import MockApiClient
from arkindex_worker.cache import CachedElement
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE
from arkindex_worker.worker import MetaType

from . import BASE_API_CALLS


def test_create_metadata_wrong_element(mock_elements_worker):
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be of type Element or CachedElement",
    ):
        mock_elements_worker.create_metadata(
            element=None,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )

    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be of type Element or CachedElement",
    ):
        mock_elements_worker.create_metadata(
            element="not element type",
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )


def test_create_metadata_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type MetaType"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type=None,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type MetaType"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type=1234,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )

    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type MetaType"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type="not_a_metadata_type",
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )


def test_create_metadata_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name=None,
            value="La Turbine, Grenoble 38000",
        )

    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name=1234,
            value="La Turbine, Grenoble 38000",
        )


def test_create_metadata_wrong_value(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(
        AssertionError, match="value shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value=None,
        )

    with pytest.raises(
        AssertionError, match="value shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value=1234,
        )


def test_create_metadata_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        )
    ]


def test_create_metadata(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    metadata_id = mock_elements_worker.create_metadata(
        element=elt,
        type=MetaType.Location,
        name="Teklia",
        value="La Turbine, Grenoble 38000",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "location",
        "name": "Teklia",
        "value": "La Turbine, Grenoble 38000",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert metadata_id == "12345678-1234-1234-1234-123456789123"


def test_create_metadata_cached_element(responses, mock_elements_worker_with_cache):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    metadata_id = mock_elements_worker_with_cache.create_metadata(
        element=elt,
        type=MetaType.Location,
        name="Teklia",
        value="La Turbine, Grenoble 38000",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "location",
        "name": "Teklia",
        "value": "La Turbine, Grenoble 38000",
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert metadata_id == "12345678-1234-1234-1234-123456789123"


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_metadata_bulk(batch_size, responses, mock_elements_worker):
    element = Element({"id": "12341234-1234-1234-1234-123412341234"})

    metadata_list = [
        {"type": MetaType.Text, "name": "fake_name", "value": "fake_value"},
        {
            "type": MetaType.Text,
            "name": "Year",
            "value": "2024",
        },
    ]
    if batch_size > 1:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
            status=201,
            json={
                "worker_run_id": "56785678-5678-5678-5678-567856785678",
                "metadata_list": [
                    {
                        "id": "fake_metadata_id1",
                        "type": metadata_list[0]["type"].value,
                        "name": metadata_list[0]["name"],
                        "value": metadata_list[0]["value"],
                        "dates": [],
                    },
                    {
                        "id": "fake_metadata_id2",
                        "type": metadata_list[1]["type"].value,
                        "name": metadata_list[1]["name"],
                        "value": metadata_list[1]["value"],
                        "dates": [],
                    },
                ],
            },
        )
    else:
        for idx, meta in enumerate(metadata_list, start=1):
            responses.add(
                responses.POST,
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
                status=201,
                json={
                    "worker_run_id": "56785678-5678-5678-5678-567856785678",
                    "metadata_list": [
                        {
                            "id": f"fake_metadata_id{idx}",
                            "type": meta["type"].value,
                            "name": meta["name"],
                            "value": meta["value"],
                            "dates": [],
                        }
                    ],
                },
            )

    created_metadata_list = mock_elements_worker.create_metadata_bulk(
        element, metadata_list, batch_size=batch_size
    )

    bulk_api_calls = [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_meta = {
        **metadata_list[0],
        "type": metadata_list[0]["type"].value,
    }
    second_meta = {**metadata_list[1], "type": metadata_list[1]["type"].value}
    empty_payload = {
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "metadata_list": [],
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "metadata_list": [first_meta, second_meta]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "metadata_list": [first_meta]})
        bodies.append({**empty_payload, "metadata_list": [second_meta]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    assert created_metadata_list == [
        {
            "id": "fake_metadata_id1",
            "type": metadata_list[0]["type"].value,
            "name": metadata_list[0]["name"],
            "value": metadata_list[0]["value"],
            "dates": [],
        },
        {
            "id": "fake_metadata_id2",
            "type": metadata_list[1]["type"].value,
            "name": metadata_list[1]["name"],
            "value": metadata_list[1]["value"],
            "dates": [],
        },
    ]


@pytest.mark.parametrize("batch_size", [DEFAULT_BATCH_SIZE, 1])
def test_create_metadata_bulk_cached_element(
    batch_size, responses, mock_elements_worker_with_cache
):
    element = CachedElement.create(
        id="12341234-1234-1234-1234-123412341234", type="thing"
    )

    metadata_list = [
        {"type": MetaType.Text, "name": "fake_name", "value": "fake_value"},
        {
            "type": MetaType.Text,
            "name": "Year",
            "value": "2024",
        },
    ]
    if batch_size > 1:
        responses.add(
            responses.POST,
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
            status=201,
            json={
                "worker_run_id": "56785678-5678-5678-5678-567856785678",
                "metadata_list": [
                    {
                        "id": "fake_metadata_id1",
                        "type": metadata_list[0]["type"].value,
                        "name": metadata_list[0]["name"],
                        "value": metadata_list[0]["value"],
                        "dates": [],
                    },
                    {
                        "id": "fake_metadata_id2",
                        "type": metadata_list[1]["type"].value,
                        "name": metadata_list[1]["name"],
                        "value": metadata_list[1]["value"],
                        "dates": [],
                    },
                ],
            },
        )
    else:
        for idx, meta in enumerate(metadata_list, start=1):
            responses.add(
                responses.POST,
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
                status=201,
                json={
                    "worker_run_id": "56785678-5678-5678-5678-567856785678",
                    "metadata_list": [
                        {
                            "id": f"fake_metadata_id{idx}",
                            "type": meta["type"].value,
                            "name": meta["name"],
                            "value": meta["value"],
                            "dates": [],
                        }
                    ],
                },
            )

    created_metadata_list = mock_elements_worker_with_cache.create_metadata_bulk(
        element, metadata_list, batch_size=batch_size
    )

    bulk_api_calls = [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        )
    ]
    if batch_size != DEFAULT_BATCH_SIZE:
        bulk_api_calls.append(
            (
                "POST",
                "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
            )
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + len(bulk_api_calls)
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + bulk_api_calls

    first_meta = {
        **metadata_list[0],
        "type": metadata_list[0]["type"].value,
    }
    second_meta = {**metadata_list[1], "type": metadata_list[1]["type"].value}
    empty_payload = {
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
        "metadata_list": [],
    }

    bodies = []
    first_call_idx = None
    if batch_size > 1:
        first_call_idx = -1
        bodies.append({**empty_payload, "metadata_list": [first_meta, second_meta]})
    else:
        first_call_idx = -2
        bodies.append({**empty_payload, "metadata_list": [first_meta]})
        bodies.append({**empty_payload, "metadata_list": [second_meta]})

    assert [
        json.loads(bulk_call.request.body)
        for bulk_call in responses.calls[first_call_idx:]
    ] == bodies

    assert created_metadata_list == [
        {
            "id": "fake_metadata_id1",
            "type": metadata_list[0]["type"].value,
            "name": metadata_list[0]["name"],
            "value": metadata_list[0]["value"],
            "dates": [],
        },
        {
            "id": "fake_metadata_id2",
            "type": metadata_list[1]["type"].value,
            "name": metadata_list[1]["name"],
            "value": metadata_list[1]["value"],
            "dates": [],
        },
    ]


@pytest.mark.parametrize("wrong_element", [None, "not_element_type", 1234, 12.5])
def test_create_metadata_bulk_wrong_element(mock_elements_worker, wrong_element):
    wrong_metadata_list = [
        {"type": MetaType.Text, "name": "fake_name", "value": "fake_value"}
    ]
    with pytest.raises(
        AssertionError,
        match="element shouldn't be null and should be of type Element or CachedElement",
    ):
        mock_elements_worker.create_metadata_bulk(
            element=wrong_element, metadata_list=wrong_metadata_list
        )


@pytest.mark.parametrize("wrong_type", [None, "not_metadata_type", 1234, 12.5])
def test_create_metadata_bulk_wrong_type(mock_elements_worker, wrong_type):
    element = Element({"id": "12341234-1234-1234-1234-123412341234"})
    wrong_metadata_list = [
        {"type": wrong_type, "name": "fake_name", "value": "fake_value"}
    ]
    with pytest.raises(
        AssertionError, match="type shouldn't be null and should be of type MetaType"
    ):
        mock_elements_worker.create_metadata_bulk(
            element=element, metadata_list=wrong_metadata_list
        )


@pytest.mark.parametrize("wrong_name", [None, 1234, 12.5, [1, 2, 3, 4]])
def test_create_metadata_bulk_wrong_name(mock_elements_worker, wrong_name):
    element = Element({"id": "fake_element_id"})
    wrong_metadata_list = [
        {"type": MetaType.Text, "name": wrong_name, "value": "fake_value"}
    ]
    with pytest.raises(
        AssertionError, match="name shouldn't be null and should be of type str"
    ):
        mock_elements_worker.create_metadata_bulk(
            element=element, metadata_list=wrong_metadata_list
        )


@pytest.mark.parametrize("wrong_value", [None, [1, 2, 3, 4]])
def test_create_metadata_bulk_wrong_value(mock_elements_worker, wrong_value):
    element = Element({"id": "fake_element_id"})
    wrong_metadata_list = [
        {"type": MetaType.Text, "name": "fake_name", "value": wrong_value}
    ]
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "value shouldn't be null and should be of type (str or float or int)"
        ),
    ):
        mock_elements_worker.create_metadata_bulk(
            element=element, metadata_list=wrong_metadata_list
        )


def test_create_metadata_bulk_api_error(responses, mock_elements_worker):
    element = Element({"id": "12341234-1234-1234-1234-123412341234"})
    metadata_list = [
        {
            "type": MetaType.Text,
            "name": "fake_name",
            "value": "fake_value",
        }
    ]
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_metadata_bulk(element, metadata_list)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        )
    ]


def test_list_element_metadata_wrong_load_parents(fake_dummy_worker):
    element = Element({"id": "element_id"})
    with pytest.raises(AssertionError, match="load_parents should be of type bool"):
        fake_dummy_worker.list_element_metadata(
            element=element,
            load_parents="not bool",
        )


def test_list_element_metadata(fake_dummy_worker):
    element = Element({"id": "element_id"})
    fake_dummy_worker.api_client.add_response(
        "ListElementMetaData",
        id=element.id,
        response=[{"id": "metadata_id"}],
    )
    assert fake_dummy_worker.list_element_metadata(element) == [{"id": "metadata_id"}]

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_element_metadata_cached_element(mock_elements_worker_with_cache):
    element = CachedElement.create(id="element_id", type="thing")
    mock_elements_worker_with_cache.api_client = MockApiClient()
    mock_elements_worker_with_cache.api_client.add_response(
        "ListElementMetaData",
        id="element_id",
        response=[{"id": "metadata_id"}],
    )
    assert mock_elements_worker_with_cache.list_element_metadata(element) == [
        {"id": "metadata_id"}
    ]

    assert len(mock_elements_worker_with_cache.api_client.history) == 1
    assert len(mock_elements_worker_with_cache.api_client.responses) == 0


def test_list_element_metadata_with_load_parents(fake_dummy_worker):
    element = Element({"id": "element_id"})
    fake_dummy_worker.api_client.add_response(
        "ListElementMetaData",
        id=element.id,
        load_parents=True,
        response=[{"id": "metadata_id"}, {"id": "parent_metadata_id"}],
    )
    assert fake_dummy_worker.list_element_metadata(element, load_parents=True) == [
        {"id": "metadata_id"},
        {"id": "parent_metadata_id"},
    ]

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0
