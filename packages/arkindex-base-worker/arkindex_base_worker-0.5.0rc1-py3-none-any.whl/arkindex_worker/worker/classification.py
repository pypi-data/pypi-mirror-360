"""
ElementsWorker methods for classifications and ML classes.
"""

from peewee import IntegrityError

from arkindex.exceptions import ErrorResponse
from arkindex_worker import logger
from arkindex_worker.cache import CachedClassification, CachedElement
from arkindex_worker.models import Element
from arkindex_worker.utils import (
    DEFAULT_BATCH_SIZE,
    batch_publication,
    make_batches,
    pluralize,
)


class ClassificationMixin:
    def load_corpus_classes(self):
        """
        Load all ML classes available in the worker's corpus and store them in the ``self.classes`` cache.
        """
        corpus_classes = self.api_client.paginate(
            "ListCorpusMLClasses",
            id=self.corpus_id,
        )
        self.classes = {ml_class["name"]: ml_class["id"] for ml_class in corpus_classes}
        logger.info(
            f"Loaded {len(self.classes)} ML {pluralize('class', len(self.classes))} in corpus ({self.corpus_id})"
        )

    def get_ml_class_id(self, ml_class: str) -> str:
        """
        Return the MLClass ID corresponding to the given class name on a specific corpus.

        If no MLClass exists for this class name, a new one is created.
        :param ml_class: Name of the MLClass.
        :returns: ID of the retrieved or created MLClass.
        """
        if not self.classes:
            self.load_corpus_classes()

        ml_class_id = self.classes.get(ml_class)
        if ml_class_id is None:
            logger.info(f"Creating ML class {ml_class} on corpus {self.corpus_id}")
            try:
                response = self.api_client.request(
                    "CreateMLClass", id=self.corpus_id, body={"name": ml_class}
                )
                ml_class_id = self.classes[ml_class] = response["id"]
                logger.debug(f"Created a new ML class {response['id']}")
            except ErrorResponse as e:
                # Only reload for 400 errors
                if e.status_code != 400:
                    raise

                # Reload and make sure we have the class
                logger.info(
                    f"Unable to create the ML class `{ml_class}`. Refreshing corpus classes cache."
                )
                self.load_corpus_classes()
                assert ml_class in self.classes, (
                    f"Missing ML class {ml_class} even after refreshing."
                )
                ml_class_id = self.classes[ml_class]

        return ml_class_id

    def retrieve_ml_class(self, ml_class_id: str) -> str:
        """
        Retrieve the name of the MLClass from its ID.

        :param ml_class_id: ID of the searched MLClass.
        :return: The MLClass's name
        """
        # Load the corpus' MLclasses if they are not available yet
        if not self.classes:
            self.load_corpus_classes()

        # Filter classes by this ml_class_id
        ml_class_name = next(
            filter(
                lambda x: self.classes[x] == ml_class_id,
                self.classes,
            ),
            None,
        )
        assert ml_class_name is not None, (
            f"Missing class with id ({ml_class_id}) in corpus ({self.corpus_id})"
        )
        return ml_class_name

    def create_classification(
        self,
        element: Element | CachedElement,
        ml_class: str,
        confidence: float,
        high_confidence: bool = False,
    ) -> dict[str, str]:
        """
        Create a classification on the given element through the API.

        :param element: The element to create a classification on.
        :param ml_class: Name of the MLClass to use.
        :param confidence: Confidence score for the classification. Must be between 0 and 1.
        :param high_confidence: Whether or not the classification is of high confidence.
        :returns: The created classification, as returned by the ``CreateClassification`` API endpoint.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        assert ml_class and isinstance(ml_class, str), (
            "ml_class shouldn't be null and should be of type str"
        )
        assert isinstance(confidence, float) and 0 <= confidence <= 1, (
            "confidence shouldn't be null and should be a float in [0..1] range"
        )
        assert isinstance(high_confidence, bool), (
            "high_confidence shouldn't be null and should be of type bool"
        )
        if self.is_read_only:
            logger.warning(
                "Cannot create classification as this worker is in read-only mode"
            )
            return
        try:
            created = self.api_client.request(
                "CreateClassification",
                body={
                    "element": str(element.id),
                    "ml_class": self.get_ml_class_id(ml_class),
                    "worker_run_id": self.worker_run_id,
                    "confidence": confidence,
                    "high_confidence": high_confidence,
                },
            )

            if self.use_cache:
                # Store classification in local cache
                try:
                    to_insert = [
                        {
                            "id": created["id"],
                            "element_id": element.id,
                            "class_name": ml_class,
                            "confidence": created["confidence"],
                            "state": created["state"],
                            "worker_run_id": self.worker_run_id,
                        }
                    ]
                    CachedClassification.insert_many(to_insert).execute()
                except IntegrityError as e:
                    logger.warning(
                        f"Couldn't save created classification in local cache: {e}"
                    )
        except ErrorResponse as e:
            # Detect already existing classification
            if e.status_code == 400 and "non_field_errors" in e.content:
                if (
                    "The fields element, worker_run, ml_class must make a unique set."
                    in e.content["non_field_errors"]
                ):
                    logger.warning(
                        f"This worker run has already set {ml_class} on element {element.id}"
                    )
                else:
                    raise
                return

            # Propagate any other API error
            raise

        return created

    @batch_publication
    def create_classifications(
        self,
        element: Element | CachedElement,
        classifications: list[dict[str, str | float | bool]],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[dict[str, str | float | bool]]:
        """
        Create multiple classifications at once on the given element through the API.

        :param element: The element to create classifications on.
        :param classifications: A list of dicts representing a classification each, with the following keys:

            ml_class (str)
                Required. Name of the MLClass to use.
            confidence (float)
                Required. Confidence score for the classification. Must be between 0 and 1.
            high_confidence (bool)
                Optional. Whether or not the classification is of high confidence.

        :param batch_size: The size of each batch, which will be used to split the publication to avoid API errors.

        :returns: List of created classifications, as returned in the ``classifications`` field by
           the ``CreateClassifications`` API endpoint.
        """
        assert element and isinstance(element, Element | CachedElement), (
            "element shouldn't be null and should be an Element or CachedElement"
        )
        assert classifications and isinstance(classifications, list), (
            "classifications shouldn't be null and should be of type list"
        )

        for index, classification in enumerate(classifications):
            ml_class = classification.get("ml_class")
            assert ml_class and isinstance(ml_class, str), (
                f"Classification at index {index} in classifications: ml_class shouldn't be null and should be of type str"
            )

            confidence = classification.get("confidence")
            assert (
                confidence is not None
                and isinstance(confidence, float)
                and 0 <= confidence <= 1
            ), (
                f"Classification at index {index} in classifications: confidence shouldn't be null and should be a float in [0..1] range"
            )

            high_confidence = classification.get("high_confidence")
            if high_confidence is not None:
                assert isinstance(high_confidence, bool), (
                    f"Classification at index {index} in classifications: high_confidence should be of type bool"
                )

        if self.is_read_only:
            logger.warning(
                "Cannot create classifications as this worker is in read-only mode"
            )
            return

        created_cls = [
            created_cl
            for batch in make_batches(classifications, "classification", batch_size)
            for created_cl in self.api_client.request(
                "CreateClassifications",
                body={
                    "parent": str(element.id),
                    "worker_run_id": self.worker_run_id,
                    "classifications": [
                        {
                            **classification,
                            "ml_class": self.get_ml_class_id(
                                classification["ml_class"]
                            ),
                        }
                        for classification in batch
                    ],
                },
            )["classifications"]
        ]

        for created_cl in created_cls:
            created_cl["class_name"] = self.retrieve_ml_class(created_cl["ml_class"])

        if self.use_cache:
            # Store classifications in local cache
            try:
                to_insert = [
                    {
                        "id": created_cl["id"],
                        "element_id": element.id,
                        "class_name": created_cl.pop("class_name"),
                        "confidence": created_cl["confidence"],
                        "state": created_cl["state"],
                        "worker_run_id": self.worker_run_id,
                    }
                    for created_cl in created_cls
                ]
                CachedClassification.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created classifications in local cache: {e}"
                )

        return created_cls
