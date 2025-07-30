"""
ElementsWorker methods for images.
"""

from arkindex_worker.models import Image


class ImageMixin:
    def create_iiif_url(self, url: str) -> Image:
        """
        Create an image from an existing IIIF image by URL.
        The URL should be of the image's identifier, not of its Image Information request (`/info.json`).

        :param url: URL of the image.
        :returns: The created image.
        """
        assert url and isinstance(url, str), (
            "url shouldn't be null and should be of type str"
        )

        return Image(self.api_client.request("CreateIIIFURL", body={"url": url}))
