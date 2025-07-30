from ..repos import APIRepo
from .get_project_by_name import get_project_by_name
from .get_service_by_name_type_project import get_service_by_name_type_project


def get_logs(user, project_name, service_type, service_name):
    project = get_project_by_name(user, project_name)
    service = get_service_by_name_type_project(
        user, project["id"], service_type, service_name
    )
    repo = APIRepo()
    return repo.get_logs(user, service["id"])
