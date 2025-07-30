import typer

from ..workspaces.add_user_to_workspace import add_user_to_workspace
from ..workspaces.change_user_role import change_workspace_user_role
from ..workspaces.remove_workspace import remove_workspace
from ..workspaces.get_workspaces import get_workspaces
from ..workspaces.create_workspace import create_workspace
from ..workspaces.remove_user_from_workspace import remove_user_from_workspace


from ..auth import auth


app = typer.Typer(help="Create or remove workspaces")


@app.command(help="Create workspace")
def create(
    workspace: str = typer.Argument("default", help="Workspace name")
):
    try:
        user = auth()
        create_workspace(user, workspace)
        typer.echo(f"Workspace {workspace} created")
    except Exception as e:
        # typer.echo(traceback.format_exc()) # do not print traceback in cli, can log to file if needed
        typer.echo(e)


@app.command(help="Remove workspace")
def delete(
    workspace: str = typer.Argument(help="Workspace name"),
):
    try:
        user = auth()
        workspaces = get_workspaces(user)
        for w in workspaces:
            if w['name'] == workspace:
                remove_workspace(user, w['id'])
                typer.echo(f"Removed workspace {w['name']}")
                return
        else:
            raise NameError(f"No workspace named {workspace['name']} exists")
    except Exception as e:
        # typer.echo(traceback.format_exc())
        typer.echo(e)


@app.command(help="Add user to workspace")
def add_user(
    user_email_to_add: str = typer.Argument(help="email-address of user to add to workspace"),
    workspace_name: str = typer.Option(..., "-w", "--workspace", help="Workspace name"),
    role: str = typer.Option("guest", "-r", "--role", help="Role, can be any of guest, developer, maintainer")
):
    try:
        user = auth()
        add_user_to_workspace(user, user_email_to_add, role, workspace_name)
        typer.echo(f"Successfully added user {user_email_to_add} to workspace {workspace_name}")
    except Exception as e:
        return typer.echo(f"Error: {e}")


@app.command(help="Set user role in workspace")
def set_user_role(
    user_email_to_change: str = typer.Argument(help="email-address of user to change role of"),
    workspace_name: str = typer.Option(..., "-w", "--workspace", help="Workspace name"),
    role: str = typer.Option(..., "-r", "--role", help="Role to set (guest, developer, maintainer)"),
):
    try:
        user = auth()
        change_workspace_user_role(user, user_email_to_change, role, workspace_name)
        typer.echo(f"Successfully set user role of {user_email_to_change} to {role}")
    except Exception as e:
        return typer.echo(f"Error: {e}")


@app.command(help="Remove user from workspace")
def remove_user(
    user_email_to_remove: str = typer.Argument(help="email-address of user to remove from workspace"),
    workspace_name: str = typer.Option(..., "-w", "--workspace", help="Workspace name"),
):
    try:
        user = auth()
        remove_user_from_workspace(user, user_email_to_remove, workspace_name)
        typer.echo(f"Successfully removed user {user_email_to_remove} from workspace {workspace_name}")
    except Exception as e:
        return typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
