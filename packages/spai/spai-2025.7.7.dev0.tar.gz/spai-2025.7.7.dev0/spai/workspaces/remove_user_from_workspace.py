

from ..repos import APIRepo
from ..workspaces.get_workspaces import get_workspaces

def remove_user_from_workspace(user, user_email_to_remove, workspace_name):
    repo = APIRepo()
    workspaces = get_workspaces(user)
    
    workspace_id = None
    for workspace in workspaces:
        if workspace["name"] == workspace_name:
            workspace_id = workspace['id']
    
    if not workspace_id:
        raise Exception(f"Workspace {workspace_name} not found for user {user['name']}")

    data, error = repo.remove_user_from_workspace(user, user_email_to_remove, workspace_id)
    if error:
        raise Exception(f"Error removing user role for workspace: {error}")
    return data
