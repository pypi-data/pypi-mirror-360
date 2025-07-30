"""
BaseWorker methods for training.
"""

import functools
from contextlib import contextmanager
from pathlib import Path
from typing import NewType
from uuid import UUID

import requests

from arkindex.exceptions import ErrorResponse
from arkindex_worker import logger
from arkindex_worker.utils import close_delete_file, create_tar_zst_archive

DirPath = NewType("DirPath", Path)
"""Path to a directory"""

Hash = NewType("Hash", str)
"""MD5 Hash"""

FileSize = NewType("FileSize", int)
"""File size"""


@contextmanager
def create_archive(path: DirPath) -> tuple[Path, Hash, FileSize, Hash]:
    """
    Create a tar archive from the files at the given location then compress it to a zst archive.

    Yield its location, its hash, its size and its content's hash.

    :param path: Create a compressed tar archive from the files
    :returns: The location of the created archive, its hash, its size and its content's hash
    """
    assert path.is_dir(), "create_archive needs a directory"

    zst_descriptor, zst_archive, archive_hash, content_hash = create_tar_zst_archive(
        path
    )

    # Get content hash, archive size and hash
    yield zst_archive, content_hash, zst_archive.stat().st_size, archive_hash

    # Remove the zst archive
    close_delete_file(zst_descriptor, zst_archive)


def build_clean_payload(**kwargs):
    """
    Remove null attributes from an API body payload
    """
    return {key: value for key, value in kwargs.items() if value is not None}


def skip_if_read_only(func):
    """
    Return shortly in case the is_read_only property is evaluated to True
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "is_read_only", False):
            logger.warning(
                "Cannot perform this operation as the worker is in read-only mode"
            )
            return
        return func(self, *args, **kwargs)

    return wrapper


class TrainingMixin:
    """
    A mixin helper to create a new model version easily.
    You may use `publish_model_version` to publish a ready model version directly, or
    separately create the model version then publish it (e.g to store training metrics).
    Stores the currently handled model version as `self.model_version`.
    """

    model_version = None

    @property
    def is_finetuning(self) -> bool:
        """
        Whether or not this worker is fine-tuning an existing model version.
        """
        return bool(self.model_version_id)

    @skip_if_read_only
    def publish_model_version(
        self,
        model_path: DirPath,
        model_id: str,
        tag: str | None = None,
        description: str | None = None,
        configuration: dict | None = None,
        parent: str | UUID | None = None,
    ):
        """
        Publish a unique version of a model in Arkindex, identified by its hash.
        In case the `create_model_version` method has been called, reuses that model
        instead of creating a new one.

        :param model_path: Path to the directory containing the model version's files.
        :param model_id: ID of the model
        :param tag: Tag of the model version
        :param description: Description of the model version
        :param configuration: Configuration of the model version
        :param parent: ID of the parent model version
        """

        configuration = configuration or {}
        if not self.model_version:
            self.create_model_version(
                model_id=model_id,
                tag=tag,
                description=description,
                configuration=configuration,
                parent=parent,
            )

        elif tag or description or configuration or parent:
            assert self.model_version.get("model_id") == model_id, (
                "Given `model_id` does not match the current model version"
            )
            # If any attribute field has been defined, PATCH the current model version
            self.update_model_version(
                tag=tag,
                description=description,
                configuration=configuration,
                parent=parent,
            )

        # Create the zst archive, get its hash and size
        # Validate the model version
        with create_archive(path=model_path) as (
            path_to_archive,
            hash,
            size,
            archive_hash,
        ):
            # Create a new model version with hash and size
            self.upload_to_s3(archive_path=path_to_archive)

            current_version_id = self.model_version["id"]
            # Mark the model as valid
            self.validate_model_version(
                size=size,
                hash=hash,
                archive_hash=archive_hash,
            )
            if self.model_version["id"] != current_version_id and (
                tag or description or configuration or parent
            ):
                logger.warning(
                    "Updating the existing available model version with the given attributes."
                )
                self.update_model_version(
                    tag=tag,
                    description=description,
                    configuration=configuration,
                    parent=parent,
                )

    @skip_if_read_only
    def create_model_version(
        self,
        model_id: str,
        tag: str | None = None,
        description: str | None = None,
        configuration: dict | None = None,
        parent: str | UUID | None = None,
    ):
        """
        Create a new version of the specified model with its base attributes.
        Once successfully created, the model version is accessible via `self.model_version`.

        :param tag: Tag of the model version
        :param description: Description of the model version
        :param configuration: Configuration of the model version
        :param parent: ID of the parent model version
        """
        assert not self.model_version, "A model version has already been created."

        configuration = configuration or {}
        self.model_version = self.api_client.request(
            "CreateModelVersion",
            id=model_id,
            body=build_clean_payload(
                tag=tag,
                description=description,
                configuration=configuration,
                parent=parent,
            ),
        )

        logger.info(
            f"Model version ({self.model_version['id']}) was successfully created"
        )

    @skip_if_read_only
    def update_model_version(
        self,
        tag: str | None = None,
        description: str | None = None,
        configuration: dict | None = None,
        parent: str | UUID | None = None,
    ):
        """
        Update the current model version with the given attributes.

        :param tag: Tag of the model version
        :param description: Description of the model version
        :param configuration: Configuration of the model version
        :param parent: ID of the parent model version
        """
        assert self.model_version, "No model version has been created yet."
        self.model_version = self.api_client.request(
            "UpdateModelVersion",
            id=self.model_version["id"],
            body=build_clean_payload(
                tag=tag,
                description=description,
                configuration=configuration,
                parent=parent,
            ),
        )
        logger.info(
            f"Model version ({self.model_version['id']}) was successfully updated"
        )

    @skip_if_read_only
    def upload_to_s3(self, archive_path: Path) -> None:
        """
        Upload the archive of the model's files to an Amazon s3 compatible storage
        """

        assert self.model_version, (
            "You must create the model version before uploading an archive."
        )
        assert self.model_version["state"] != "Available", (
            "The model is already marked as available."
        )

        s3_put_url = self.model_version.get("s3_put_url")
        assert s3_put_url, (
            "S3 PUT URL is not set, please ensure you have the right to validate a model version."
        )

        logger.info("Uploading to s3...")
        # Upload the archive on s3
        with archive_path.open("rb") as archive:
            r = requests.put(
                url=s3_put_url,
                data=archive,
                headers={"Content-Type": "application/zstd"},
            )
        r.raise_for_status()

    @skip_if_read_only
    def validate_model_version(
        self,
        hash: str,
        size: int,
        archive_hash: str,
    ):
        """
        Sets the model version as `Available`, once its archive has been uploaded to S3.

        :param hash: MD5 hash of the files contained in the archive
        :param size: The size of the uploaded archive
        :param archive_hash: MD5 hash of the uploaded archive
        """
        assert self.model_version, (
            "You must create the model version and upload its archive before validating it."
        )
        try:
            self.model_version = self.api_client.request(
                "PartialUpdateModelVersion",
                id=self.model_version["id"],
                body={
                    "state": "available",
                    "size": size,
                    "hash": hash,
                    "archive_hash": archive_hash,
                },
            )
        except ErrorResponse as e:
            model_version = e.content
            if not model_version or "id" not in model_version:
                raise e

            logger.warning(
                f"An available model version exists with hash {hash}, using it instead of the pending version."
            )
            pending_version_id = self.model_version["id"]
            logger.warning("Removing the pending model version.")
            try:
                self.api_client.request("DestroyModelVersion", id=pending_version_id)
            except ErrorResponse as e:
                msg = getattr(e, "content", str(e))
                logger.error(
                    f"An error occurred removing the pending version {pending_version_id}: {msg}."
                )

            logger.info("Retrieving the existing model version.")
            existing_version_id = model_version["id"].pop()
            try:
                self.model_version = self.api_client.request(
                    "RetrieveModelVersion", id=existing_version_id
                )
            except ErrorResponse as e:
                logger.error(
                    f"An error occurred retrieving the existing version {existing_version_id}: {e.status_code} - {e.content}."
                )
                raise

        logger.info(f"Model version {self.model_version['id']} is now available.")
