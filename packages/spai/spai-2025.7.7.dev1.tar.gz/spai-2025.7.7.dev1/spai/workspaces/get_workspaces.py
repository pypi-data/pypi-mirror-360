from ..repos import APIRepo

def get_workspaces(user):
    repo = APIRepo()
    data, error = repo.retrieve_workspaces_by_user(user)
    if error:
        raise Exception(f"Error occured retrieving workspaces: {error}")
    return data
