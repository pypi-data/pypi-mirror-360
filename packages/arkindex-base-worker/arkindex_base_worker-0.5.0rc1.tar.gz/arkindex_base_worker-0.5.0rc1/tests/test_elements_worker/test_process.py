import pytest

from tests import PROCESS_ID


@pytest.mark.parametrize(
    ("with_image", "elements"),
    [
        (
            False,
            [
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "type_id": "baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "element 1",
                    "confidence": 1,
                    "image_id": None,
                    "image_width": None,
                    "image_height": None,
                    "image_url": None,
                    "polygon": None,
                    "rotation_angle": 0,
                    "mirrored": False,
                },
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa0",
                    "type_id": "baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "element 2",
                    "confidence": 1,
                    "image_id": None,
                    "image_width": None,
                    "image_height": None,
                    "image_url": None,
                    "polygon": None,
                    "rotation_angle": 0,
                    "mirrored": False,
                },
            ],
        ),
        (
            True,
            [
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "type_id": "baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "element 1",
                    "confidence": 1,
                    "image_id": "aaa2aaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "image_width": 76,
                    "image_height": 138,
                    "image_url": "http://somewhere.com/iiif/image.jpeg",
                    "polygon": [[0, 0], [0, 40], [20, 40], [20, 0]],
                    "rotation_angle": 0,
                    "mirrored": False,
                },
                {
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa0",
                    "type_id": "baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "name": "element 2",
                    "confidence": 1,
                    "image_id": "aaa2aaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                    "image_width": 138,
                    "image_height": 76,
                    "image_url": "http://somewhere.com/iiif/image.jpeg",
                    "polygon": [[0, 0], [0, 40], [20, 40], [20, 0]],
                    "rotation_angle": 0,
                    "mirrored": False,
                },
            ],
        ),
    ],
)
def test_list_process_elements_with_image(
    responses, mock_elements_worker, with_image, elements
):
    responses.add(
        responses.GET,
        f"http://testserver/api/v1/process/{PROCESS_ID}/elements/?page_size=500&with_count=true&with_image={with_image}",
        status=200,
        json={
            "count": 2,
            "next": None,
            "results": elements,
        },
    )
    assert (
        list(mock_elements_worker.list_process_elements(with_image=with_image))
        == elements
    )
