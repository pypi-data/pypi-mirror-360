from ..repos import APIRepo


def get_service_by_name_type_project(user, project_id, service_type, service_name):
    repo = APIRepo()
    data, error = repo.retrieve_service_by_name_type_project(
        user, project_id, service_type, service_name
    )
    if data:
        return data
    raise Exception("Something went wrong.\n" + error)
