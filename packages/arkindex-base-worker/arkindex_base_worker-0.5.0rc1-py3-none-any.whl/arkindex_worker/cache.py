"""
Database mappings and helper methods for the experimental worker caching feature.

On methods that support caching, the database will be used for all reads,
and writes will go both to the Arkindex API and the database,
reducing network usage.
"""

import json
import sqlite3
from pathlib import Path

from peewee import (
    SQL,
    BooleanField,
    CharField,
    Check,
    CompositeKey,
    Field,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    OperationalError,
    SqliteDatabase,
    TextField,
    UUIDField,
)
from PIL import Image

from arkindex_worker import logger

db = SqliteDatabase(None)


class JSONField(Field):
    """
    A Peewee field that stores a JSON payload as a string and parses it automatically.
    """

    field_type = "text"

    def db_value(self, value):
        if value is None:
            return
        return json.dumps(value)

    def python_value(self, value):
        if value is None:
            return
        return json.loads(value)


class Version(Model):
    """
    Cache version table, used to warn about incompatible cache databases
    when a worker uses an outdated version of ``base-worker``.
    """

    version = IntegerField(primary_key=True)

    class Meta:
        database = db
        table_name = "version"


class CachedImage(Model):
    """
    Cache image table
    """

    id = UUIDField(primary_key=True)
    width = IntegerField()
    height = IntegerField()
    url = TextField()

    class Meta:
        database = db
        table_name = "images"


class CachedElement(Model):
    """
    Cache element table
    """

    id = UUIDField(primary_key=True)
    parent_id = UUIDField(null=True)
    type = CharField(max_length=50)
    image = ForeignKeyField(CachedImage, backref="elements", null=True)
    polygon = JSONField(null=True)
    rotation_angle = IntegerField(default=0)
    mirrored = BooleanField(default=False)
    initial = BooleanField(default=False)
    # Needed to filter elements with cache
    worker_version_id = UUIDField(null=True)
    worker_run_id = UUIDField(null=True)
    confidence = FloatField(null=True)

    class Meta:
        database = db
        table_name = "elements"

    def open_image(
        self,
        *args,
        max_width: int | None = None,
        max_height: int | None = None,
        **kwargs,
    ) -> Image:
        """
        Open this element's image as a Pillow image.
        This does not crop the image to the element's polygon.
        IIIF servers with maxWidth, maxHeight or maxArea restrictions on image size are not supported.

        Warns:
        ----
           If both, ``max_width`` and ``max_height`` are set, the image ratio is not preserved.


        :param *args: Positional arguments passed to [arkindex_worker.image.open_image][]
        :param max_width: The maximum width of the image.
        :param max_height: The maximum height of the image.
        :param **kwargs: Keyword arguments passed to [arkindex_worker.image.open_image][]
        :raises ValueError: When this element does not have an image ID or a polygon.
        :return: A Pillow image.
        """
        from arkindex_worker.image import open_image, polygon_bounding_box

        if not self.image_id or not self.polygon:
            raise ValueError(f"Element {self.id} has no image")

        # Always fetch the image from the bounding box when size differs from full image
        bounding_box = polygon_bounding_box(self.polygon)
        if (
            bounding_box.width != self.image.width
            or bounding_box.height != self.image.height
        ):
            box = f"{bounding_box.x},{bounding_box.y},{bounding_box.width},{bounding_box.height}"
        else:
            box = "full"

        if max_width is None and max_height is None:
            resize = "full"
        else:
            if (
                # Do not resize for polygons that do not exactly match the images
                # as the resize is made directly by the IIIF server using the box parameter
                bounding_box.width != self.image.width
                or bounding_box.height != self.image.height
            ) or (
                # Do not resize when the image is below the maximum size
                (max_width is None or self.image.width <= max_width)
                and (max_height is None or self.image.height <= max_height)
            ):
                resize = "full"
            else:
                resize = f"{max_width or ''},{max_height or ''}"

        url = self.image.url
        if not url.endswith("/"):
            url += "/"

        return open_image(
            f"{url}{box}/{resize}/0/default.jpg",
            *args,
            rotation_angle=self.rotation_angle,
            mirrored=self.mirrored,
            **kwargs,
        )


class CachedTranscription(Model):
    """
    Cache transcription table
    """

    id = UUIDField(primary_key=True)
    element = ForeignKeyField(CachedElement, backref="transcriptions")
    text = TextField()
    confidence = FloatField(null=True)
    orientation = CharField(max_length=50)
    # Needed to filter transcriptions with cache
    worker_version_id = UUIDField(null=True)
    worker_run_id = UUIDField(null=True)

    class Meta:
        database = db
        table_name = "transcriptions"


class CachedClassification(Model):
    """
    Cache classification table
    """

    id = UUIDField(primary_key=True)
    element = ForeignKeyField(CachedElement, backref="classifications")
    class_name = TextField()
    confidence = FloatField()
    state = CharField(max_length=10)
    worker_run_id = UUIDField(null=True)

    class Meta:
        database = db
        table_name = "classifications"


class CachedTranscriptionEntity(Model):
    """
    Cache transcription entity table
    """

    transcription = ForeignKeyField(
        CachedTranscription, backref="transcription_entities"
    )
    type = CharField(max_length=50)
    offset = IntegerField(constraints=[Check("offset >= 0")])
    length = IntegerField(constraints=[Check("length > 0")])
    worker_run_id = UUIDField(null=True)
    confidence = FloatField(null=True)

    class Meta:
        primary_key = CompositeKey("transcription", "type")
        database = db
        table_name = "transcription_entities"


class CachedDataset(Model):
    id = UUIDField(primary_key=True)
    name = CharField()
    state = CharField(constraints=[SQL("DEFAULT 'open'")])
    sets = TextField()

    class Meta:
        database = db
        table_name = "datasets"


class CachedDatasetElement(Model):
    id = UUIDField(primary_key=True)
    element = ForeignKeyField(column_name="element_id", field="id", model=CachedElement)
    dataset = ForeignKeyField(column_name="dataset_id", field="id", model=CachedDataset)
    set_name = CharField()

    class Meta:
        database = db
        table_name = "dataset_elements"


# Add all the managed models in that list
# It's used here, but also in unit tests
MODELS = [
    CachedImage,
    CachedElement,
    CachedTranscription,
    CachedClassification,
    CachedTranscriptionEntity,
    CachedDataset,
    CachedDatasetElement,
]
SQL_VERSION = 4


def init_cache_db(path: Path):
    """
    Create the cache database on the given path
    :param path: Where the new database should be created
    """
    db.init(
        path,
        pragmas={
            # SQLite ignores foreign keys and check constraints by default!
            "foreign_keys": 1,
            "ignore_check_constraints": 0,
        },
    )
    db.connect()
    logger.info(f"Connected to cache on {path}")


def create_tables():
    """
    Creates the tables in the cache DB only if they do not already exist.
    """
    db.create_tables(MODELS)


def create_version_table():
    """
    Creates the Version table in the cache DB.
    This step must be independent from other tables creation since we only
    want to create the table and add the one and only Version entry when the
    cache is created from scratch.
    """
    db.create_tables([Version])
    Version.create(version=SQL_VERSION)


def check_version(cache_path: str | Path):
    """
    Check the validity of the SQLite version

    :param cache_path: Path towards a local SQLite database
    """
    with SqliteDatabase(cache_path) as provided_db, provided_db.bind_ctx([Version]):
        try:
            version = Version.get().version
        except OperationalError:
            version = None

        assert version == SQL_VERSION, (
            f"The SQLite database {cache_path} does not have the correct cache version, it should be {SQL_VERSION}"
        )


def merge_parents_cache(paths: list, current_database: Path):
    """
    Merge all the potential parent task's databases into the existing local one
    :param paths: Path to cache databases
    :param current_database: Path to the current database
    """
    assert current_database.exists()

    if not paths:
        logger.info("No parents cache to use")
        return

    # Open a connection on current database
    connection = sqlite3.connect(current_database)
    cursor = connection.cursor()

    # Merge each table into the local database
    for idx, path in enumerate(paths):
        # Check that the parent cache uses a compatible version
        check_version(path)

        with SqliteDatabase(path) as source, source.bind_ctx(MODELS):
            source.create_tables(MODELS)

        logger.info(f"Merging parent db {path} into {current_database}")
        statements = [
            "PRAGMA page_size=80000;",
            "PRAGMA synchronous=OFF;",
            f"ATTACH DATABASE '{path}' AS source_{idx};",
            f"REPLACE INTO images SELECT * FROM source_{idx}.images;",
            f"REPLACE INTO elements SELECT * FROM source_{idx}.elements;",
            f"REPLACE INTO transcriptions SELECT * FROM source_{idx}.transcriptions;",
            f"REPLACE INTO classifications SELECT * FROM source_{idx}.classifications;",
            f"REPLACE INTO transcription_entities SELECT * FROM source_{idx}.transcription_entities;",
            f"REPLACE INTO datasets SELECT * FROM source_{idx}.datasets;",
            f"REPLACE INTO dataset_elements SELECT * FROM source_{idx}.dataset_elements;",
        ]

        for statement in statements:
            cursor.execute(statement)
        connection.commit()


def unsupported_cache(func):
    def wrapper(self, *args, **kwargs):
        results = func(self, *args, **kwargs)

        if self.use_cache:
            logger.warning(
                f"This API helper `{func.__name__}` did not update the cache database"
            )

        return results

    return wrapper
