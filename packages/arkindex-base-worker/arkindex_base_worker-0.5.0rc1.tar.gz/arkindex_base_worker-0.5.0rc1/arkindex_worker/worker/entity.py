"""
ElementsWorker methods for entities.
"""

from operator import itemgetter
from typing import TypedDict
from warnings import warn

from peewee import IntegrityError

from arkindex.exceptions import ErrorResponse
from arkindex_worker import logger
from arkindex_worker.cache import (
    CachedTranscriptionEntity,
    unsupported_cache,
)
from arkindex_worker.models import Transcription
from arkindex_worker.utils import pluralize


class Entity(TypedDict):
    type_id: str
    length: int
    offset: int
    confidence: float | None


class MissingEntityType(Exception):
    """
    Raised when the specified entity type was not found in the corpus and
    the worker cannot create it.
    """


class EntityMixin:
    def list_corpus_entity_types(self):
        """
        Loads available entity types in corpus.
        """
        self.entity_types = {
            entity_type["name"]: entity_type["id"]
            for entity_type in self.api_client.paginate(
                "ListCorpusEntityTypes", id=self.corpus_id
            )
        }
        count = len(self.entity_types)
        logger.info(
            f"Loaded {count} entity {pluralize('type', count)} in corpus ({self.corpus_id})."
        )

    @unsupported_cache
    def create_entity_type(self, name: str) -> None:
        """
        Create an entity type on the given corpus.

        :param name: Name of the entity type.
        """
        assert name and isinstance(name, str), (
            "name shouldn't be null and should be of type str"
        )

        try:
            entity_type = self.api_client.request(
                "CreateEntityType",
                body={
                    "name": name,
                    "corpus": self.corpus_id,
                },
            )
            self.entity_types[name] = entity_type["id"]
            logger.info(f"Created a new entity type with name `{name}`.")
        except ErrorResponse as e:
            # Only reload for 400 errors
            if e.status_code != 400:
                raise

            # Reload and make sure we have the element type now
            logger.warning(
                f"Unable to create the entity type `{name}`. Refreshing corpus entity types cache."
            )
            self.list_corpus_entity_types()
            assert name in self.entity_types, (
                f"Missing entity type `{name}` even after refreshing."
            )

    def check_required_entity_types(
        self, entity_types: list[str], create_missing: bool = True
    ) -> None:
        """
        Check that every entity type needed is available in the corpus.
        Missing ones may be created automatically if needed.

        :param entity_types: Entity type names to search.
        :param create_missing: Whether the missing types should be created. Defaults to True.
        :raises MissingEntityType: When an entity type is missing and cannot be created.
        """
        assert entity_types and isinstance(entity_types, list), (
            "entity_types shouldn't be null and should be of type list"
        )

        for index, entity_type in enumerate(entity_types):
            assert isinstance(entity_type, str), (
                f"Entity type at index {index} in entity_types: Should be of type str"
            )

        assert create_missing is not None and isinstance(create_missing, bool), (
            "create_missing shouldn't be null and should be of type bool"
        )

        if not self.entity_types:
            self.list_corpus_entity_types()

        for entity_type in entity_types:
            # Do nothing if the type already exists
            if entity_type in self.entity_types:
                continue

            # Do not create missing if not requested
            if not create_missing:
                raise MissingEntityType(
                    f"Entity type `{entity_type}` was not in the corpus."
                )

            # Create the type if non-existent
            self.create_entity_type(entity_type)

    def create_transcription_entity(
        self,
        transcription: Transcription,
        type_id: str,
        offset: int,
        length: int,
        confidence: float | None = None,
    ) -> dict[str, str | int] | None:
        """
        Create an entity on an existing transcription.
        If cache support is enabled, a `CachedTranscriptionEntity` will also be created.

        :param transcription: Transcription to create the entity on.
        :param type_id: UUID of the entity type.
        :param offset: Starting position of the entity in the transcription's text,
           as a 0-based index.
        :param length: Length of the entity in the transcription's text.
        :param confidence: Optional confidence score between 0 or 1.
        :returns: A dict as returned by the ``CreateTranscriptionEntity`` API endpoint,
           or None if the worker is in read-only mode.
        """
        assert transcription and isinstance(transcription, Transcription), (
            "transcription shouldn't be null and should be a Transcription"
        )
        assert type_id and isinstance(type_id, str), (
            "type_id shouldn't be null and should be of type str"
        )
        assert offset is not None and isinstance(offset, int) and offset >= 0, (
            "offset shouldn't be null and should be a positive integer"
        )
        assert length is not None and isinstance(length, int) and length > 0, (
            "length shouldn't be null and should be a strictly positive integer"
        )
        assert (
            confidence is None or isinstance(confidence, float) and 0 <= confidence <= 1
        ), "confidence should be null or a float in [0..1] range"
        if self.is_read_only:
            logger.warning(
                "Cannot create transcription entity as this worker is in read-only mode"
            )
            return

        body = {
            "type_id": type_id,
            "length": length,
            "offset": offset,
            "worker_run_id": self.worker_run_id,
        }
        if confidence is not None:
            body["confidence"] = confidence

        tr_entity = self.api_client.request(
            "CreateTranscriptionEntity",
            id=transcription.id,
            body=body,
        )

        if self.use_cache:
            # Store transcription entity in local cache
            try:
                CachedTranscriptionEntity.create(
                    transcription=transcription.id,
                    type=tr_entity["type"]["name"],
                    offset=offset,
                    length=length,
                    worker_run_id=self.worker_run_id,
                    confidence=confidence,
                )
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcription entity in local cache: {e}"
                )

        return tr_entity

    @unsupported_cache
    def create_transcription_entities(
        self,
        transcription: Transcription,
        entities: list[Entity],
    ) -> list[dict[str, str]]:
        """
        Create multiple entities on a transcription in a single API request.

        :param transcription: Transcription to create the entity on.
        :param entities: List of dicts, one per element. Each dict can have the following keys:

            type_id (str)
               Required. ID of the EntityType of the entity.

            length (int)
               Required. Length of the entity in the transcription's text.

            offset (int)
               Required. Starting position of the entity in the transcription's text, as a 0-based index.

            confidence (float or None)
                Optional confidence score, between 0.0 and 1.0.

        :return: List of strings, holding the UUID of each created object.
        """
        assert transcription and isinstance(transcription, Transcription), (
            "transcription shouldn't be null and should be of type Transcription"
        )

        assert entities and isinstance(entities, list), (
            "entities shouldn't be null and should be of type list"
        )

        for index, entity in enumerate(entities):
            assert isinstance(entity, dict), (
                f"Entity at index {index} in entities: Should be of type dict"
            )

            type_id = entity.get("type_id")
            assert type_id and isinstance(type_id, str), (
                f"Entity at index {index} in entities: type_id shouldn't be null and should be of type str"
            )

            offset = entity.get("offset")
            assert offset is not None and isinstance(offset, int) and offset >= 0, (
                f"Entity at index {index} in entities: offset shouldn't be null and should be a positive integer"
            )

            length = entity.get("length")
            assert length is not None and isinstance(length, int) and length > 0, (
                f"Entity at index {index} in entities: length shouldn't be null and should be a strictly positive integer"
            )

            confidence = entity.get("confidence")
            assert confidence is None or (
                isinstance(confidence, float) and 0 <= confidence <= 1
            ), (
                f"Entity at index {index} in entities: confidence should be None or a float in [0..1] range"
            )

        assert len(entities) == len(
            set(map(itemgetter("offset", "length", "type_id"), entities))
        ), "entities should be unique"

        if self.is_read_only:
            logger.warning(
                "Cannot create transcription entities in bulk as this worker is in read-only mode"
            )
            return

        created_tr_entities = self.api_client.request(
            "CreateTranscriptionEntities",
            id=transcription.id,
            body={
                "worker_run_id": self.worker_run_id,
                "transcription_entities": entities,
            },
        )["transcription_entities"]

        return created_tr_entities

    def list_transcription_entities(
        self,
        transcription: Transcription,
        worker_version: str | bool | None = None,
        worker_run: str | bool | None = None,
    ):
        """
        List existing entities on a transcription
        This method does not support cache

        Warns:
        ----
        The following parameters are **deprecated**:

        - `worker_version` in favor of `worker_run`

        :param transcription: The transcription to list entities on.
        :param worker_version: **Deprecated** Restrict to entities created by a worker version with this UUID. Set to False to look for manually created entities.
        :param worker_run: Restrict to entities created by a worker run with this UUID. Set to False to look for manually created entities.
        """
        query_params = {}
        assert transcription and isinstance(transcription, Transcription), (
            "transcription shouldn't be null and should be a Transcription"
        )

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

        return self.api_client.paginate(
            "ListTranscriptionEntities", id=transcription.id, **query_params
        )
