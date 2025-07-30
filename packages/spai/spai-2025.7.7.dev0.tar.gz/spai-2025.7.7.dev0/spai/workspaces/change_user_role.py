from ..workspaces.get_workspaces import get_workspaces
from ..repos.APIRepo import APIRepo


def change_workspace_user_role(user, user_email_to_change, role, workspace_name):
    if role not in ["guest", "developer", "maintainer"]:
        raise ValueError("Role must be one of guest, developer, maintainer")
    
    repo = APIRepo()
    workspaces = get_workspaces(user)

    workspace_id = None
    for workspace in workspaces:
        if workspace["name"] == workspace_name:
            workspace_id = workspace['id']

    if not workspace_id:
        raise Exception(f"Workspace {workspace_name} not found for user {user['name']}")

    requested_user = {"email": user_email_to_change, "role": role}
    data, error = repo.set_workspace_user_role(user, requested_user, workspace_id)
    if error:
        raise Exception(f"Error changing user role for workspace: {error}")
    return data
