"""Unit tests for the esports feature — pure logic, no Flask app, no database."""

import csv
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.feature_loader import declared_features
from app.features.dataset.models import BaseDataset
from app.features.esports.models import CSV_COLUMNS, CSV_DELIMITER, Esports, EsportsDataset

pytestmark = pytest.mark.unit

EXAMPLE_CSV_PATH = Path(__file__).resolve().parents[1] / "csv_examples" / "valorant-data-example.csv"


def test_esports_feature_is_registered_in_splent_configuration():
    assert "esports" in declared_features("dev")
    assert "esports" in declared_features("prod")


def test_esports_dataset_inherits_from_base_dataset():
    assert issubclass(EsportsDataset, BaseDataset)
    assert Esports is EsportsDataset
    assert EsportsDataset.__table__.name == "esports_dataset"


def test_esports_dataset_defines_all_25_documented_csv_columns():
    expected_columns = (
        "row_id",
        "match_date",
        "event_name",
        "event_stage",
        "team1",
        "team2",
        "team1_map_score",
        "team2_map_score",
        "map",
        "winner",
        "team1_total_rounds",
        "team2_total_rounds",
        "player_name",
        "player_team",
        "agent",
        "acs",
        "kills",
        "deaths",
        "assists",
        "adr",
        "hs_percent",
        "first_kills",
        "first_deaths",
        "plants",
        "defuses",
    )
    assert CSV_COLUMNS == expected_columns
    assert len(CSV_COLUMNS) == 25

    table_columns = {column.name for column in EsportsDataset.__table__.columns}
    base_columns = {"id", "user_id", "ds_meta_data_id", "created_at", "game"}
    assert base_columns.issubset(table_columns)
    assert set(CSV_COLUMNS).issubset(table_columns)


def test_esports_dataset_stores_match_fields_and_defaults_game_to_valorant():
    dataset = EsportsDataset(
        id=9,
        row_id=1,
        match_date="08/01/2022 15:30",
        event_name="Nerd Street Gamers Winter Championship - Regional LAN Philadelphia",
        event_stage="Group Stage: Decider (A)",
        team1="Booster Seat Gaming",
        team2="Pho Real",
        team1_map_score=2,
        team2_map_score=1,
        map="Breeze",
        winner="Booster Seat Gaming",
        team1_total_rounds=13,
        team2_total_rounds=7,
        player_name="Boltzy",
        player_team="Boos",
        agent="viper",
        acs=218,
        kills=17,
        deaths=12,
        assists=2,
        adr=141,
        hs_percent=0.19,
        first_kills=3,
        first_deaths=0,
        plants=0,
        defuses=0,
    )

    assert dataset.game == "Valorant"
    assert dataset.team1 == "Booster Seat Gaming"
    assert dataset.team2 == "Pho Real"
    assert dataset.team1_total_rounds == 13
    assert dataset.team2_total_rounds == 7
    assert dataset.winner == "Booster Seat Gaming"
    assert dataset.match_date == "08/01/2022 15:30"
    assert dataset.map == "Breeze"
    assert dataset.player_name == "Boltzy"
    assert dataset.agent == "viper"
    assert dataset.hs_percent == pytest.approx(0.19)
    assert repr(dataset) == "EsportsDataset<9>"

    as_dict = dataset.csv_fields_to_dict()
    assert len(as_dict) == 25
    assert as_dict["row_id"] == 1
    assert as_dict["winner"] == "Booster Seat Gaming"
    assert as_dict["kills"] == 17


def test_esports_dataset_implements_base_dataset_files_contract():
    empty_dataset = EsportsDataset()
    assert empty_dataset.files() == []
    assert empty_dataset.get_files_count() == 0
    assert empty_dataset.get_file_total_size() == 0

    csv_files = [SimpleNamespace(name="partidas.csv", size=1024), SimpleNamespace(name="extra.csv", size=512)]
    dataset = EsportsDataset(csv_files=csv_files)
    assert dataset.files() == csv_files
    assert dataset.get_files_count() == 2
    assert dataset.get_file_total_size() == 1536


def test_from_csv_row_converts_types_and_preserves_empty_cells_as_none():
    raw_row = {
        "row_id": "31",
        "match_date": "08/01/2022 15:30",
        "event_name": "Nerd Street Gamers Winter Championship - Regional LAN Philadelphia",
        "event_stage": "Group Stage: Decider (C)",
        "team1": "Bjor's Kittens",
        "team2": "Mugiwara",
        "team1_map_score": "2",
        "team2_map_score": "0",
        "map": "Icebox",
        "winner": "Bjor's Kittens",
        "team1_total_rounds": "13",
        "team2_total_rounds": "6",
        "player_name": "Coach",
        "player_team": "",
        "agent": "sage",
        "acs": "",
        "kills": "10",
        "deaths": "10",
        "assists": "12",
        "adr": "117",
        "hs_percent": "",
        "first_kills": "1",
        "first_deaths": "1",
        "plants": "4",
        "defuses": "1",
    }

    dataset = EsportsDataset.from_csv_row(raw_row)

    assert dataset.row_id == 31
    assert dataset.team1 == "Bjor's Kittens"
    assert dataset.team2 == "Mugiwara"
    assert dataset.team1_total_rounds == 13
    assert dataset.team2_total_rounds == 6
    assert dataset.player_name == "Coach"
    assert dataset.player_team is None
    assert dataset.acs is None
    assert dataset.hs_percent is None
    assert dataset.kills == 10


def test_valorant_example_csv_matches_model_schema_and_parses_all_rows():
    assert EXAMPLE_CSV_PATH.exists(), "valorant-data-example.csv debe existir en app/features/esports/csv_examples/"

    with EXAMPLE_CSV_PATH.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=CSV_DELIMITER)
        assert tuple(reader.fieldnames) == CSV_COLUMNS
        datasets = [EsportsDataset.from_csv_row(row) for row in reader]

    assert len(datasets) == 100

    first = datasets[0]
    assert first.row_id == 1
    assert first.match_date == "08/01/2022 15:30"
    assert first.team1 == "Booster Seat Gaming"
    assert first.team2 == "Pho Real"
    assert first.team1_map_score == 2
    assert first.team2_map_score == 1
    assert first.map == "Breeze"
    assert first.winner == "Booster Seat Gaming"
    assert first.team1_total_rounds == 13
    assert first.team2_total_rounds == 7
    assert first.player_name == "Boltzy"
    assert first.player_team == "Boos"
    assert first.agent == "viper"
    assert first.acs == 218
    assert first.kills == 17
    assert first.deaths == 12
    assert first.assists == 2
    assert first.adr == 141
    assert first.hs_percent == pytest.approx(0.19)
    assert first.first_kills == 3
    assert first.first_deaths == 0
    assert first.plants == 0
    assert first.defuses == 0

    coach_row = datasets[30]
    assert coach_row.row_id == 31
    assert coach_row.player_name == "Coach"
    assert coach_row.player_team is None
    assert coach_row.agent == "sage"
