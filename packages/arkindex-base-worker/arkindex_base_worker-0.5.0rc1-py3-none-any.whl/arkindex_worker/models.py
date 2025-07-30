"""
Wrappers around API results to provide more convenient attribute access and IIIF helpers.
"""

import tempfile
from collections.abc import Generator
from contextlib import contextmanager

from PIL import Image
from requests import HTTPError


class MagicDict(dict):
    """
    A dict whose items can be accessed like attributes.
    """

    def _magify(self, item):
        """
        Automagically convert lists and dicts to MagicDicts and lists of MagicDicts
        Allows for nested access: foo.bar.baz
        """
        if isinstance(item, Dataset):
            return item
        if isinstance(item, list):
            return list(map(self._magify, item))
        if isinstance(item, dict):
            return MagicDict(item)
        return item

    def __getitem__(self, item):
        item = super().__getitem__(item)
        return self._magify(item)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute '{name}'"
            ) from e

    def __setattr__(self, name, value):
        return super().__setitem__(name, value)

    def __delattr__(self, name):
        try:
            return super().__delattr__(name)
        except AttributeError:
            try:
                return super().__delitem__(name)
            except KeyError:
                pass
            raise

    def __dir__(self):
        return super().__dir__() + list(self.keys())


class Element(MagicDict):
    """
    Describes an Arkindex element.
    """

    def resize_zone_url(self, size: str = "full") -> str:
        """
        Compute the URL of the image corresponding to the size
        :param size: Requested size
        :return: The URL corresponding to the size
        """
        if size == "full":
            return self.zone.url
        else:
            parts = self.zone.url.split("/")
            parts[-3] = size
            return "/".join(parts)

    def image_url(self, size: str = "full") -> str | None:
        """
        Build a URL to access the image.
        When possible, will return the S3 URL for images, so an ML worker can bypass IIIF servers.
        :param size: Subresolution of the image, following the syntax of the IIIF resize parameter.
        :returns: A URL to the image, or None if the element does not have an image.
        """
        if not self.get("zone"):
            return
        url = self.zone.image.get("s3_url")
        if url:
            return url
        url = self.zone.image.url
        if not url.endswith("/"):
            url += "/"
        return f"{url}full/{size}/0/default.jpg"

    @property
    def polygon(self) -> list[float]:
        """
        Access an Element's polygon.
        This is a shortcut to an Element's polygon, normally accessed via
        its zone field via `zone.polygon`. This is mostly done
        to facilitate access to this important field by matching
        the [CachedElement][arkindex_worker.cache.CachedElement].polygon field.
        """
        if not self.get("zone"):
            raise ValueError(f"Element {self.id} has no zone")
        return self.zone.polygon

    @property
    def requires_tiles(self) -> bool:
        """
        Whether or not downloading and combining IIIF tiles will be necessary
           to retrieve this element's image. Will be False if the element has no image.
        """
        from arkindex_worker.image import polygon_bounding_box

        if not self.get("zone") or self.zone.image.get("s3_url"):
            return False
        max_width = self.zone.image.server.max_width or float("inf")
        max_height = self.zone.image.server.max_height or float("inf")
        bounding_box = polygon_bounding_box(self.zone.polygon)
        return bounding_box.width > max_width or bounding_box.height > max_height

    def open_image(
        self,
        *args,
        max_width: int | None = None,
        max_height: int | None = None,
        use_full_image: bool | None = False,
        **kwargs,
    ) -> Image.Image:
        """
        Open this element's image using Pillow, rotating and mirroring it according
        to the ``rotation_angle`` and ``mirrored`` attributes.

        When tiling is not required to download the image, and no S3 URL is available
        to bypass IIIF servers, the image will be cropped to the rectangle bounding box
        of the ``zone.polygon`` attribute.

        Warns:
        ----
           This method implicitly applies the element's orientation to the image.

           If your process uses the returned image to find more polygons and send them
           back to Arkindex, use the [arkindex_worker.image.revert_orientation][]
           helper to undo the orientation on all polygons before sending them, as the
           Arkindex API expects unoriented polygons.

           Although not recommended, you can bypass this behavior by passing
           ``rotation_angle=0, mirrored=False`` as keyword arguments.


        Warns:
        ----
           If both, ``max_width`` and ``max_height`` are set, the image ratio is not preserved.


        :param max_width: The maximum width of the image.
        :param max_height: The maximum height of the image.
        :param use_full_image: Ignore the ``zone.polygon`` and always
           retrieve the image without cropping.
        :param *args: Positional arguments passed to [arkindex_worker.image.open_image][].
        :param **kwargs: Keyword arguments passed to [arkindex_worker.image.open_image][].
        :raises ValueError: When the element does not have an image.
        :raises NotImplementedError: When the ``max_size`` parameter is set,
           but the IIIF server's configuration requires downloading and combining tiles
           to retrieve the image.
        :raises NotImplementedError: When an S3 URL has been used to download the image,
           but the URL has expired. Re-fetching the URL automatically is not supported.
        :return: A Pillow image.
        """
        from arkindex_worker.image import (
            download_tiles,
            open_image,
        )

        if not self.get("zone"):
            raise ValueError(f"Element {self.id} has no zone")

        if self.requires_tiles:
            if max_width is None and max_height is None:
                return download_tiles(self.zone.image.url)
            else:
                raise NotImplementedError

        if max_width is None and max_height is None:
            resize = "full"
        else:
            original_size = {"w": self.zone.image.width, "h": self.zone.image.height}
            # No resizing if the image is smaller than the wanted size.
            if (max_width is None or original_size["w"] <= max_width) and (
                max_height is None or original_size["h"] <= max_height
            ):
                resize = "full"
            # Resizing if the image is bigger than the wanted size.
            else:
                resize = f"{max_width or ''},{max_height or ''}"

        url = self.image_url(resize) if use_full_image else self.resize_zone_url(resize)

        try:
            return open_image(
                url,
                *args,
                rotation_angle=self.rotation_angle,
                mirrored=self.mirrored,
                **kwargs,
            )
        except HTTPError as e:
            if (
                self.zone.image.get("s3_url") is not None
                and e.response.status_code == 403
            ):
                # This element uses an S3 URL: the URL may have expired.
                # Call the API to get a fresh URL and try again
                # TODO: this should be done by the worker
                raise NotImplementedError from e
                return open_image(self.image_url(resize), *args, **kwargs)
            raise

    @contextmanager
    def open_image_tempfile(
        self, format: str | None = "jpeg", *args, **kwargs
    ) -> Generator[tempfile.NamedTemporaryFile, None, None]:
        """
        Get the element's image as a temporary file stored on the disk.
        To be used as a context manager.

        Example
        ----
        ```
        with element.open_image_tempfile() as f:
            ...
        ```

        :param format: File format to use the store the image on the disk.
           Must be a format supported by Pillow.
        :param *args: Positional arguments passed to [arkindex_worker.image.open_image][].
        :param **kwargs: Keyword arguments passed to [arkindex_worker.image.open_image][].

        """
        with tempfile.NamedTemporaryFile() as f:
            self.open_image(*args, **kwargs).save(f, format=format)
            yield f

    def __str__(self):
        if isinstance(self.type, dict):
            type_name = self.type["display_name"]
        else:
            type_name = str(self.type)
        return f"{type_name} {self.name} ({self.id})"


class ArkindexModel(MagicDict):
    def __str__(self):
        return f"{self.__class__.__name__} ({self.id})"


class Transcription(ArkindexModel):
    """
    Describes an Arkindex element's transcription.
    """


class Image(ArkindexModel):
    """
    Describes an Arkindex image.
    """


class Dataset(ArkindexModel):
    """
    Describes an Arkindex dataset.
    """

    @property
    def filepath(self) -> str:
        """
        Generic filepath to the Dataset compressed archive.
        """
        return f"{self.id}.tar.zst"


class Set(MagicDict):
    """
    Describes an Arkindex dataset set.
    """

    def __str__(self):
        # Not using ArkindexModel.__str__ as we do not retrieve the Set ID
        return f"{self.__class__.__name__} ({self.name}) from {self.dataset}"


class Artifact(ArkindexModel):
    """
    Describes an Arkindex artifact.
    """
