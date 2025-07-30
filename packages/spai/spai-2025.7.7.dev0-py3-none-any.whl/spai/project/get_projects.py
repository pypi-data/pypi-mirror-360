from ..repos import APIRepo


def get_projects(user):
    repo = APIRepo()
    projects = repo.retrieve_projects(user)
    return [project["name"] for project in projects]


def get_projects_names_in_workspace(user, workspace):
    repo = APIRepo()
    projects_in_workspace, error = repo.retrieve_projects_in_workspace(user, workspace)
    if error:
        raise Exception(f"Error retrieving projects in workspace: {error}")
    return [project['name'] for project in projects_in_workspace]


def get_project_in_workspace(user, workspace_name, project_name):
    repo = APIRepo()
    projects_in_workspace, error = repo.retrieve_projects_in_workspace(user, workspace_name)
    if error:
        raise Exception("Error retrieving projects in workspace")
    
    for project in projects_in_workspace:
        if project['name'] == project_name:
            return project
    raise Exception(f"No project named '{project_name}' found in workspace '{workspace_name}'.")
