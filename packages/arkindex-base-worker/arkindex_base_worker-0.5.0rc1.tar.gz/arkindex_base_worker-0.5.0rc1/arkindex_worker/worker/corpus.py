"""
BaseWorker methods for corpora.
"""

from enum import Enum
from operator import itemgetter
from tempfile import _TemporaryFileWrapper
from uuid import UUID

from arkindex_worker import logger


class CorpusExportState(Enum):
    """
    State of a corpus export.
    """

    Created = "created"
    """
    The corpus export is created, awaiting its processing.
    """

    Running = "running"
    """
    The corpus export is being built.
    """

    Failed = "failed"
    """
    The corpus export failed.
    """

    Done = "done"
    """
    The corpus export ended in success.
    """


class CorpusMixin:
    def download_export(self, export_id: str) -> _TemporaryFileWrapper:
        """
        Download an export.

        :param export_id: UUID of the export to download
        :returns: The downloaded export stored in a temporary file.
        """
        try:
            UUID(export_id)
        except ValueError as e:
            raise ValueError("export_id is not a valid uuid.") from e

        logger.info(f"Downloading export ({export_id})...")
        export: _TemporaryFileWrapper = self.api_client.request(
            "DownloadExport", id=export_id
        )
        logger.info(f"Downloaded export ({export_id}) @ `{export.name}`")
        return export

    def download_latest_export(self) -> _TemporaryFileWrapper:
        """
        Download the latest export in `done` state of the current corpus.

        :returns: The downloaded export stored in a temporary file.
        """
        # List all exports on the corpus
        exports = self.api_client.paginate("ListExports", id=self.corpus_id)

        # Find the latest that is in "done" state
        exports: list[dict] = sorted(
            list(
                filter(
                    lambda export: export["state"] == CorpusExportState.Done.value,
                    exports,
                )
            ),
            key=itemgetter("updated"),
            reverse=True,
        )
        assert len(exports) > 0, (
            f'No available exports found for the corpus ({self.corpus_id}) with state "{CorpusExportState.Done.value.capitalize()}".'
        )

        # Download latest export
        export_id: str = exports[0]["id"]

        return self.download_export(export_id)
