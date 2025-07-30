from ..repos.APIRepo import APIRepo


def remove_workspace(user, workspace_id):
    repo = APIRepo()
    data, error = repo.remove_workspace(user, workspace_id)
    if error:
        raise Exception(f"Error removing workspace: {error}")
    return data
