from uuid import UUID

import pytest

from arkindex_worker.cache import (
    MODELS,
    SQL_VERSION,
    CachedClassification,
    CachedElement,
    CachedImage,
    CachedTranscription,
    CachedTranscriptionEntity,
    Version,
    merge_parents_cache,
)


@pytest.mark.parametrize(
    ("parents", "expected_elements", "expected_transcriptions"),
    [
        # Nothing happen when no parents are available
        ([], [], []),
        # Nothing happen when the parent file does not exist
        (
            [
                "missing",
            ],
            [],
            [],
        ),
        # When one parent is available, its data is reused
        (
            [
                "first",
            ],
            [
                UUID("12341234-1234-1234-1234-123412341234"),
                UUID("56785678-5678-5678-5678-567856785678"),
            ],
            [],
        ),
        # When 2 parents are available, their data is merged
        (
            [
                "first",
                "second",
            ],
            [
                UUID("12341234-1234-1234-1234-123412341234"),
                UUID("56785678-5678-5678-5678-567856785678"),
                UUID("42424242-4242-4242-4242-424242424242"),
            ],
            [
                UUID("11111111-1111-1111-1111-111111111111"),
            ],
        ),
        # When N parents are available, their data is merged, and conflicts are supported
        (
            [
                "first",
                "second",
                "conflict",
            ],
            [
                UUID("12341234-1234-1234-1234-123412341234"),
                UUID("56785678-5678-5678-5678-567856785678"),
                UUID("42424242-4242-4242-4242-424242424242"),
            ],
            [
                UUID("11111111-1111-1111-1111-111111111111"),
                UUID("22222222-2222-2222-2222-222222222222"),
            ],
        ),
    ],
)
def test_merge_databases(
    mock_databases, tmp_path, parents, expected_elements, expected_transcriptions
):
    """Test multiple database merge scenarios"""

    # We always start with an empty database
    with mock_databases["target"]["db"].bind_ctx(MODELS):
        assert CachedImage.select().count() == 0
        assert CachedElement.select().count() == 0
        assert CachedTranscription.select().count() == 0
        assert CachedClassification.select().count() == 0
        assert CachedTranscriptionEntity.select().count() == 0

    # Retrieve parents databases paths
    paths = filter(
        lambda p: p.is_file(),
        [tmp_path / parent / "db.sqlite" for parent in parents],
    )

    # Merge all requested parents databases into our target
    merge_parents_cache(paths, mock_databases["target"]["path"])

    # The target now should have the expected elements and transcriptions
    with mock_databases["target"]["db"].bind_ctx(MODELS):
        assert CachedImage.select().count() == 0
        assert CachedElement.select().count() == len(expected_elements)
        assert CachedTranscription.select().count() == len(expected_transcriptions)
        assert CachedClassification.select().count() == 0
        assert CachedTranscriptionEntity.select().count() == 0
        assert [
            e.id for e in CachedElement.select().order_by("id")
        ] == expected_elements
        assert [
            t.id for t in CachedTranscription.select().order_by("id")
        ] == expected_transcriptions


def test_merge_chunk(mock_databases, tmp_path):
    """
    Check the db merge algorithm support two parents
    and one of them has a chunk
    """
    # At first we have nothing in target
    with mock_databases["target"]["db"].bind_ctx(MODELS):
        assert CachedImage.select().count() == 0
        assert CachedElement.select().count() == 0
        assert CachedTranscription.select().count() == 0
        assert CachedClassification.select().count() == 0
        assert CachedTranscriptionEntity.select().count() == 0

    # Check filenames
    assert mock_databases["chunk_42"]["path"].name == "db_42.sqlite"
    assert mock_databases["first"]["path"].name == "db.sqlite"

    paths = [
        tmp_path / "chunk_42" / "db_42.sqlite",
        tmp_path / "first" / "db.sqlite",
    ]

    merge_parents_cache(paths, mock_databases["target"]["path"])

    # The target should now have 3 elements and 0 transcription
    with mock_databases["target"]["db"].bind_ctx(MODELS):
        assert CachedImage.select().count() == 0
        assert CachedElement.select().count() == 3
        assert CachedTranscription.select().count() == 0
        assert CachedClassification.select().count() == 0
        assert CachedTranscriptionEntity.select().count() == 0
        assert [e.id for e in CachedElement.select().order_by("id")] == [
            UUID("42424242-4242-4242-4242-424242424242"),
            UUID("12341234-1234-1234-1234-123412341234"),
            UUID("56785678-5678-5678-5678-567856785678"),
        ]


def test_merge_from_worker(
    responses, mock_base_worker_with_cache, mock_databases, tmp_path
):
    """
    High level merge from the base worker
    """
    responses.add(
        responses.GET,
        "http://testserver/api/v1/task/my_task/",
        status=200,
        json={"parents": ["first", "second"]},
    )
    # At first we have nothing in target
    with mock_databases["target"]["db"].bind_ctx(MODELS):
        assert CachedImage.select().count() == 0
        assert CachedElement.select().count() == 0
        assert CachedTranscription.select().count() == 0
        assert CachedClassification.select().count() == 0
        assert CachedTranscriptionEntity.select().count() == 0

    # Configure worker with a specific data directory
    mock_base_worker_with_cache.task_data_dir = tmp_path

    # Create the task's output dir, so that it can create its own database
    (tmp_path / "my_task").mkdir()
    mock_base_worker_with_cache.args = mock_base_worker_with_cache.parser.parse_args()
    mock_base_worker_with_cache.configure()
    # Store parent tasks IDs as attribute
    assert mock_base_worker_with_cache.task_parents == ["first", "second"]

    assert mock_base_worker_with_cache.use_cache

    # Then we have 2 elements and a transcription
    assert CachedImage.select().count() == 0
    assert CachedElement.select().count() == 3
    assert CachedTranscription.select().count() == 1
    assert CachedClassification.select().count() == 0
    assert CachedTranscriptionEntity.select().count() == 0
    assert [e.id for e in CachedElement.select().order_by("id")] == [
        UUID("12341234-1234-1234-1234-123412341234"),
        UUID("56785678-5678-5678-5678-567856785678"),
        UUID("42424242-4242-4242-4242-424242424242"),
    ]
    assert [t.id for t in CachedTranscription.select().order_by("id")] == [
        UUID("11111111-1111-1111-1111-111111111111"),
    ]


def test_merge_conflicting_versions(mock_databases, tmp_path):
    """
    Merging databases with differing versions should not be allowed
    """

    with mock_databases["second"]["db"].bind_ctx([Version]):
        assert Version.get() == Version(version=SQL_VERSION)
        fake_version = 420
        Version.update(version=fake_version).execute()
        assert Version.get() == Version(version=fake_version)

    with mock_databases["target"]["db"].bind_ctx([Version]):
        assert Version.get() == Version(version=SQL_VERSION)

    # Retrieve parents databases paths
    paths = [
        tmp_path / "first" / "db.sqlite",
        tmp_path / "second" / "db.sqlite",
    ]

    # Merge all requested parents databases into our target, the "second" parent have a differing version
    with pytest.raises(
        AssertionError,
        match=f"The SQLite database {paths[1]} does not have the correct cache version, it should be {SQL_VERSION}",
    ):
        merge_parents_cache(paths, mock_databases["target"]["path"])
