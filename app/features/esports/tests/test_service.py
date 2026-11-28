"""Service-level tests for the esports feature."""

import pytest

from app.features.auth.repositories import UserRepository
from app.features.dataset.models import PublicationType
from app.features.dataset.repositories import DSMetaDataRepository
from app.features.esports.services import EsportsService

pytestmark = pytest.mark.service


def test_esports_service_creates_and_counts_esports_datasets(test_app, clean_database):
    with test_app.app_context():
        user = UserRepository().create(email="service@example.com", password="secret")
        meta = DSMetaDataRepository().create(
            title="Valorant CSV Service Dataset",
            description="Dataset creado desde EsportsService",
            publication_type=PublicationType.OTHER,
        )
        service = EsportsService()
        dataset = service.create(
            user_id=user.id,
            ds_meta_data_id=meta.id,
            team1="Akrew",
            team2="Booster Seat Gaming",
            winner="Akrew",
            team1_total_rounds=13,
            team2_total_rounds=7,
            match_date="08/01/2022 12:30",
        )

        assert dataset.id is not None
        assert service.count() == 1
        assert service.get_or_404(dataset.id).winner == "Akrew"
