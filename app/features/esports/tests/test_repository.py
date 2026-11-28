"""Repository-level tests for the esports feature."""

import pytest

from app.features.auth.repositories import UserRepository
from app.features.dataset.models import PublicationType
from app.features.dataset.repositories import DSMetaDataRepository
from app.features.esports.repositories import EsportsRepository

pytestmark = pytest.mark.repository


def test_esports_repository_creates_and_retrieves_esports_dataset(test_app, clean_database):
    with test_app.app_context():
        user = UserRepository().create(email="valorant@example.com", password="secret")
        meta = DSMetaDataRepository().create(
            title="Valorant Pro Matches",
            description="Partidas profesionales de Valorant en CSV",
            publication_type=PublicationType.OTHER,
            tags="valorant,esports",
        )
        repo = EsportsRepository()
        created = repo.create(
            user_id=user.id,
            ds_meta_data_id=meta.id,
            row_id=1,
            match_date="08/01/2022 15:30",
            team1="Booster Seat Gaming",
            team2="Pho Real",
            winner="Booster Seat Gaming",
            team1_total_rounds=13,
            team2_total_rounds=7,
            map="Breeze",
        )

        fetched = repo.get_or_404(created.id)
        assert fetched.id == created.id
        assert fetched.name() == "Valorant Pro Matches"
        assert fetched.team1 == "Booster Seat Gaming"
        assert fetched.winner == "Booster Seat Gaming"
        assert fetched.game == "Valorant"
