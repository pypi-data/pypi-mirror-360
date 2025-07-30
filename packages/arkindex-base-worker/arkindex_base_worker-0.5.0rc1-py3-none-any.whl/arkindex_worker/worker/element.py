"""
ElementsWorker methods for elements and element types.
"""

import os
from collections.abc import Iterable
from operator import attrgetter
from uuid import UUID
from warnings import warn

from peewee import IntegrityError

from arkindex.exceptions import ErrorResponse
from arkindex_worker import logger
from arkindex_worker.cache import CachedElement, CachedImage, unsupported_cache
from arkindex_worker.models import Element
from arkindex_worker.utils import (
    DEFAULT_BATCH_SIZE,
    batch_publication,
    make_batches,
    pluralize,
)


class MissingElementType(Exception):
    """
    Raised when the specified element type was not found in the corpus and
    the worker cannot create it.
    """


class ElementMixin:
    def add_arguments(self):
        """Define specific ``argparse`` arguments for the worker using this mixin"""
        self.parser.add_argument(
            "--elements-list",
            help="JSON elements list to use",
            type=open,
            default=os.environ.get("TASK_ELEMENTS"),
        )
        self.parser.add_argument(
            "--element",
            type=str,
            nargs="+",
            help="One or more Arkindex element ID",
        )
        super().add_arguments()

    def list_corpus_types(self):
        """
        Loads available element types in corpus.
        """
        self.corpus_types = {
            element_type["slug"]: element_type
            for element_type in self.api_client.request(
                "RetrieveCorpus", id=self.corpus_id
            )["types"]
        }
        count = len(self.corpus_types)
        logger.info(
            f"Loaded {count} element {pluralize('type', count)} in corpus ({self.corpus_id})."
        )

    @unsupported_cache
    def create_element_type(
        self, slug: str, name: str, is_folder: bool = False
    ) -> None:
        """
        Create an element type on the given corpus.

        :param slug: Slug of the element type.
        :param name: Name of the element type.
        :param is_folder: Whether an element with this type can contain other elements or not.
        """
        assert slug and isinstance(slug, str), (
            "slug shouldn't be null and should be of type str"
        )
        assert name and isinstance(name, str), (
            "name shouldn't be null and should be of type str"
        )
        assert is_folder is not None and isinstance(is_folder, bool), (
            "is_folder shouldn't be null and should be of type bool"
        )

        try:
            element_type = self.api_client.request(
                "CreateElementType",
                body={
                    "slug": slug,
                    "display_name": name,
                    "folder": is_folder,
                    "corpus": self.corpus_id,
                },
            )
            self.corpus_types[slug] = element_type
            logger.info(f"Created a new element type with slug `{slug}`.")
        except ErrorResponse as e:
            # Only reload for 400 errors
            if e.status_code != 400:
                raise

            # Reload and make sure we have the element type now
            logger.warning(
                f"Unable to create the element type `{slug}`. Refreshing corpus element types cache."
            )
            self.list_corpus_types()
            assert slug in self.corpus_types, (
                f"Missing element type `{slug}` even after refreshing."
            )

    def check_required_types(
        self, type_slugs: list[str], create_missing: bool = False
    ) -> None:
        """
        Check that every element type needed is available in the corpus.
        Missing ones may be created automatically if needed.

        :param type_slugs: Element type slugs to search.
        :param create_missing: Whether the missing types should be created. Defaults to False.
        :raises MissingElementType: When an entity type is missing and cannot be created.
        """
        assert type_slugs and isinstance(type_slugs, list), (
            "type_slugs shouldn't be null and should be of type list"
        )

        for index, slug in enumerate(type_slugs):
            assert isinstance(slug, str), (
                f"Element type at index {index} in type_slugs: Should be of type str"
            )

        assert create_missing is not None and isinstance(create_missing, bool), (
            "create_missing shouldn't be null and should be of type bool"
        )

        if not self.corpus_types:
            self.list_corpus_types()

        for slug in type_slugs:
            # Do nothing if the type already exists
            if slug in self.corpus_types:
                continue

            # Do not create missing if not requested
            if not create_missing:
                raise MissingElementType(
                    f"Element type `{slug}` was not in the corpus."
                )

            # Create the type if non-existent
            self.create_element_type(slug=slug, name=slug)

    @unsupported_cache
    def create_sub_element(
        self,
        element: Element,
        type: str,
        name: str,
        polygon: list[list[int | float]] | None = None,
        confidence: float | None = None,
        image: str | None = None,
        slim_output: bool = True,
    ) -> str:
        """
        Create a child element on the given element through the API.

        :param Element element: The parent element.
        :param type: Slug of the element type for this child element.
        :param name: Name of the child element.
        :param polygon: Optional polygon of the child element.
        :param confidence: Optional confidence score, between 0.0 and 1.0.
        :param image: Optional image ID of the child element.
        :param slim_output: Whether to return the child ID or the full child.
        :returns: UUID of the created element.
        """
        assert element and isinstance(element, Element), (
            "element shouldn't be null and should be of type Element"
        )
        assert type and isinstance(type, str), (
            "type shouldn't be null and should be of type str"
        )
        assert name and isinstance(name, str), (
            "name shouldn't be null and should be of type str"
        )
        assert polygon is None or isinstance(polygon, list), (
            "polygon should be None or a list"
        )
        if polygon is not None:
            assert len(polygon) >= 3, "polygon should have at least three points"
            assert all(
                isinstance(point, list) and len(point) == 2 for point in polygon
            ), "polygon points should be lists of two items"
            assert all(
                isinstance(coord, int | float) for point in polygon for coord in point
            ), "polygon points should be lists of two numbers"
        assert confidence is None or (
            isinstance(confidence, float) and 0 <= confidence <= 1
        ), "confidence should be None or a float in [0..1] range"
        assert image is None or isinstance(image, str), "image should be None or string"
        if image is not None:
            # Make sure it's a valid UUID
            try:
                UUID(image)
            except ValueError as e:
                raise ValueError("image is not a valid uuid.") from e
        if polygon and image is None:
            assert element.zone, (
                "An image or a parent with an image is required to create an element with a polygon."
            )
        assert isinstance(slim_output, bool), "slim_output should be of type bool"

        if self.is_read_only:
            logger.warning("Cannot create element as this worker is in read-only mode")
            return

        sub_element = self.api_client.request(
            "CreateElement",
            body={
                "type": type,
                "name": name,
                "image": image,
                "corpus": element.corpus.id,
                "polygon": polygon,
                "parent": element.id,
                "worker_run_id": self.worker_run_id,
                "confidence": confidence,
            },
        )

        return sub_element["id"] if slim_output else sub_element

    @batch_publication
    def create_elements(
        self,
        parent: Element | CachedElement,
        elements: list[dict[str, str | list[list[int | float]] | float | None]],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[dict[str, str]]:
        """
        Create child elements on the given element in a single API request.

        :param parent: Parent element for all the new child elements. The parent must have an image and a polygon.
        :param elements: List of dicts, one per element. Each dict can have the following keys:

            name (str)
               Required. Name of the element.

            type (str)
               Required. Slug of the element type for this element.

            polygon (list(list(int or float)))
               Required. Polygon for this child element. Must have at least three points, with each point
               having two non-negative coordinates and being inside of the parent element's image.

            confidence (float or None)
                Optional confidence score, between 0.0 and 1.0.

        :param batch_size: The size of each batch, which will be used to split the publication to avoid API errors.

        :return: List of dicts, with each dict having a single key, ``id``, holding the UUID of each created element.
        """
        if isinstance(parent, Element):
            assert parent.get("zone"), (
                "create_elements cannot be used on parents without zones"
            )
        elif isinstance(parent, CachedElement):
            assert parent.image_id, (
                "create_elements cannot be used on parents without images"
            )
        else:
            raise TypeError(
                "Parent element should be an Element or CachedElement instance"
            )

        assert elements and isinstance(elements, list), (
            "elements shouldn't be null and should be of type list"
        )

        for index, element in enumerate(elements):
            assert isinstance(element, dict), (
                f"Element at index {index} in elements: Should be of type dict"
            )

            name = element.get("name")
            assert name and isinstance(name, str), (
                f"Element at index {index} in elements: name shouldn't be null and should be of type str"
            )

            type = element.get("type")
            assert type and isinstance(type, str), (
                f"Element at index {index} in elements: type shouldn't be null and should be of type str"
            )

            polygon = element.get("polygon")
            assert polygon and isinstance(polygon, list), (
                f"Element at index {index} in elements: polygon shouldn't be null and should be of type list"
            )
            assert len(polygon) >= 3, (
                f"Element at index {index} in elements: polygon should have at least three points"
            )
            assert all(
                isinstance(point, list) and len(point) == 2 for point in polygon
            ), (
                f"Element at index {index} in elements: polygon points should be lists of two items"
            )
            assert all(
                isinstance(coord, int | float) for point in polygon for coord in point
            ), (
                f"Element at index {index} in elements: polygon points should be lists of two numbers"
            )

            confidence = element.get("confidence")
            assert confidence is None or (
                isinstance(confidence, float) and 0 <= confidence <= 1
            ), (
                f"Element at index {index} in elements: confidence should be None or a float in [0..1] range"
            )

        if self.is_read_only:
            logger.warning("Cannot create elements as this worker is in read-only mode")
            return

        created_ids = [
            created_id
            for batch in make_batches(elements, "element", batch_size)
            for created_id in self.api_client.request(
                "CreateElements",
                id=parent.id,
                body={
                    "worker_run_id": self.worker_run_id,
                    "elements": batch,
                },
            )
        ]

        if self.use_cache:
            # Create the image as needed and handle both an Element and a CachedElement
            if isinstance(parent, CachedElement):
                image_id = parent.image_id
            else:
                image_id = parent.zone.image.id
                CachedImage.get_or_create(
                    id=parent.zone.image.id,
                    defaults={
                        "width": parent.zone.image.width,
                        "height": parent.zone.image.height,
                        "url": parent.zone.image.url,
                    },
                )

            # Store elements in local cache
            try:
                to_insert = [
                    {
                        "id": created_ids[idx]["id"],
                        "parent_id": parent.id,
                        "type": element["type"],
                        "image_id": image_id,
                        "polygon": element["polygon"],
                        "worker_run_id": self.worker_run_id,
                        "confidence": element.get("confidence"),
                    }
                    for idx, element in enumerate(elements)
                ]
                CachedElement.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(f"Couldn't save created elements in local cache: {e}")

        return created_ids

    @unsupported_cache
    def create_element_parent(
        self,
        parent: Element,
        child: Element,
    ) -> dict[str, str]:
        """
        Link an element to a parent through the API.

        :param parent: Parent element.
        :param child: Child element.
        :returns: A dict from the ``CreateElementParent`` API endpoint.
        """
        assert parent and isinstance(parent, Element), (
            "parent shouldn't be null and should be of type Element"
        )
        assert child and isinstance(child, Element), (
            "child shouldn't be null and should be of type Element"
        )

        if self.is_read_only:
            logger.warning("Cannot link elements as this worker is in read-only mode")
            return

        return self.api_client.request(
            "CreateElementParent",
            parent=parent.id,
            child=child.id,
        )

    @unsupported_cache
    @batch_publication
    def create_element_children(
        self,
        parent: Element,
        children: list[Element],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[str]:
        """
        Link multiple elements to a single parent through the API.

        :param parent: Parent element.
        :param children: A list of child elements.
        :param batch_size: The size of each batch, which will be used to split the publication to avoid API errors.

        :returns: A list containing the string UUID of each child linked to the parent.
        """
        assert parent and isinstance(parent, Element), (
            "parent shouldn't be null and should be of type Element"
        )

        assert children and isinstance(children, list), (
            "children shouldn't be null and should be of type list"
        )

        for index, child in enumerate(children):
            assert isinstance(child, Element), (
                f"Child at index {index} in children: Should be of type Element"
            )

        if self.is_read_only:
            logger.warning("Cannot link elements as this worker is in read-only mode")
            return

        return [
            child_id
            for batch in make_batches(children, "child", batch_size)
            for child_id in self.api_client.request(
                "CreateElementChildren",
                id=parent.id,
                body={
                    "children": list(map(attrgetter("id"), batch)),
                },
            )["children"]
        ]

    def partial_update_element(
        self, element: Element | CachedElement, **kwargs
    ) -> dict:
        """
        Partially updates an element through the API.

        :param element: The element to update.
        :param **kwargs:

            * *type* (``str``): Optional slug type of the element.
            * *name* (``str``): Optional name of the element.
            * *polygon* (``list``): Optional polygon for this element
            * *confidence* (``float``): Optional confidence score of this element
            * *rotation_angle* (``int``): Optional rotation angle of this element
            * *mirrored* (``bool``): Optional mirror status of this element
            * *image* (``UUID``): Optional ID of the image of this element


        :returns: A dict from the ``PartialUpdateElement`` API endpoint.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )

        if "type" in kwargs:
            assert isinstance(kwargs["type"], str), "type should be a str"

        if "name" in kwargs:
            assert isinstance(kwargs["name"], str), "name should be a str"

        if "polygon" in kwargs:
            polygon = kwargs["polygon"]
            assert isinstance(polygon, list), "polygon should be a list"
            assert len(polygon) >= 3, "polygon should have at least three points"
            assert all(
                isinstance(point, list) and len(point) == 2 for point in polygon
            ), "polygon points should be lists of two items"
            assert all(
                isinstance(coord, int | float) for point in polygon for coord in point
            ), "polygon points should be lists of two numbers"

        if "confidence" in kwargs:
            confidence = kwargs["confidence"]
            assert confidence is None or (
                isinstance(confidence, float) and 0 <= confidence <= 1
            ), "confidence should be None or a float in [0..1] range"

        if "rotation_angle" in kwargs:
            rotation_angle = kwargs["rotation_angle"]
            assert isinstance(rotation_angle, int) and rotation_angle >= 0, (
                "rotation_angle should be a positive integer"
            )

        if "mirrored" in kwargs:
            assert isinstance(kwargs["mirrored"], bool), "mirrored should be a boolean"

        if "image" in kwargs:
            image = kwargs["image"]
            assert isinstance(image, UUID), "image should be a UUID"
            # Cast to string
            kwargs["image"] = str(image)

        if self.is_read_only:
            logger.warning("Cannot update element as this worker is in read-only mode")
            return

        updated_element = self.api_client.request(
            "PartialUpdateElement",
            id=element.id,
            body=kwargs,
        )

        if self.use_cache:
            # Name is not present in CachedElement model
            kwargs.pop("name", None)

            # Stringify polygon if present
            if "polygon" in kwargs:
                kwargs["polygon"] = str(kwargs["polygon"])

            # Retrieve the right image
            if "image" in kwargs:
                kwargs["image"] = CachedImage.get_by_id(kwargs["image"])

            CachedElement.update(**kwargs).where(
                CachedElement.id == element.id
            ).execute()

        return updated_element

    def list_elements(
        self,
        folder: bool | None = None,
        name: str | None = None,
        top_level: bool | None = None,
        transcription_worker_version: str | bool | None = None,
        transcription_worker_run: str | bool | None = None,
        type: str | None = None,
        with_classes: bool | None = None,
        with_corpus: bool | None = None,
        with_metadata: bool | None = None,
        with_has_children: bool | None = None,
        with_zone: bool | None = None,
        worker_version: str | bool | None = None,
        worker_run: str | bool | None = None,
    ) -> Iterable[dict] | Iterable[CachedElement]:
        """
        List element in a corpus.

        Warns:
        ----
        The following parameters are **deprecated**:

        - `transcription_worker_version` in favor of `transcription_worker_run`
        - `worker_version` in favor of `worker_run`

        :param folder: Restrict to or exclude elements with folder types.
           This parameter is not supported when caching is enabled.
        :param name: Restrict to elements whose name contain a substring (case-insensitive).
           This parameter is not supported when caching is enabled.
        :param top_level: Restrict to or exclude folder elements without parent elements (top-level elements).
           This parameter is not supported when caching is enabled.
        :param transcription_worker_version: **Deprecated** Restrict to elements that have a transcription created by a worker version with this UUID. Set to False to look for elements that have a manual transcription.
           This parameter is not supported when caching is enabled.
        :param transcription_worker_run: Restrict to elements that have a transcription created by a worker run with this UUID. Set to False to look for elements that have a manual transcription.
           This parameter is not supported when caching is enabled.
        :param type: Restrict to elements with a specific type slug
           This parameter is not supported when caching is enabled.
        :param with_classes: Include each element's classifications in the response.
           This parameter is not supported when caching is enabled.
        :param with_corpus: Include each element's corpus in the response.
           This parameter is not supported when caching is enabled.
        :param with_has_children: Include the ``has_children`` attribute in the response,
           indicating if this element has child elements of its own.
           This parameter is not supported when caching is enabled.
        :param with_metadata: Include each element's metadata in the response.
           This parameter is not supported when caching is enabled.
        :param with_zone: Include the ``zone`` attribute in the response,
           holding the element's image and polygon.
           This parameter is not supported when caching is enabled.
        :param worker_version: **Deprecated** Restrict to elements created by a worker version with this UUID.
        :param worker_run: Restrict to elements created by a worker run with this UUID.
        :return: An iterable of dicts from the ``ListElementChildren`` API endpoint,
           or an iterable of [CachedElement][arkindex_worker.cache.CachedElement] when caching is enabled.
        """
        query_params = {}
        if folder is not None:
            assert isinstance(folder, bool), "folder should be of type bool"
            query_params["folder"] = folder
        if name:
            assert isinstance(name, str), "name should be of type str"
            query_params["name"] = name
        if top_level is not None:
            assert isinstance(top_level, bool), "top_level should be of type bool"
            query_params["top_level"] = top_level
        if transcription_worker_version is not None:
            warn(
                "`transcription_worker_version` usage is deprecated. Consider using `transcription_worker_run` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            assert isinstance(transcription_worker_version, str | bool), (
                "transcription_worker_version should be of type str or bool"
            )
            if isinstance(transcription_worker_version, bool):
                assert transcription_worker_version is False, (
                    "if of type bool, transcription_worker_version can only be set to False"
                )
            query_params["transcription_worker_version"] = transcription_worker_version
        if transcription_worker_run is not None:
            assert isinstance(transcription_worker_run, str | bool), (
                "transcription_worker_run should be of type str or bool"
            )
            if isinstance(transcription_worker_run, bool):
                assert transcription_worker_run is False, (
                    "if of type bool, transcription_worker_run can only be set to False"
                )
            query_params["transcription_worker_run"] = transcription_worker_run
        if type:
            assert isinstance(type, str), "type should be of type str"
            query_params["type"] = type
        if with_classes is not None:
            assert isinstance(with_classes, bool), "with_classes should be of type bool"
            query_params["with_classes"] = with_classes
        if with_corpus is not None:
            assert isinstance(with_corpus, bool), "with_corpus should be of type bool"
            query_params["with_corpus"] = with_corpus
        if with_has_children is not None:
            assert isinstance(with_has_children, bool), (
                "with_has_children should be of type bool"
            )
            query_params["with_has_children"] = with_has_children
        if with_metadata is not None:
            assert isinstance(with_metadata, bool), (
                "with_metadata should be of type bool"
            )
            query_params["with_metadata"] = with_metadata
        if with_zone is not None:
            assert isinstance(with_zone, bool), "with_zone should be of type bool"
            query_params["with_zone"] = with_zone
        if worker_version is not None:
            warn(
                "`worker_version` usage is deprecated. Consider using `worker_run` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            assert isinstance(worker_version, str | bool), (
                "worker_version should be of type str or bool"
            )
            if isinstance(worker_version, bool):
                assert worker_version is False, (
                    "if of type bool, worker_version can only be set to False"
                )
            query_params["worker_version"] = worker_version
        if worker_run is not None:
            assert isinstance(worker_run, str | bool), (
                "worker_run should be of type str or bool"
            )
            if isinstance(worker_run, bool):
                assert worker_run is False, (
                    "if of type bool, worker_run can only be set to False"
                )
            query_params["worker_run"] = worker_run

        if not self.use_cache:
            return self.api_client.paginate(
                "ListElements", corpus=self.corpus_id, **query_params
            )

        # Checking that we only received query_params handled by the cache
        assert set(query_params.keys()) <= {
            "type",
            "worker_version",
            "worker_run",
        }, (
            "When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'"
        )

        query = CachedElement.select()
        if type:
            query = query.where(CachedElement.type == type)
        if worker_version is not None:
            # If worker_version=False, filter by manual worker_version e.g. None
            worker_version_id = worker_version or None
            if worker_version_id:
                query = query.where(
                    CachedElement.worker_version_id == worker_version_id
                )
            else:
                query = query.where(CachedElement.worker_version_id.is_null())

        if worker_run is not None:
            # If worker_run=False, filter by manual worker_run e.g. None
            worker_run_id = worker_run or None
            if worker_run_id:
                query = query.where(CachedElement.worker_run_id == worker_run_id)
            else:
                query = query.where(CachedElement.worker_run_id.is_null())

        return query

    def list_element_children(
        self,
        element: Element | CachedElement,
        folder: bool | None = None,
        name: str | None = None,
        recursive: bool | None = None,
        transcription_worker_version: str | bool | None = None,
        transcription_worker_run: str | bool | None = None,
        type: str | None = None,
        with_classes: bool | None = None,
        with_corpus: bool | None = None,
        with_metadata: bool | None = None,
        with_has_children: bool | None = None,
        with_zone: bool | None = None,
        worker_version: str | bool | None = None,
        worker_run: str | bool | None = None,
    ) -> Iterable[dict] | Iterable[CachedElement]:
        """
        List children of an element.

        Warns:
        ----
        The following parameters are **deprecated**:

        - `transcription_worker_version` in favor of `transcription_worker_run`
        - `worker_version` in favor of `worker_run`

        :param element: Parent element to find children of.
        :param folder: Restrict to or exclude elements with folder types.
           This parameter is not supported when caching is enabled.
        :param name: Restrict to elements whose name contain a substring (case-insensitive).
           This parameter is not supported when caching is enabled.
        :param recursive: Look for elements recursively (grand-children, etc.)
           This parameter is not supported when caching is enabled.
        :param transcription_worker_version: **Deprecated** Restrict to elements that have a transcription created by a worker version with this UUID. Set to False to look for elements that have a manual transcription.
           This parameter is not supported when caching is enabled.
        :param transcription_worker_run: Restrict to elements that have a transcription created by a worker run with this UUID. Set to False to look for elements that have a manual transcription.
           This parameter is not supported when caching is enabled.
        :param type: Restrict to elements with a specific type slug
           This parameter is not supported when caching is enabled.
        :param with_classes: Include each element's classifications in the response.
           This parameter is not supported when caching is enabled.
        :param with_corpus: Include each element's corpus in the response.
           This parameter is not supported when caching is enabled.
        :param with_has_children: Include the ``has_children`` attribute in the response,
           indicating if this element has child elements of its own.
           This parameter is not supported when caching is enabled.
        :param with_metadata: Include each element's metadata in the response.
           This parameter is not supported when caching is enabled.
        :param with_zone: Include the ``zone`` attribute in the response,
           holding the element's image and polygon.
           This parameter is not supported when caching is enabled.
        :param worker_version: **Deprecated** Restrict to elements created by a worker version with this UUID.
        :param worker_run: Restrict to elements created by a worker run with this UUID.
        :return: An iterable of dicts from the ``ListElementChildren`` API endpoint,
           or an iterable of [CachedElement][arkindex_worker.cache.CachedElement] when caching is enabled.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        query_params = {}
        if folder is not None:
            assert isinstance(folder, bool), "folder should be of type bool"
            query_params["folder"] = folder
        if name:
            assert isinstance(name, str), "name should be of type str"
            query_params["name"] = name
        if recursive is not None:
            assert isinstance(recursive, bool), "recursive should be of type bool"
            query_params["recursive"] = recursive
        if transcription_worker_version is not None:
            warn(
                "`transcription_worker_version` usage is deprecated. Consider using `transcription_worker_run` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            assert isinstance(transcription_worker_version, str | bool), (
                "transcription_worker_version should be of type str or bool"
            )
            if isinstance(transcription_worker_version, bool):
                assert transcription_worker_version is False, (
                    "if of type bool, transcription_worker_version can only be set to False"
                )
            query_params["transcription_worker_version"] = transcription_worker_version
        if transcription_worker_run is not None:
            assert isinstance(transcription_worker_run, str | bool), (
                "transcription_worker_run should be of type str or bool"
            )
            if isinstance(transcription_worker_run, bool):
                assert transcription_worker_run is False, (
                    "if of type bool, transcription_worker_run can only be set to False"
                )
            query_params["transcription_worker_run"] = transcription_worker_run
        if type:
            assert isinstance(type, str), "type should be of type str"
            query_params["type"] = type
        if with_classes is not None:
            assert isinstance(with_classes, bool), "with_classes should be of type bool"
            query_params["with_classes"] = with_classes
        if with_corpus is not None:
            assert isinstance(with_corpus, bool), "with_corpus should be of type bool"
            query_params["with_corpus"] = with_corpus
        if with_has_children is not None:
            assert isinstance(with_has_children, bool), (
                "with_has_children should be of type bool"
            )
            query_params["with_has_children"] = with_has_children
        if with_metadata is not None:
            assert isinstance(with_metadata, bool), (
                "with_metadata should be of type bool"
            )
            query_params["with_metadata"] = with_metadata
        if with_zone is not None:
            assert isinstance(with_zone, bool), "with_zone should be of type bool"
            query_params["with_zone"] = with_zone
        if worker_version is not None:
            warn(
                "`worker_version` usage is deprecated. Consider using `worker_run` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            assert isinstance(worker_version, str | bool), (
                "worker_version should be of type str or bool"
            )
            if isinstance(worker_version, bool):
                assert worker_version is False, (
                    "if of type bool, worker_version can only be set to False"
                )
            query_params["worker_version"] = worker_version
        if worker_run is not None:
            assert isinstance(worker_run, str | bool), (
                "worker_run should be of type str or bool"
            )
            if isinstance(worker_run, bool):
                assert worker_run is False, (
                    "if of type bool, worker_run can only be set to False"
                )
            query_params["worker_run"] = worker_run

        if not self.use_cache:
            return self.api_client.paginate(
                "ListElementChildren", id=element.id, **query_params
            )

        # Checking that we only received query_params handled by the cache
        assert set(query_params.keys()) <= {
            "type",
            "worker_version",
            "worker_run",
        }, (
            "When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'"
        )

        query = CachedElement.select().where(CachedElement.parent_id == element.id)
        if type:
            query = query.where(CachedElement.type == type)
        if worker_version is not None:
            # If worker_version=False, filter by manual worker_version e.g. None
            worker_version_id = worker_version or None
            if worker_version_id:
                query = query.where(
                    CachedElement.worker_version_id == worker_version_id
                )
            else:
                query = query.where(CachedElement.worker_version_id.is_null())

        if worker_run is not None:
            # If worker_run=False, filter by manual worker_run e.g. None
            worker_run_id = worker_run or None
            if worker_run_id:
                query = query.where(CachedElement.worker_run_id == worker_run_id)
            else:
                query = query.where(CachedElement.worker_run_id.is_null())

        return query

    def list_element_parents(
        self,
        element: Element | CachedElement,
        folder: bool | None = None,
        name: str | None = None,
        recursive: bool | None = None,
        transcription_worker_version: str | bool | None = None,
        transcription_worker_run: str | bool | None = None,
        type: str | None = None,
        with_classes: bool | None = None,
        with_corpus: bool | None = None,
        with_metadata: bool | None = None,
        with_has_children: bool | None = None,
        with_zone: bool | None = None,
        worker_version: str | bool | None = None,
        worker_run: str | bool | None = None,
    ) -> Iterable[dict] | Iterable[CachedElement]:
        """
        List parents of an element.

        Warns:
        ----
        The following parameters are **deprecated**:

        - `transcription_worker_version` in favor of `transcription_worker_run`
        - `worker_version` in favor of `worker_run`

        :param element: Child element to find parents of.
        :param folder: Restrict to or exclude elements with folder types.
           This parameter is not supported when caching is enabled.
        :param name: Restrict to elements whose name contain a substring (case-insensitive).
           This parameter is not supported when caching is enabled.
        :param recursive: Look for elements recursively (grand-children, etc.)
           This parameter is not supported when caching is enabled.
        :param transcription_worker_version: **Deprecated** Restrict to elements that have a transcription created by a worker version with this UUID.
           This parameter is not supported when caching is enabled.
        :param transcription_worker_run: Restrict to elements that have a transcription created by a worker run with this UUID.
           This parameter is not supported when caching is enabled.
        :param type: Restrict to elements with a specific type slug
           This parameter is not supported when caching is enabled.
        :param with_classes: Include each element's classifications in the response.
           This parameter is not supported when caching is enabled.
        :param with_corpus: Include each element's corpus in the response.
           This parameter is not supported when caching is enabled.
        :param with_has_children: Include the ``has_children`` attribute in the response,
           indicating if this element has child elements of its own.
           This parameter is not supported when caching is enabled.
        :param with_metadata: Include each element's metadata in the response.
           This parameter is not supported when caching is enabled.
        :param with_zone: Include the ``zone`` attribute in the response,
           holding the element's image and polygon.
           This parameter is not supported when caching is enabled.
        :param worker_version: **Deprecated** Restrict to elements created by a worker version with this UUID.
        :param worker_run: Restrict to elements created by a worker run with this UUID.
        :return: An iterable of dicts from the ``ListElementParents`` API endpoint,
           or an iterable of [CachedElement][arkindex_worker.cache.CachedElement] when caching is enabled.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        query_params = {}
        if folder is not None:
            assert isinstance(folder, bool), "folder should be of type bool"
            query_params["folder"] = folder
        if name:
            assert isinstance(name, str), "name should be of type str"
            query_params["name"] = name
        if recursive is not None:
            assert isinstance(recursive, bool), "recursive should be of type bool"
            query_params["recursive"] = recursive
        if transcription_worker_version is not None:
            warn(
                "`transcription_worker_version` usage is deprecated. Consider using `transcription_worker_run` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            assert isinstance(transcription_worker_version, str | bool), (
                "transcription_worker_version should be of type str or bool"
            )
            if isinstance(transcription_worker_version, bool):
                assert transcription_worker_version is False, (
                    "if of type bool, transcription_worker_version can only be set to False"
                )
            query_params["transcription_worker_version"] = transcription_worker_version
        if transcription_worker_run is not None:
            assert isinstance(transcription_worker_run, str | bool), (
                "transcription_worker_run should be of type str or bool"
            )
            if isinstance(transcription_worker_run, bool):
                assert transcription_worker_run is False, (
                    "if of type bool, transcription_worker_run can only be set to False"
                )
            query_params["transcription_worker_run"] = transcription_worker_run
        if type:
            assert isinstance(type, str), "type should be of type str"
            query_params["type"] = type
        if with_classes is not None:
            assert isinstance(with_classes, bool), "with_classes should be of type bool"
            query_params["with_classes"] = with_classes
        if with_corpus is not None:
            assert isinstance(with_corpus, bool), "with_corpus should be of type bool"
            query_params["with_corpus"] = with_corpus
        if with_has_children is not None:
            assert isinstance(with_has_children, bool), (
                "with_has_children should be of type bool"
            )
            query_params["with_has_children"] = with_has_children
        if with_metadata is not None:
            assert isinstance(with_metadata, bool), (
                "with_metadata should be of type bool"
            )
            query_params["with_metadata"] = with_metadata
        if with_zone is not None:
            assert isinstance(with_zone, bool), "with_zone should be of type bool"
            query_params["with_zone"] = with_zone
        if worker_version is not None:
            warn(
                "`worker_version` usage is deprecated. Consider using `worker_run` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            assert isinstance(worker_version, str | bool), (
                "worker_version should be of type str or bool"
            )
            if isinstance(worker_version, bool):
                assert worker_version is False, (
                    "if of type bool, worker_version can only be set to False"
                )
            query_params["worker_version"] = worker_version
        if worker_run is not None:
            assert isinstance(worker_run, str | bool), (
                "worker_run should be of type str or bool"
            )
            if isinstance(worker_run, bool):
                assert worker_run is False, (
                    "if of type bool, worker_run can only be set to False"
                )
            query_params["worker_run"] = worker_run

        if not self.use_cache:
            return self.api_client.paginate(
                "ListElementParents", id=element.id, **query_params
            )

        # Checking that we only received query_params handled by the cache
        assert set(query_params.keys()) <= {
            "type",
            "worker_version",
            "worker_run",
        }, (
            "When using the local cache, you can only filter by 'type' and/or 'worker_version' and/or 'worker_run'"
        )

        parent_ids = CachedElement.select(CachedElement.parent_id).where(
            CachedElement.id == element.id
        )
        query = CachedElement.select().where(CachedElement.id.in_(parent_ids))
        if type:
            query = query.where(CachedElement.type == type)
        if worker_version is not None:
            # If worker_version=False, filter by manual worker_version e.g. None
            worker_version_id = worker_version or None
            if worker_version_id:
                query = query.where(
                    CachedElement.worker_version_id == worker_version_id
                )
            else:
                query = query.where(CachedElement.worker_version_id.is_null())

        if worker_run is not None:
            # If worker_run=False, filter by manual worker_run e.g. None
            worker_run_id = worker_run or None
            if worker_run_id:
                query = query.where(CachedElement.worker_run_id == worker_run_id)
            else:
                query = query.where(CachedElement.worker_run_id.is_null())

        return query
