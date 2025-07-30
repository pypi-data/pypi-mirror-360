"""Tooled Python worker to create a transcription on Arkindex elements"""

import logging

from arkindex_worker.models import Element
from arkindex_worker.worker import ElementsWorker

# Initialize the logger to provide feedback about the worker's execution to the final user
logging.basicConfig(
    format="%(asctime)s %(levelname)s/%(name)s: %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Create a worker inheriting from the `ElementsWorker` class provided by the `arkindex-base-worker` package
class BasicWorker(ElementsWorker):
    def process_element(self, element: Element) -> None:
        """Process a single Arkindex element at once and publish a simple transcription on it.

        :param Element element: The element currently being processed from the element list
        """
        try:
            # Create the "Hello world!" transcription on the current element
            # Helper: `TranscriptionMixin.create_transcription` from the `arkindex-base-worker` package
            transcription = self.create_transcription(
                element=element,
                text="Hello world!",
                confidence=1.0,
            )

            # Output feedback when a transcription is successfully created
            logger.info(
                f"A transcription with the ID {transcription['id']} was successfully created on element {element.id}."
            )

        except Exception as e:
            # Output feedback when failing to create a transcription
            logger.error(
                f"Failed to create a transcription on element {element.id}: {e}"
            )


def main() -> None:
    BasicWorker(
        description="Tooled Python worker to create a transcription on Arkindex elements"
    ).run()


if __name__ == "__main__":
    main()
