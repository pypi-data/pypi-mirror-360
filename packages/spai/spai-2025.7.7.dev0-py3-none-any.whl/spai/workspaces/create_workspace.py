from ..repos.APIRepo import APIRepo


def create_workspace(user, workspace_name):
    repo = APIRepo()
    data, error = repo.create_workspace_for_user(user, workspace_name)
    if error:
        raise Exception(error)
    return data
