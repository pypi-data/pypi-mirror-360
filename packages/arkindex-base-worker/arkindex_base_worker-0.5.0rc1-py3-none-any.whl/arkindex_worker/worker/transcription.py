"""
ElementsWorker methods for transcriptions.
"""

from collections.abc import Iterable
from enum import Enum
from warnings import warn

from peewee import IntegrityError

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement, CachedTranscription
from arkindex_worker.models import Element
from arkindex_worker.utils import DEFAULT_BATCH_SIZE, batch_publication, make_batches


class TextOrientation(Enum):
    """
    Orientation of a transcription's text.
    """

    HorizontalLeftToRight = "horizontal-lr"
    """
    The text is read from top to bottom then left to right.
    This is the default when no orientation is specified.
    """

    HorizontalRightToLeft = "horizontal-rl"
    """
    The text is read from top to bottom then right to left.
    """

    VerticalRightToLeft = "vertical-rl"
    """
    The text is read from right to left then top to bottom.
    """

    VerticalLeftToRight = "vertical-lr"
    """
    The text is read from left to right then top to bottom.
    """


class TranscriptionMixin:
    def create_transcription(
        self,
        element: Element | CachedElement,
        text: str,
        confidence: float,
        orientation: TextOrientation = TextOrientation.HorizontalLeftToRight,
    ) -> dict[str, str | float] | None:
        """
        Create a transcription on the given element through the API.

        :param element: Element to create a transcription on.
        :param text: Text of the transcription.
        :param confidence: Confidence score, between 0 and 1.
        :param orientation: Orientation of the transcription's text.
        :returns: A dict as returned by the ``CreateTranscription`` API endpoint,
           or None if the worker is in read-only mode.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        assert text and isinstance(text, str), (
            "text shouldn't be null and should be of type str"
        )
        assert orientation and isinstance(orientation, TextOrientation), (
            "orientation shouldn't be null and should be of type TextOrientation"
        )
        assert isinstance(confidence, float) and 0 <= confidence <= 1, (
            "confidence shouldn't be null and should be a float in [0..1] range"
        )

        if self.is_read_only:
            logger.warning(
                "Cannot create transcription as this worker is in read-only mode"
            )
            return

        created = self.api_client.request(
            "CreateTranscription",
            id=element.id,
            body={
                "text": text,
                "worker_run_id": self.worker_run_id,
                "confidence": confidence,
                "orientation": orientation.value,
            },
        )

        if self.use_cache:
            # Store transcription in local cache
            try:
                to_insert = [
                    {
                        "id": created["id"],
                        "element_id": element.id,
                        "text": created["text"],
                        "confidence": created["confidence"],
                        "orientation": created["orientation"],
                        "worker_run_id": self.worker_run_id,
                    }
                ]
                CachedTranscription.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcription in local cache: {e}"
                )

        return created

    @batch_publication
    def create_transcriptions(
        self,
        transcriptions: list[dict[str, str | float | TextOrientation | None]],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[dict[str, str | float]]:
        """
        Create multiple transcriptions at once on existing elements through the API,
        and creates [CachedTranscription][arkindex_worker.cache.CachedTranscription] instances if cache support is enabled.

        :param transcriptions: A list of dicts representing a transcription each, with the following keys:

            element_id (str)
                Required. UUID of the element to create this transcription on.
            text (str)
                Required. Text of the transcription.
            confidence (float)
                Required. Confidence score between 0 and 1.
            orientation (TextOrientation)
                Optional. Orientation of the transcription's text.

        :param batch_size: The size of each batch, which will be used to split the publication to avoid API errors.

        :returns: A list of dicts as returned in the ``transcriptions`` field by the ``CreateTranscriptions`` API endpoint.
        """

        assert transcriptions and isinstance(transcriptions, list), (
            "transcriptions shouldn't be null and should be of type list"
        )

        # Create shallow copies of every transcription to avoid mutating the original payload
        transcriptions_payload = list(map(dict, transcriptions))

        for index, transcription in enumerate(transcriptions_payload):
            element_id = transcription.get("element_id")
            assert element_id and isinstance(element_id, str), (
                f"Transcription at index {index} in transcriptions: element_id shouldn't be null and should be of type str"
            )

            text = transcription.get("text")
            assert text and isinstance(text, str), (
                f"Transcription at index {index} in transcriptions: text shouldn't be null and should be of type str"
            )

            confidence = transcription.get("confidence")
            assert (
                confidence is not None
                and isinstance(confidence, float)
                and 0 <= confidence <= 1
            ), (
                f"Transcription at index {index} in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
            )

            orientation = transcription.get(
                "orientation", TextOrientation.HorizontalLeftToRight
            )
            assert orientation and isinstance(orientation, TextOrientation), (
                f"Transcription at index {index} in transcriptions: orientation shouldn't be null and should be of type TextOrientation"
            )
            if orientation:
                transcription["orientation"] = orientation.value

        if self.is_read_only:
            logger.warning(
                "Cannot create transcription as this worker is in read-only mode"
            )
            return

        created_trs = [
            created_tr
            for batch in make_batches(
                transcriptions_payload, "transcription", batch_size
            )
            for created_tr in self.api_client.request(
                "CreateTranscriptions",
                body={
                    "worker_run_id": self.worker_run_id,
                    "transcriptions": batch,
                },
            )["transcriptions"]
        ]

        if self.use_cache:
            # Store transcriptions in local cache
            try:
                to_insert = [
                    {
                        "id": created_tr["id"],
                        "element_id": created_tr["element_id"],
                        "text": created_tr["text"],
                        "confidence": created_tr["confidence"],
                        "orientation": created_tr["orientation"],
                        "worker_run_id": self.worker_run_id,
                    }
                    for created_tr in created_trs
                ]
                CachedTranscription.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcriptions in local cache: {e}"
                )

        return created_trs

    @batch_publication
    def create_element_transcriptions(
        self,
        element: Element | CachedElement,
        sub_element_type: str,
        transcriptions: list[dict[str, str | float]],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> dict[str, str | bool]:
        """
        Create multiple elements and transcriptions at once on a single parent element through the API.

        :param element: Element to create elements and transcriptions on.
        :param sub_element_type: Slug of the element type to use for the new elements.
        :param transcriptions: A list of dicts representing an element and transcription each, with the following keys:

            polygon (list(list(int or float)))
                Required. Polygon of the element.
            text (str)
                Required. Text of the transcription.
            confidence (float)
                Required. Confidence score between 0 and 1.
            orientation ([TextOrientation][arkindex_worker.worker.transcription.TextOrientation])
                Optional. Orientation of the transcription's text.
            element_confidence (float)
                Optional. Confidence score of the element between 0 and 1.

        :param batch_size: The size of each batch, which will be used to split the publication to avoid API errors.

        :returns: A list of dicts as returned by the ``CreateElementTranscriptions`` API endpoint.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        assert sub_element_type and isinstance(sub_element_type, str), (
            "sub_element_type shouldn't be null and should be of type str"
        )
        assert transcriptions and isinstance(transcriptions, list), (
            "transcriptions shouldn't be null and should be of type list"
        )

        # Create shallow copies of every transcription to avoid mutating the original payload
        transcriptions_payload = list(map(dict, transcriptions))

        for index, transcription in enumerate(transcriptions_payload):
            text = transcription.get("text")
            assert text and isinstance(text, str), (
                f"Transcription at index {index} in transcriptions: text shouldn't be null and should be of type str"
            )

            confidence = transcription.get("confidence")
            assert (
                confidence is not None
                and isinstance(confidence, float)
                and 0 <= confidence <= 1
            ), (
                f"Transcription at index {index} in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"
            )

            orientation = transcription.get(
                "orientation", TextOrientation.HorizontalLeftToRight
            )
            assert orientation and isinstance(orientation, TextOrientation), (
                f"Transcription at index {index} in transcriptions: orientation shouldn't be null and should be of type TextOrientation"
            )
            if orientation:
                transcription["orientation"] = orientation.value

            polygon = transcription.get("polygon")
            assert polygon and isinstance(polygon, list), (
                f"Transcription at index {index} in transcriptions: polygon shouldn't be null and should be of type list"
            )
            assert len(polygon) >= 3, (
                f"Transcription at index {index} in transcriptions: polygon should have at least three points"
            )
            assert all(
                isinstance(point, list) and len(point) == 2 for point in polygon
            ), (
                f"Transcription at index {index} in transcriptions: polygon points should be lists of two items"
            )
            assert all(
                isinstance(coord, int | float) for point in polygon for coord in point
            ), (
                f"Transcription at index {index} in transcriptions: polygon points should be lists of two numbers"
            )

            element_confidence = transcription.get("element_confidence")
            assert element_confidence is None or (
                isinstance(element_confidence, float) and 0 <= element_confidence <= 1
            ), (
                f"Transcription at index {index} in transcriptions: element_confidence should be either null or a float in [0..1] range"
            )

        if self.is_read_only:
            logger.warning(
                "Cannot create transcriptions as this worker is in read-only mode"
            )
            return

        annotations = [
            annotation
            for batch in make_batches(
                transcriptions_payload, "transcription", batch_size
            )
            for annotation in self.api_client.request(
                "CreateElementTranscriptions",
                id=element.id,
                body={
                    "element_type": sub_element_type,
                    "worker_run_id": self.worker_run_id,
                    "transcriptions": batch,
                    "return_elements": True,
                },
            )
        ]

        for annotation in annotations:
            if annotation["created"]:
                logger.debug(
                    f"A sub_element of {element.id} with type {sub_element_type} was created during transcriptions bulk creation"
                )

        if self.use_cache:
            # Store transcriptions and their associated element (if created) in local cache
            created_ids = set()
            elements_to_insert = []
            transcriptions_to_insert = []
            for index, annotation in enumerate(annotations):
                transcription = transcriptions[index]

                if annotation["element_id"] not in created_ids:
                    # Even if the API says the element already existed in the DB,
                    # we need to check if it is available in the local cache.
                    # Peewee does not have support for SQLite's INSERT OR IGNORE,
                    # so we do the check here, element by element.
                    try:
                        CachedElement.get_by_id(annotation["element_id"])
                    except CachedElement.DoesNotExist:
                        elements_to_insert.append(
                            {
                                "id": annotation["element_id"],
                                "parent_id": element.id,
                                "type": sub_element_type,
                                "image_id": element.image_id,
                                "polygon": transcription["polygon"],
                                "worker_run_id": self.worker_run_id,
                                "confidence": transcription.get("element_confidence"),
                            }
                        )

                    created_ids.add(annotation["element_id"])

                transcriptions_to_insert.append(
                    {
                        "id": annotation["id"],
                        "element_id": annotation["element_id"],
                        "text": transcription["text"],
                        "confidence": transcription["confidence"],
                        "orientation": transcription.get(
                            "orientation", TextOrientation.HorizontalLeftToRight
                        ).value,
                        "worker_run_id": self.worker_run_id,
                    }
                )

            try:
                CachedElement.insert_many(elements_to_insert).execute()
                CachedTranscription.insert_many(transcriptions_to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcriptions in local cache: {e}"
                )

        return annotations

    def list_transcriptions(
        self,
        element: Element | CachedElement,
        element_type: str | None = None,
        recursive: bool | None = None,
        worker_version: str | bool | None = None,
        worker_run: str | bool | None = None,
    ) -> Iterable[dict] | Iterable[CachedTranscription]:
        """
        List transcriptions on an element.

        Warns:
        ----
        The following parameters are **deprecated**:

        - `worker_version` in favor of `worker_run`

        :param element: The element to list transcriptions on.
        :param element_type: Restrict to transcriptions whose elements have an element type with this slug.
        :param recursive: Include transcriptions of any descendant of this element, recursively.
        :param worker_version: **Deprecated** Restrict to transcriptions created by a worker version with this UUID. Set to False to look for manually created transcriptions.
        :param worker_run: Restrict to transcriptions created by a worker run with this UUID. Set to False to look for manually created transcriptions.
        :returns: An iterable of dicts representing each transcription,
           or an iterable of CachedTranscription when cache support is enabled.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        query_params = {}
        if element_type:
            assert isinstance(element_type, str), "element_type should be of type str"
            query_params["element_type"] = element_type
        if recursive is not None:
            assert isinstance(recursive, bool), "recursive should be of type bool"
            query_params["recursive"] = recursive
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
                "ListTranscriptions", id=element.id, **query_params
            )

        if not recursive:
            # In this case we don't have to return anything, it's easier to use an
            # impossible condition (False) rather than filtering by type for nothing
            if element_type and element_type != element.type:
                return CachedTranscription.select().where(False)
            transcriptions = CachedTranscription.select().where(
                CachedTranscription.element_id == element.id
            )
        else:
            base_case = (
                CachedElement.select()
                .where(CachedElement.id == element.id)
                .cte("base", recursive=True)
            )
            recursive = CachedElement.select().join(
                base_case, on=(CachedElement.parent_id == base_case.c.id)
            )
            cte = base_case.union_all(recursive)
            transcriptions = (
                CachedTranscription.select()
                .join(cte, on=(CachedTranscription.element_id == cte.c.id))
                .with_cte(cte)
            )

            if element_type:
                transcriptions = transcriptions.where(cte.c.type == element_type)

        if worker_version is not None:
            # If worker_version=False, filter by manual worker_version e.g. None
            worker_version_id = worker_version or None
            if worker_version_id:
                transcriptions = transcriptions.where(
                    CachedTranscription.worker_version_id == worker_version_id
                )
            else:
                transcriptions = transcriptions.where(
                    CachedTranscription.worker_version_id.is_null()
                )

        if worker_run is not None:
            # If worker_run=False, filter by manual worker_run e.g. None
            worker_run_id = worker_run or None
            if worker_run_id:
                transcriptions = transcriptions.where(
                    CachedTranscription.worker_run_id == worker_run_id
                )
            else:
                transcriptions = transcriptions.where(
                    CachedTranscription.worker_run_id.is_null()
                )

        return transcriptions
