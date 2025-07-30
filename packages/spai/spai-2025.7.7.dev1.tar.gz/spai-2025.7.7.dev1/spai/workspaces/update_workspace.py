from ..repos.APIRepo import APIRepo


def update_workspace(user, workspace):
    repo = APIRepo()
    data, error = repo.update_workspace(user, workspace)
    if error:
        raise Exception(f"Error updating workspace: {error}")
    return data
