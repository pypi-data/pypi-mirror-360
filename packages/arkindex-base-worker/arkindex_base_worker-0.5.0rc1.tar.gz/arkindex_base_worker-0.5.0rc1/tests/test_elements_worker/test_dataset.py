import json
import logging

import pytest

from arkindex.exceptions import ErrorResponse
from arkindex_worker.models import Dataset, Element, Set
from arkindex_worker.worker.dataset import DatasetState
from tests import PROCESS_ID
from tests.test_elements_worker import BASE_API_CALLS


def test_list_process_sets_readonly_error(mock_dataset_worker):
    # Set worker in read_only mode
    mock_dataset_worker.worker_run_id = None
    assert mock_dataset_worker.is_read_only

    with pytest.raises(
        AssertionError, match="This helper is not available in read-only mode."
    ):
        mock_dataset_worker.list_process_sets()


def test_list_process_sets_api_error(responses, mock_dataset_worker):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/process/{PROCESS_ID}/sets/",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_dataset_worker.list_process_sets())

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # The API call is retried 5 times
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
    ]


def test_list_process_sets(
    responses,
    mock_dataset_worker,
):
    expected_results = [
        {
            "id": "set_1",
            "dataset": {
                "id": "dataset_1",
                "name": "Dataset 1",
                "description": "My first great dataset",
                "sets": [
                    {"id": "set_1", "name": "train"},
                    {"id": "set_2", "name": "val"},
                ],
                "state": "open",
                "corpus_id": "corpus_id",
                "creator": "test@teklia.com",
                "task_id": "task_id_1",
            },
            "set_name": "train",
        },
        {
            "id": "set_2",
            "dataset": {
                "id": "dataset_1",
                "name": "Dataset 1",
                "description": "My first great dataset",
                "sets": [
                    {"id": "set_1", "name": "train"},
                    {"id": "set_2", "name": "val"},
                ],
                "state": "open",
                "corpus_id": "corpus_id",
                "creator": "test@teklia.com",
                "task_id": "task_id_1",
            },
            "set_name": "val",
        },
        {
            "id": "set_3",
            "dataset": {
                "id": "dataset_2",
                "name": "Dataset 2",
                "description": "My second great dataset",
                "sets": [{"id": "set_3", "name": "my_set"}],
                "state": "complete",
                "corpus_id": "corpus_id",
                "creator": "test@teklia.com",
                "task_id": "task_id_2",
            },
            "set_name": "my_set",
        },
    ]
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/process/{PROCESS_ID}/sets/",
        status=200,
        json={
            "count": 3,
            "next": None,
            "results": expected_results,
        },
    )

    for idx, dataset_set in enumerate(mock_dataset_worker.list_process_sets()):
        assert isinstance(dataset_set, Set)
        assert dataset_set.name == expected_results[idx]["set_name"]

        assert isinstance(dataset_set.dataset, Dataset)
        assert dataset_set.dataset == expected_results[idx]["dataset"]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("GET", f"http://testserver/api/v1/process/{PROCESS_ID}/sets/"),
    ]


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Set
        (
            {"dataset_set": None},
            "dataset_set shouldn't be null and should be a Set",
        ),
        (
            {"dataset_set": "not Set type"},
            "dataset_set shouldn't be null and should be a Set",
        ),
    ],
)
def test_list_set_elements_wrong_param_dataset_set(mock_dataset_worker, payload, error):
    with pytest.raises(AssertionError, match=error):
        mock_dataset_worker.list_set_elements(**payload)


def test_list_set_elements_api_error(
    responses, mock_dataset_worker, default_dataset, default_train_set
):
    query_params = f"?set={default_train_set.name}&with_count=true"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        status=418,
    )

    with pytest.raises(
        Exception, match="Stopping pagination as data will be incomplete"
    ):
        next(mock_dataset_worker.list_set_elements(dataset_set=default_train_set))

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # The API call is retried 5 times
        (
            "GET",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        ),
        (
            "GET",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        ),
        (
            "GET",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        ),
        (
            "GET",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        ),
        (
            "GET",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        ),
    ]


def test_list_set_elements(
    responses,
    mock_dataset_worker,
    default_dataset,
    default_train_set,
):
    expected_results = [
        {
            "set": "train",
            "element": {
                "id": "element_1",
                "type": "page",
                "name": "1",
                "corpus": {},
                "thumbnail_url": None,
                "zone": {},
                "best_classes": None,
                "has_children": None,
                "worker_version_id": None,
                "worker_run_id": None,
            },
        }
    ]
    expected_results.append({**expected_results[-1]})
    expected_results[-1]["element"]["id"] = "element_2"
    expected_results[-1]["element"]["name"] = "2"

    query_params = f"?set={default_train_set.name}&with_count=true"
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        status=200,
        json={
            "count": 2,
            "next": None,
            "results": expected_results,
        },
    )

    for idx, element in enumerate(
        mock_dataset_worker.list_set_elements(dataset_set=default_train_set)
    ):
        assert isinstance(element, Element)
        assert element == expected_results[idx]["element"]

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "GET",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/elements/{query_params}",
        )
    ]


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # Dataset
        (
            {"dataset": None},
            "dataset shouldn't be null and should be a Dataset",
        ),
        (
            {"dataset": "not dataset type"},
            "dataset shouldn't be null and should be a Dataset",
        ),
    ],
)
def test_update_dataset_state_wrong_param_dataset(
    mock_dataset_worker, default_dataset, payload, error
):
    api_payload = {
        "dataset": Dataset(**default_dataset),
        "state": DatasetState.Building,
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_dataset_worker.update_dataset_state(**api_payload)


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        # DatasetState
        (
            {"state": None},
            "state shouldn't be null and should be a str from DatasetState",
        ),
        (
            {"state": "not dataset type"},
            "state shouldn't be null and should be a str from DatasetState",
        ),
    ],
)
def test_update_dataset_state_wrong_param_state(
    mock_dataset_worker, default_dataset, payload, error
):
    api_payload = {
        "dataset": Dataset(**default_dataset),
        "state": DatasetState.Building,
        **payload,
    }

    with pytest.raises(AssertionError, match=error):
        mock_dataset_worker.update_dataset_state(**api_payload)


def test_update_dataset_state_readonly_error(
    caplog, mock_dev_dataset_worker, default_dataset
):
    api_payload = {
        "dataset": Dataset(**default_dataset),
        "state": DatasetState.Building,
    }

    assert not mock_dev_dataset_worker.update_dataset_state(**api_payload)
    assert [(level, message) for _, level, message in caplog.record_tuples] == [
        (
            logging.WARNING,
            "Cannot update dataset as this worker is in read-only mode",
        ),
    ]


def test_update_dataset_state_api_error(
    responses, mock_dataset_worker, default_dataset
):
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/datasets/{default_dataset.id}/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_dataset_worker.update_dataset_state(
            dataset=default_dataset,
            state=DatasetState.Building,
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        ("PATCH", f"http://testserver/api/v1/datasets/{default_dataset.id}/")
    ]


def test_update_dataset_state(
    responses,
    mock_dataset_worker,
    default_dataset,
):
    dataset_response = {
        "name": "My dataset",
        "description": "A super dataset built by me",
        "sets": ["set_1", "set_2", "set_3"],
        "state": DatasetState.Building.value,
    }
    responses.add(
        responses.PATCH,
        f"http://testserver/api/v1/datasets/{default_dataset.id}/",
        status=200,
        json=dataset_response,
    )

    updated_dataset = mock_dataset_worker.update_dataset_state(
        dataset=default_dataset,
        state=DatasetState.Building,
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "PATCH",
            f"http://testserver/api/v1/datasets/{default_dataset.id}/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "state": DatasetState.Building.value
    }
    assert updated_dataset == Dataset(**{**default_dataset, **dataset_response})
