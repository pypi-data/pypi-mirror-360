import hashlib
import inspect
import logging
import os
import tarfile
import tempfile
from collections.abc import Callable, Generator
from itertools import islice
from pathlib import Path
from typing import Any

import zstandard as zstd

logger = logging.getLogger(__name__)


def pluralize(singular: str, count: int) -> str:
    """Pluralize a noun, if necessary, using simplified rules of English pluralization and a list of exceptions.

    :param str singular: A singular noun describing an object
    :param int count: The object count, to determine whether to pluralize or not
    :return str: The noun in its singular or plural form
    """
    if count == 1:
        return singular

    some_exceptions = {
        "child": "children",
        "class": "classes",
        "entity": "entities",
        "metadata": "metadata",
    }
    if singular in some_exceptions:
        return some_exceptions[singular]

    return singular + "s"


MANUAL_SOURCE = "manual"


def parse_source_id(value: str) -> bool | str | None:
    """
    Parse a UUID argument (Worker Version, Worker Run, ...) to use it directly in the API.
    Arkindex API filters generally expect `False` to filter manual sources.
    """
    if value == MANUAL_SOURCE:
        return False
    return value or None


CHUNK_SIZE = 1024
"""Chunk Size used for ZSTD compression"""


def decompress_zst_archive(compressed_archive: Path) -> tuple[int, Path]:
    """
    Decompress a ZST-compressed tar archive in data dir. The tar archive is not extracted.
    This returns the path to the archive and the file descriptor.

    Beware of closing the file descriptor explicitly or the main
    process will keep the memory held even if the file is deleted.

    :param compressed_archive: Path to the target ZST-compressed archive
    :return: File descriptor and path to the uncompressed tar archive
    """
    dctx = zstd.ZstdDecompressor()
    archive_fd, archive_path = tempfile.mkstemp(suffix=".tar")
    archive_path = Path(archive_path)

    logger.debug(f"Uncompressing file to {archive_path}")
    try:
        with (
            compressed_archive.open("rb") as compressed,
            archive_path.open("wb") as decompressed,
        ):
            dctx.copy_stream(compressed, decompressed)
        logger.debug(f"Successfully uncompressed archive {compressed_archive}")
    except zstd.ZstdError as e:
        raise Exception(f"Couldn't uncompressed archive: {e}") from e

    return archive_fd, archive_path


def extract_tar_archive(archive_path: Path, destination: Path):
    """
    Extract the tar archive's content to a specific destination

    :param archive_path: Path to the archive
    :param destination: Path where the archive's data will be extracted
    """
    try:
        with tarfile.open(archive_path) as tar_archive:
            tar_archive.extractall(destination)
    except tarfile.ReadError as e:
        raise Exception(f"Couldn't handle the decompressed Tar archive: {e}") from e


def extract_tar_zst_archive(
    compressed_archive: Path, destination: Path
) -> tuple[int, Path]:
    """
    Extract a ZST-compressed tar archive's content to a specific destination

    :param compressed_archive: Path to the target ZST-compressed archive
    :param destination: Path where the archive's data will be extracted
    :return: File descriptor and path to the uncompressed tar archive
    """

    archive_fd, archive_path = decompress_zst_archive(compressed_archive)
    extract_tar_archive(archive_path, destination)

    return archive_fd, archive_path


def close_delete_file(file_descriptor: int, file_path: Path):
    """
    Close the file descriptor of the file and delete the file

    :param file_descriptor: File descriptor of the archive
    :param file_path: Path to the archive
    """
    try:
        os.close(file_descriptor)
        file_path.unlink()
    except OSError as e:
        logger.warning(f"Unable to delete file {file_path}: {e}")


def zstd_compress(
    source: Path, destination: Path | None = None
) -> tuple[int | None, Path, str]:
    """Compress a file using the Zstandard compression algorithm.

    :param source: Path to the file to compress.
    :param destination: Optional path for the created ZSTD archive. A tempfile will be created if this is omitted.
    :return: The file descriptor (if one was created) and path to the compressed file, hash of its content.
    """
    compressor = zstd.ZstdCompressor(level=3)
    archive_hasher = hashlib.md5()

    # Parse destination and create a tmpfile if none was specified
    file_d, destination = (
        tempfile.mkstemp(prefix="teklia-", suffix=".tar.zst")
        if destination is None
        else (None, destination)
    )
    destination = Path(destination)
    logger.debug(f"Compressing file to {destination}")

    try:
        with destination.open("wb") as archive_file, source.open("rb") as model_data:
            for model_chunk in iter(lambda: model_data.read(CHUNK_SIZE), b""):
                compressed_chunk = compressor.compress(model_chunk)
                archive_hasher.update(compressed_chunk)
                archive_file.write(compressed_chunk)
        logger.debug(f"Successfully compressed {source}")
    except zstd.ZstdError as e:
        raise Exception(f"Couldn't compress archive: {e}") from e
    return file_d, destination, archive_hasher.hexdigest()


def create_tar_archive(
    path: Path, destination: Path | None = None
) -> tuple[int | None, Path, str]:
    """Create a tar archive using the content at specified location.

    :param path: Path to the file to archive
    :param destination: Optional path for the created TAR archive. A tempfile will be created if this is omitted.
    :return: The file descriptor (if one was created) and path to the TAR archive, hash of its content.
    """
    # Parse destination and create a tmpfile if none was specified
    file_d, destination = (
        tempfile.mkstemp(prefix="teklia-", suffix=".tar")
        if destination is None
        else (None, destination)
    )
    destination = Path(destination)
    logger.debug(f"Compressing file to {destination}")

    # Create an uncompressed tar archive with all the needed files
    # Files hierarchy ifs kept in the archive.
    files = []
    try:
        logger.debug(f"Compressing files to {destination}")
        with tarfile.open(destination, "w") as tar:
            for p in path.rglob("*"):
                x = p.relative_to(path)
                tar.add(p, arcname=x, recursive=False)
                # Only keep files when computing the hash
                if p.is_file():
                    files.append(p)
        logger.debug(f"Successfully created Tar archive from files @ {path}")
    except tarfile.TarError as e:
        raise Exception(f"Couldn't create Tar archive: {e}") from e

    # Sort by path
    files.sort()

    content_hasher = hashlib.md5()
    # Compute hash of the files
    for file_path in files:
        with file_path.open("rb") as file_data:
            for chunk in iter(lambda: file_data.read(CHUNK_SIZE), b""):
                content_hasher.update(chunk)
    return file_d, destination, content_hasher.hexdigest()


def create_tar_zst_archive(
    source: Path, destination: Path | None = None
) -> tuple[int | None, Path, str, str]:
    """Helper to create a TAR+ZST archive from a source folder.

    :param source: Path to the folder whose content should be archived.
    :param destination: Path to the created archive, defaults to None. If unspecified, a temporary file will be created.
    :return: The file descriptor of the created tempfile (if one was created), path to the archive, its hash and the hash of the tar archive's content.
    """
    # Create tar archive
    tar_fd, tar_archive, tar_hash = create_tar_archive(source)

    zst_fd, zst_archive, zst_hash = zstd_compress(tar_archive, destination)

    close_delete_file(tar_fd, tar_archive)

    return zst_fd, zst_archive, zst_hash, tar_hash


DEFAULT_BATCH_SIZE = 50
"""Batch size used for bulk publication to Arkindex"""


def batch_publication(func: Callable) -> Callable:
    """
    Decorator for functions that should raise an error when the value passed through the ``batch_size`` parameter is **not** a strictly positive integer.

    :param func: The function to wrap with the ``batch_size`` check
    :return: The function passing the ``batch_size`` check
    """
    signature = inspect.signature(func)

    def wrapper(self, *args, **kwargs):
        bound_func = signature.bind(self, *args, **kwargs)
        bound_func.apply_defaults()
        batch_size = bound_func.arguments.get("batch_size")
        assert (
            batch_size is not None and isinstance(batch_size, int) and batch_size > 0
        ), "batch_size shouldn't be null and should be a strictly positive integer"

        return func(self, *args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def make_batches(
    objects: list, singular_name: str, batch_size: int
) -> Generator[list[Any]]:
    """Split an object list in successive batches of maximum size ``batch_size``.

    :param objects: The object list to divide in batches of ``batch_size`` size
    :param singular_name: The singular form of the noun associated with the object list
    :param batch_size: The maximum size of each batch to split the object list
    :return: A generator of successive batches containing ``batch_size`` items from ``objects``
    """
    count = len(objects)
    logger.info(
        f"Creating batches of size {batch_size} to process {count} {pluralize(singular_name, count)}"
    )

    index = 1
    iterator = iter(objects)
    while batch := list(islice(iterator, batch_size)):
        count = len(batch)
        logger.info(
            f"Processing batch {index} containing {count} {pluralize(singular_name, count)}..."
        )

        yield batch

        index += 1
