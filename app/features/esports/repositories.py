from splent_framework.repositories.BaseRepository import BaseRepository

from app.features.esports.models import EsportsDataset


class EsportsRepository(BaseRepository):
    def __init__(self):
        super().__init__(EsportsDataset)
