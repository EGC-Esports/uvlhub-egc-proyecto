from splent_framework.resources.generic_resource import create_resource
from splent_framework.serialisers.serializer import Serializer

from app.features.dataset.models import DataSet

file_fields = {"file_id": "id", "file_name": "name", "size": "get_formatted_size"}
file_serializer = Serializer(file_fields)

dataset_fields = {
    "dataset_id": "id",
    "created": "created_at",
    "name": "name",
    "doi": "get_uvlhub_doi",
    "files": "files",
}

dataset_serializer = Serializer(dataset_fields, related_serializers={"files": file_serializer})

DataSetResourceBase = create_resource(DataSet, dataset_serializer)


class DataSetResource(DataSetResourceBase):
    """El recurso toma el nombre de la clase del modelo para sus mensajes.

    Desde el WI-1.1 (#8) la clase se llama UVLDataset; se fija "DataSet" para
    que la API siga respondiendo igual ("DataSet not found").
    """

    def __init__(self):
        super().__init__()
        self.model_name = "DataSet"


def init_blueprint_api(api):
    """Function to register resources with the provided Flask-RESTful Api instance."""
    api.add_resource(DataSetResource, "/api/v1/datasets/", endpoint="datasets")
    api.add_resource(DataSetResource, "/api/v1/datasets/<int:id>", endpoint="dataset")
