from splent_framework.services.BaseService import BaseService

from app.features.esports.repositories import EsportsRepository


class EsportsService(BaseService):
    def __init__(self):
        super().__init__(EsportsRepository())
