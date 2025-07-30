"""
BaseWorker methods for tasks.
"""

import uuid
from collections.abc import Iterator

from arkindex.compat import DownloadedFile
from arkindex_worker.models import Artifact


class TaskMixin:
    def list_artifacts(self, task_id: uuid.UUID) -> Iterator[Artifact]:
        """
        List artifacts associated to a task.

        :param task_id: Task ID to find artifacts from.
        :returns: An iterator of ``Artifact`` objects built from the ``ListArtifacts`` API endpoint.
        """
        assert task_id and isinstance(task_id, uuid.UUID), (
            "task_id shouldn't be null and should be an UUID"
        )

        results = self.api_client.request("ListArtifacts", id=task_id)

        return map(Artifact, results)

    def download_artifact(
        self, task_id: uuid.UUID, artifact: Artifact
    ) -> DownloadedFile:
        """
        Download an artifact content.

        :param task_id: Task ID the Artifact is from.
        :param artifact: Artifact to download content from.
        :returns: A temporary file containing the ``Artifact`` downloaded from the ``DownloadArtifact`` API endpoint.
        """
        assert task_id and isinstance(task_id, uuid.UUID), (
            "task_id shouldn't be null and should be an UUID"
        )
        assert artifact and isinstance(artifact, Artifact), (
            "artifact shouldn't be null and should be an Artifact"
        )

        return self.api_client.request(
            "DownloadArtifact", id=task_id, path=artifact.path
        )
