"""Service-level tests for dataset — orchestration on top of a real database."""

import os
import shutil
from datetime import datetime, timedelta, timezone
from io import BytesIO
from zipfile import ZipFile

import pytest
from werkzeug.datastructures import FileStorage

from app.features.auth.repositories import UserRepository
from app.features.dataset.models import PublicationType
from app.features.dataset.repositories import (
    AuthorRepository,
    DataSetRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
)
from app.features.dataset.services import (
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
)

pytestmark = pytest.mark.service


def _make_user(email):
    return UserRepository().create(email=email, password="secret")


def _make_dataset(user, title="Sample dataset", doi=None, tags="tag1,tag2", authors=None, created_at=None):
    meta = DSMetaDataRepository().create(
        title=title,
        description=f"Description for {title}",
        publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
        dataset_doi=doi,
        tags=tags,
    )
    for author_name in authors or []:
        AuthorRepository().create(name=author_name, ds_meta_data_id=meta.id)
    return DataSetRepository().create(
        user_id=user.id,
        ds_meta_data_id=meta.id,
        created_at=created_at or datetime.now(timezone.utc),
    )


def _uvl_upload(filename, content=b"features\n\tRoot\n"):
    return FileStorage(stream=BytesIO(content), filename=filename, content_type="text/plain")


def test_synchronized_lookups_are_delegated_and_scoped_to_the_user(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        other = _make_user("other@example.com")
        synced = _make_dataset(owner, title="Synced", doi="10.1234/synced")
        local = _make_dataset(owner, title="Local")
        theirs = _make_dataset(other, title="Theirs", doi="10.1234/theirs")

        service = DataSetService()
        assert [d.id for d in service.get_synchronized(owner.id)] == [synced.id]
        assert [d.id for d in service.get_unsynchronized(owner.id)] == [local.id]
        assert service.get_unsynchronized_dataset(owner.id, local.id).id == local.id
        assert service.count_synchronized_datasets() == 2
        assert {d.id for d in service.latest_synchronized()} == {synced.id, theirs.id}


def test_counts_reflect_the_rows_actually_persisted(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Counted")
        AuthorRepository().create(name="Ada Lovelace", ds_meta_data_id=dataset.ds_meta_data_id)
        AuthorRepository().create(name="Alan Turing", ds_meta_data_id=dataset.ds_meta_data_id)

        service = DataSetService()
        assert service.count_authors() == 2
        assert service.count_dsmetadata() == 1
        assert service.count() == 1


def test_get_uvlhub_doi_builds_a_url_from_the_configured_domain(test_app, clean_database, monkeypatch):
    monkeypatch.setenv("DOMAIN", "uvlhub.test")
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Published", doi="10.1234/published")

        assert DataSetService().get_uvlhub_doi(dataset) == "http://uvlhub.test/doi/10.1234/published"


def test_dsmetadata_service_updates_and_finds_by_doi(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Draft")

        service = DSMetaDataService()
        assert service.filter_by_doi("10.1234/minted") is None

        service.update(dataset.ds_meta_data_id, dataset_doi="10.1234/minted", deposition_id=99)

        found = service.filter_by_doi("10.1234/minted")
        assert found is not None
        assert found.id == dataset.ds_meta_data_id
        assert found.deposition_id == 99


def test_doi_mapping_service_unwraps_the_new_doi(test_app, clean_database):
    with test_app.app_context():
        service = DOIMappingService()
        service.create(dataset_doi_old="10.1234/old", dataset_doi_new="10.5678/new")

        assert service.get_new_doi("10.1234/old") == "10.5678/new"
        assert service.get_new_doi("10.1234/unknown") is None


def test_record_download_is_recorded_once_per_cookie(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Downloadable")

        service = DSDownloadRecordService()
        service.record_download(owner, dataset.id, "cookie-a")
        service.record_download(owner, dataset.id, "cookie-a")
        assert service.count() == 1

        service.record_download(owner, dataset.id, "cookie-b")
        assert service.count() == 2


def test_create_cookie_registers_a_single_view_per_cookie(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Viewable")

        service = DSViewRecordService()
        with test_app.test_request_context("/", headers={"Cookie": "view_cookie=abc-123"}):
            assert service.create_cookie(dataset) == "abc-123"
            assert service.count() == 1

            # Same visitor, same cookie: no duplicate row.
            assert service.create_cookie(dataset) == "abc-123"
            assert service.count() == 1

        with test_app.test_request_context("/", headers={"Cookie": "view_cookie=def-456"}):
            service.create_cookie(dataset)
            assert service.count() == 2


def test_save_temp_uvl_rejects_files_that_are_not_uvl(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        result = DataSetService().save_temp_uvl(_uvl_upload("notes.txt"), owner)

        assert result["status"] == "error"
        assert result["code"] == 400
        assert result["message"] == "No valid file"
        assert not os.path.isdir(owner.temp_folder())


def test_save_temp_uvl_disambiguates_repeated_filenames(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        service = DataSetService()

        first = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)
        second = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)
        third = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)

        assert first["filename"] == "model.uvl"
        assert second["filename"] == "model (1).uvl"
        assert third["filename"] == "model (2).uvl"
        assert sorted(os.listdir(owner.temp_folder())) == ["model (1).uvl", "model (2).uvl", "model.uvl"]


def test_delete_temp_file_removes_an_uploaded_file(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        service = DataSetService()

        saved = service.save_temp_uvl(_uvl_upload("model.uvl"), owner)
        assert os.path.exists(os.path.join(owner.temp_folder(), saved["filename"]))

        deleted = service.delete_temp_file(saved["filename"], owner)
        assert deleted["code"] == 200
        assert not os.path.exists(os.path.join(owner.temp_folder(), saved["filename"]))

        # Deleting the same file twice, or passing no filename at all, is an error.
        assert service.delete_temp_file(saved["filename"], owner)["code"] == 404
        assert service.delete_temp_file("", owner)["code"] == 400


def test_build_download_archive_zips_the_dataset_upload_folder(test_app, clean_database, monkeypatch, tmp_path):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Zippable")
        source_dir = tmp_path / "uploads" / f"user_{owner.id}" / f"dataset_{dataset.id}"
        source_dir.mkdir(parents=True)
        (source_dir / "file1.uvl").write_text("features\n\tRoot\n")

        tmp_dir, zip_name = DataSetService().build_download_archive(dataset)

        assert zip_name == f"dataset_{dataset.id}.zip"
        with ZipFile(os.path.join(tmp_dir, zip_name)) as archive:
            assert archive.namelist() == [f"dataset_{dataset.id}/file1.uvl"]
            assert archive.read(f"dataset_{dataset.id}/file1.uvl") == b"features\n\tRoot\n"
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_build_download_archive_yields_an_empty_zip_when_nothing_was_uploaded(
    test_app, clean_database, monkeypatch, tmp_path
):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        owner = _make_user("owner@example.com")
        dataset = _make_dataset(owner, title="Empty")

        tmp_dir, zip_name = DataSetService().build_download_archive(dataset)
        with ZipFile(os.path.join(tmp_dir, zip_name)) as archive:
            assert archive.namelist() == []
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _seed_downloads(dataset, count):
    repo = DSDownloadRecordRepository()
    for i in range(count):
        repo.create(
            user_id=None,
            dataset_id=dataset.id,
            download_date=datetime.now(timezone.utc),
            download_cookie=f"cookie-{dataset.id}-{i}",
        )


def test_get_recommendations_orders_known_seeded_datasets_by_score(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("recommender@example.com")
        now = datetime(2026, 11, 28, 12, 0, tzinfo=timezone.utc)

        target = _make_dataset(
            owner,
            title="Feature Models for Software Product Lines",
            doi="10.1234/target",
            tags="spl, uvl, variability",
            authors=["Lovelace, Ada", "Turing, Alan"],
            created_at=now,
        )

        # 1st expected: 2 shared tags (6.0) + 1 shared author (2.0) + 5 downloads (~1.79) + fresh (1.0) = ~10.79
        top_match = _make_dataset(
            owner,
            title="Variability Models for Mobile Apps",
            doi="10.1234/top",
            tags="spl, variability, mobile",
            authors=["Lovelace, Ada"],
            created_at=now,
        )
        _seed_downloads(top_match, 5)

        # 2nd expected: 1 shared tag (3.0) + 1 shared author (2.0) + 10 downloads (~2.40) + 30d old (0.5) = ~7.90
        second_match = _make_dataset(
            owner,
            title="SPL Datasets from Industry",
            doi="10.1234/second",
            tags="spl, industry",
            authors=["Turing, Alan"],
            created_at=now - timedelta(days=30),
        )
        _seed_downloads(second_match, 10)

        # 3rd expected: 1 shared tag (3.0) + 0 authors + 20 downloads (~3.04) + 30d old (0.5) = ~6.54
        third_popular = _make_dataset(
            owner,
            title="Popular UVL Benchmark",
            doi="10.1234/third",
            tags="uvl",
            authors=["Hopper, Grace"],
            created_at=now - timedelta(days=30),
        )
        _seed_downloads(third_popular, 20)

        # 4th expected: 1 shared tag (3.0) + 0 authors + 0 downloads + 10d old (0.75) = 3.75
        fourth_recent = _make_dataset(
            owner,
            title="Recent UVL Case Study",
            doi="10.1234/fourth",
            tags="uvl",
            authors=["Dijkstra, Edsger"],
            created_at=now - timedelta(days=10),
        )

        # 5th expected: 1 shared tag (3.0) + 0 authors + 0 downloads + 90d old (0.25) = 3.25
        fifth_older = _make_dataset(
            owner,
            title="Historical UVL Archive",
            doi="10.1234/fifth",
            tags="uvl",
            authors=["Dijkstra, Edsger"],
            created_at=now - timedelta(days=90),
        )

        # 6th expected (fallback without shared tags or authors): 0 + 0 + 2 downloads (~1.10) + fresh (1.0) = ~2.10
        sixth_unrelated = _make_dataset(
            owner,
            title="Unrelated Chess Openings",
            doi="10.1234/sixth",
            tags="chess, boardgames",
            authors=["Kasparov, Garry"],
            created_at=now,
        )
        _seed_downloads(sixth_unrelated, 2)

        # Unpublished draft despite identical tags and authors: must never appear
        _make_dataset(
            owner,
            title="Unpublished Twin Draft",
            doi=None,
            tags="spl, uvl, variability",
            authors=["Lovelace, Ada", "Turing, Alan"],
            created_at=now,
        )

        service = DataSetService()

        # Default limit (5) excludes the 6th lowest-scoring dataset, unpublished draft, and target itself
        top_five = service.get_recommendations(target, now=now)
        assert [d.id for d in top_five] == [
            top_match.id,
            second_match.id,
            third_popular.id,
            fourth_recent.id,
            fifth_older.id,
        ]
        assert target.id not in [d.id for d in top_five]

        # With limit=10, the unrelated published dataset appears in 6th place as fallback
        all_ranked = service.get_recommendations(target, limit=10, now=now)
        assert [d.id for d in all_ranked] == [
            top_match.id,
            second_match.id,
            third_popular.id,
            fourth_recent.id,
            fifth_older.id,
            sixth_unrelated.id,
        ]

        # Custom limit=2 returns only top 2
        assert [d.id for d in service.get_recommendations(target, limit=2, now=now)] == [
            top_match.id,
            second_match.id,
        ]


def test_get_recommendations_handles_empty_or_non_positive_limits(test_app, clean_database):
    with test_app.app_context():
        owner = _make_user("alone@example.com")
        only_dataset = _make_dataset(owner, title="Only One", doi="10.1234/only")

        service = DataSetService()
        assert service.get_recommendations(only_dataset) == []
        assert service.get_recommendations(only_dataset, limit=0) == []
        assert service.get_recommendations(None) == []
