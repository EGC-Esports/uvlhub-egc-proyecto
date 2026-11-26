"""Unit tests for dataset — pure logic, no app context and no database.

The helpers under test are either module-level functions or methods that only
read attributes off ``self``, so they are exercised against lightweight stubs
instead of persisted rows.
"""

import hashlib
from types import SimpleNamespace

import pytest

from app.features.dataset.forms import DataSetForm
from app.features.dataset.models import BaseDataset, DataSet, PublicationType, UVLDataset
from app.features.dataset.services import SizeService, calculate_checksum_and_size

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "size, expected",
    [
        (0, "0 bytes"),
        (512, "512 bytes"),
        (1023, "1023 bytes"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1024**2, "1.0 MB"),
        (5 * 1024**2, "5.0 MB"),
        (1024**3, "1.0 GB"),
    ],
)
def test_get_human_readable_size_picks_the_right_unit(size, expected):
    assert SizeService().get_human_readable_size(size) == expected


def test_calculate_checksum_and_size_matches_file_contents(tmp_path):
    content = b"features\n\tRoot\n"
    uvl = tmp_path / "model.uvl"
    uvl.write_bytes(content)

    checksum, size = calculate_checksum_and_size(str(uvl))

    assert checksum == hashlib.md5(content).hexdigest()
    assert size == len(content)


def test_convert_publication_type_maps_enum_value_to_name():
    assert DataSetForm.convert_publication_type(None, "article") == "JOURNAL_ARTICLE"
    assert DataSetForm.convert_publication_type(None, "datamanagementplan") == "DATA_MANAGEMENT_PLAN"


def test_convert_publication_type_falls_back_to_none_for_unknown_values():
    assert DataSetForm.convert_publication_type(None, "not-a-publication-type") == "NONE"


def test_get_cleaned_publication_type_humanises_the_enum_name():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(publication_type=PublicationType.DATA_MANAGEMENT_PLAN))

    assert DataSet.get_cleaned_publication_type(dataset) == "Data Management Plan"


def test_get_zenodo_url_is_none_without_a_dataset_doi():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(deposition_id=42, dataset_doi=None))

    assert DataSet.get_zenodo_url(dataset) is None


def test_get_zenodo_url_is_none_without_a_deposition_id():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(deposition_id=None, dataset_doi="10.1234/dataset1"))

    assert DataSet.get_zenodo_url(dataset) is None


def test_get_zenodo_url_points_at_the_deposition_record():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(deposition_id=42, dataset_doi="10.1234/dataset1"))

    assert DataSet.get_zenodo_url(dataset) == "https://zenodo.org/record/42"


def test_files_and_sizes_are_aggregated_across_feature_models():
    dataset = SimpleNamespace(
        feature_models=[
            SimpleNamespace(files=[SimpleNamespace(size=100), SimpleNamespace(size=200)]),
            SimpleNamespace(files=[SimpleNamespace(size=724)]),
        ]
    )

    assert DataSet.get_files_count(dataset) == 3
    assert DataSet.get_file_total_size(dataset) == 1024
    assert len(DataSet.files(dataset)) == 3


def test_base_dataset_is_abstract_and_has_no_table():
    assert BaseDataset.__dict__.get("__abstract__") is True
    assert not hasattr(BaseDataset, "__table__")


def test_uvl_dataset_inherits_base_dataset_and_keeps_the_data_set_table():
    assert issubclass(UVLDataset, BaseDataset)
    assert UVLDataset.__table__.name == "data_set"


def test_dataset_alias_points_at_uvl_dataset():
    assert DataSet is UVLDataset


def test_uvl_dataset_table_keeps_the_original_columns():
    columns = {column.name for column in UVLDataset.__table__.columns}

    assert columns == {"id", "user_id", "ds_meta_data_id", "created_at"}


def test_base_dataset_files_must_be_implemented_by_each_dataset_type():
    with pytest.raises(NotImplementedError):
        BaseDataset.files(SimpleNamespace())


def test_base_dataset_counts_and_sizes_come_from_files():
    files = [SimpleNamespace(size=10), SimpleNamespace(size=32)]
    dataset = SimpleNamespace(files=lambda: files)

    assert BaseDataset.get_files_count(dataset) == 2
    assert BaseDataset.get_file_total_size(dataset) == 42


def test_publication_type_none_is_the_documented_default_value():
    assert PublicationType.NONE.value == "none"
    assert PublicationType("article") is PublicationType.JOURNAL_ARTICLE
