from ..repos import APIRepo
from ..models.StorageConfig import S3StorageCredentials
from ..auth import auth


def create_or_retrieve_s3_bucket(project_name, storage_name):
    user = auth()
    repo = APIRepo()
    data, error = repo.create_or_retrieve_s3_bucket(user, project_name, storage_name)
    if data:
        return S3StorageCredentials(**data)
    raise Exception("Something went wrong.\n" + error)
