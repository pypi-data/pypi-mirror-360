import json

import pytest

from arkindex.exceptions import ErrorResponse

from . import BASE_API_CALLS


@pytest.mark.parametrize(
    ("data", "error_message"),
    [
        (None, "url shouldn't be null and should be of type str"),
        (1234, "url shouldn't be null and should be of type str"),
    ],
)
def test_create_iiif_url_wrong_data(data, error_message, mock_elements_worker):
    with pytest.raises(AssertionError, match=error_message):
        mock_elements_worker.create_iiif_url(url=data)


def test_create_iiif_url_api_error(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/image/iiif/url/",
        status=418,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_iiif_url("http://url/to/my/image")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/image/iiif/url/")]


def test_create_iiif_url(responses, mock_elements_worker):
    responses.add(
        responses.POST,
        "http://testserver/api/v1/image/iiif/url/",
        status=201,
        json={
            "id": "cafecafe-cafe-cafe-cafe-cafecafecafe",
            "url": "http://url/to/my/image",
            "status": "checked",
            "server": {
                "id": 5,
                "display_name": "My server",
                "url": "http://url/to/my",
                "max_width": 42,
                "max_height": 42,
            },
        },
    )

    image = mock_elements_worker.create_iiif_url("http://url/to/my/image")

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [("POST", "http://testserver/api/v1/image/iiif/url/")]
    assert json.loads(responses.calls[-1].request.body) == {
        "url": "http://url/to/my/image"
    }
    assert image.id == "cafecafe-cafe-cafe-cafe-cafecafecafe"
