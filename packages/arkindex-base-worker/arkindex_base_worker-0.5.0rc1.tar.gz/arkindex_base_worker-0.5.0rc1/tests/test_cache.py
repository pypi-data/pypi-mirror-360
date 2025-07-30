from pathlib import Path
from uuid import UUID

import pytest
from peewee import OperationalError

from arkindex_worker.cache import (
    SQL_VERSION,
    CachedElement,
    CachedImage,
    Version,
    check_version,
    create_tables,
    create_version_table,
    db,
    init_cache_db,
)


def test_init_non_existent_path():
    with pytest.raises(OperationalError, match="unable to open database file"):
        init_cache_db("path/not/found.sqlite")


def test_init(tmp_path):
    db_path = Path(f"{tmp_path}/db.sqlite")
    init_cache_db(db_path)

    assert db_path.is_file()


def test_create_tables_existing_table(tmp_path):
    db_path = tmp_path / "db.sqlite"

    # Create the tables once…
    init_cache_db(db_path)
    create_tables()
    db.close()

    before = db_path.read_bytes()

    # Create them again
    init_cache_db(db_path)
    create_tables()

    after = db_path.read_bytes()

    assert before == after, "Existing table structure was modified"


def test_create_tables(tmp_path):
    db_path = f"{tmp_path}/db.sqlite"
    init_cache_db(db_path)
    create_tables()

    # WARNING: If you are updating this schema following a development you have made
    # in base-worker, make sure to upgrade the arkindex_worker.cache.SQL_VERSION in
    # the same merge request as your changes.
    expected_schema = """CREATE TABLE "classifications" ("id" TEXT NOT NULL PRIMARY KEY, "element_id" TEXT NOT NULL, "class_name" TEXT NOT NULL, "confidence" REAL NOT NULL, "state" VARCHAR(10) NOT NULL, "worker_run_id" TEXT, FOREIGN KEY ("element_id") REFERENCES "elements" ("id"))
CREATE TABLE "dataset_elements" ("id" TEXT NOT NULL PRIMARY KEY, "element_id" TEXT NOT NULL, "dataset_id" TEXT NOT NULL, "set_name" VARCHAR(255) NOT NULL, FOREIGN KEY ("element_id") REFERENCES "elements" ("id"), FOREIGN KEY ("dataset_id") REFERENCES "datasets" ("id"))
CREATE TABLE "datasets" ("id" TEXT NOT NULL PRIMARY KEY, "name" VARCHAR(255) NOT NULL, "state" VARCHAR(255) NOT NULL DEFAULT 'open', "sets" TEXT NOT NULL)
CREATE TABLE "elements" ("id" TEXT NOT NULL PRIMARY KEY, "parent_id" TEXT, "type" VARCHAR(50) NOT NULL, "image_id" TEXT, "polygon" text, "rotation_angle" INTEGER NOT NULL, "mirrored" INTEGER NOT NULL, "initial" INTEGER NOT NULL, "worker_version_id" TEXT, "worker_run_id" TEXT, "confidence" REAL, FOREIGN KEY ("image_id") REFERENCES "images" ("id"))
CREATE TABLE "images" ("id" TEXT NOT NULL PRIMARY KEY, "width" INTEGER NOT NULL, "height" INTEGER NOT NULL, "url" TEXT NOT NULL)
CREATE TABLE "transcription_entities" ("transcription_id" TEXT NOT NULL, "type" VARCHAR(50) NOT NULL, "offset" INTEGER NOT NULL CHECK (offset >= 0), "length" INTEGER NOT NULL CHECK (length > 0), "worker_run_id" TEXT, "confidence" REAL, PRIMARY KEY ("transcription_id", "type"), FOREIGN KEY ("transcription_id") REFERENCES "transcriptions" ("id"))
CREATE TABLE "transcriptions" ("id" TEXT NOT NULL PRIMARY KEY, "element_id" TEXT NOT NULL, "text" TEXT NOT NULL, "confidence" REAL, "orientation" VARCHAR(50) NOT NULL, "worker_version_id" TEXT, "worker_run_id" TEXT, FOREIGN KEY ("element_id") REFERENCES "elements" ("id"))"""

    actual_schema = "\n".join(
        [
            row[0]
            for row in db.connection()
            .execute("SELECT sql FROM sqlite_master WHERE type = 'table' ORDER BY name")
            .fetchall()
        ]
    )

    assert expected_schema == actual_schema


def test_create_version_table(tmp_path):
    db_path = f"{tmp_path}/db.sqlite"
    init_cache_db(db_path)
    create_version_table()

    expected_schema = 'CREATE TABLE "version" ("version" INTEGER NOT NULL PRIMARY KEY)'
    actual_schema = "\n".join(
        [
            row[0]
            for row in db.connection()
            .execute("SELECT sql FROM sqlite_master WHERE type = 'table' ORDER BY name")
            .fetchall()
        ]
    )

    assert expected_schema == actual_schema
    assert Version.select().count() == 1
    assert Version.get() == Version(version=SQL_VERSION)


def test_check_version_unset_version(tmp_path):
    """
    The cache misses the version table
    """
    db_path = f"{tmp_path}/db.sqlite"
    init_cache_db(db_path)

    with pytest.raises(
        AssertionError,
        match=f"The SQLite database {db_path} does not have the correct cache version, it should be {SQL_VERSION}",
    ):
        check_version(db_path)


def test_check_version_differing_version(tmp_path):
    """
    The cache has a differing version
    """
    db_path = f"{tmp_path}/db.sqlite"
    init_cache_db(db_path)

    fake_version = 420
    assert fake_version != SQL_VERSION
    db.create_tables([Version])
    Version.create(version=fake_version)
    db.close()

    with pytest.raises(
        AssertionError,
        match=f"The SQLite database {db_path} does not have the correct cache version, it should be {SQL_VERSION}",
    ):
        check_version(db_path)


def test_check_version_same_version(tmp_path):
    """
    The cache has the expected version
    """
    db_path = f"{tmp_path}/db.sqlite"
    init_cache_db(db_path)
    create_version_table()
    db.close()

    check_version(db_path)


@pytest.mark.parametrize(
    (
        "image_width",
        "image_height",
        "polygon_x",
        "polygon_y",
        "polygon_width",
        "polygon_height",
        "max_width",
        "max_height",
        "expected_url",
    ),
    [
        # No max_size: no resize
        (
            400,
            600,
            0,
            0,
            400,
            600,
            None,
            None,
            "http://something/full/full/0/default.jpg",
        ),
        # No max_size: resize on bbox
        (
            400,
            600,
            0,
            0,
            200,
            100,
            None,
            None,
            "http://something/0,0,200,100/full/0/default.jpg",
        ),
        (
            400,
            600,
            50,
            50,
            200,
            100,
            None,
            None,
            "http://something/50,50,200,100/full/0/default.jpg",
        ),
        # max_size equal to the image size, no resize
        (
            400,
            600,
            0,
            0,
            400,
            600,
            400,
            None,
            "http://something/full/full/0/default.jpg",
        ),
        (
            600,
            400,
            0,
            0,
            600,
            400,
            None,
            400,
            "http://something/full/full/0/default.jpg",
        ),
        (
            400,
            400,
            0,
            0,
            400,
            400,
            400,
            400,
            "http://something/full/full/0/default.jpg",
        ),
        (
            400,
            400,
            50,
            50,
            200,
            100,
            200,
            100,
            "http://something/50,50,200,100/full/0/default.jpg",
        ),
        # max_size is smaller than the image, resize
        (
            400,
            600,
            0,
            0,
            400,
            600,
            None,
            400,
            "http://something/full/,400/0/default.jpg",
        ),
        (
            600,
            400,
            0,
            0,
            600,
            400,
            400,
            None,
            "http://something/full/400,/0/default.jpg",
        ),
        (
            400,
            600,
            0,
            0,
            200,
            600,
            400,
            600,
            "http://something/0,0,200,600/full/0/default.jpg",
        ),
        (
            400,
            600,
            50,
            50,
            200,
            600,
            400,
            600,
            "http://something/50,50,200,600/full/0/default.jpg",
        ),
        (
            400,
            400,
            0,
            0,
            400,
            400,
            200,
            200,
            "http://something/full/200,200/0/default.jpg",
        ),
        # max_size above the image size, no resize
        (
            400,
            600,
            0,
            0,
            400,
            600,
            800,
            None,
            "http://something/full/full/0/default.jpg",
        ),
        (
            600,
            400,
            0,
            0,
            600,
            400,
            None,
            800,
            "http://something/full/full/0/default.jpg",
        ),
        (
            400,
            400,
            0,
            0,
            400,
            400,
            800,
            800,
            "http://something/full/full/0/default.jpg",
        ),
        (
            400,
            400,
            50,
            50,
            200,
            100,
            800,
            800,
            "http://something/50,50,200,100/full/0/default.jpg",
        ),
    ],
)
def test_element_open_image(
    mocker,
    image_width,
    image_height,
    polygon_x,
    polygon_y,
    polygon_width,
    polygon_height,
    max_width,
    max_height,
    expected_url,
):
    open_mock = mocker.patch(
        "arkindex_worker.image.open_image", return_value="an image!"
    )

    image = CachedImage(
        id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        width=image_width,
        height=image_height,
        url="http://something",
    )
    elt = CachedElement(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        type="element",
        image=image,
        polygon=[
            [polygon_x, polygon_y],
            [polygon_x + polygon_width, polygon_y],
            [polygon_x + polygon_width, polygon_y + polygon_height],
            [polygon_x, polygon_y + polygon_height],
            [polygon_x, polygon_y],
        ],
    )

    assert elt.open_image(max_width=max_width, max_height=max_height) == "an image!"
    assert open_mock.call_count == 1
    assert open_mock.call_args == mocker.call(
        expected_url, mirrored=False, rotation_angle=0
    )


def test_element_open_image_requires_image():
    with pytest.raises(
        ValueError, match="Element aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa has no image"
    ):
        CachedElement(id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")).open_image()
