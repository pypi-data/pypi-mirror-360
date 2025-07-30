from ..repos import APIRepo


def get_project_by_name(user, project):
    repo = APIRepo()
    data, error = repo.retrieve_project_by_name(user, project)
    if data:
        return data
    raise Exception("Something went wrong.\n" + error)
