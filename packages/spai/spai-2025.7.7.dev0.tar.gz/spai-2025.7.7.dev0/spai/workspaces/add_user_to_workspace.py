import traceback
from ..workspaces.get_workspaces import get_workspaces
from ..repos.APIRepo import APIRepo


def add_user_to_workspace(user, user_email_to_add, role, workspace_name):
    if role not in ["guest", "developer", "maintainer"]:
        raise ValueError("Role must be one of guest, developer, maintainer")
    
    repo = APIRepo()
    
    workspace_id = None
    workspaces = get_workspaces(user)
    for workspace in workspaces:
        if workspace["name"] == workspace_name:
            workspace_id = workspace['id']

    if not workspace_id:
       raise Exception(f"Workspace {workspace_name} not found")

    requested_user = {"email": user_email_to_add, "role": role}
    data, error = repo.add_user_to_workspace(user, requested_user, workspace_id)
    if error:
        print(traceback.format_exc())
        raise Exception(f"Error adding user to workspace: {error}")
    return data
