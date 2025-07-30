from ..repos import APIRepo

from .get_project_by_name import get_project_by_name
from ..workspaces.get_workspaces import get_workspaces
from ..workspaces.update_workspace import update_workspace

def delete_project(user, project):
    repo = APIRepo()
    project = get_project_by_name(user, project)
    data, error = repo.delete_project(user, project["id"])
    if error:
        raise Exception("Something went wrong.\n" + error)

    workspaces = get_workspaces(user)
    for workspace in workspaces:
        if project["id"] in workspace["project_ids"]:
            print(f"found Project {project['id']} in workspace {workspace['name']}")

            workspace["project_ids"].remove(project["id"])
            data = update_workspace(user, workspace)
            if error:
                raise Exception(f"error updating workspace: {error}")

    return data
