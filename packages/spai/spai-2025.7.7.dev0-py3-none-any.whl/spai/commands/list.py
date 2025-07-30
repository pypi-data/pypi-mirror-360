import traceback
import typer
from ..project import get_projects, get_services
from ..auth import auth
from rich import print

from ..workspaces.get_workspaces import get_workspaces

app = typer.Typer(help="Retrieve information about your projects and services")


@app.command(help="List all projects")
def projects():
    try:
        user = auth()
        projects = get_projects(user)
        if len(projects) == 0:
            return typer.echo(f"No projects found.")
        typer.echo("Projects:")
        for project in projects:
            typer.echo(project)
    except Exception as e:
        typer.echo(traceback.format_exc())


@app.command(help="List all services in a project")
def services(
    project: str = typer.Argument(..., help="Project name"),
):
    try:
        user = auth()
        if project is None:
            raise Exception("Project name is required.")
        services = get_services(user, project, format=True)
        if len(services) == 0:
            return typer.echo(f"No services running in project '{project}'.")
        typer.echo(f"Services in project '{project}':")
        return
    except Exception as e:
        return typer.echo(traceback.format_exc())


@app.command(help="List all your workspaces")
def workspaces():
    try:
        user = auth()
        workspaces = get_workspaces(user)
        typer.echo(f"Workspaces found: {[workspace['name'] for workspace in workspaces]}")
    except Exception as e:
        return typer.echo(traceback.format_exc())


if __name__ == "__main__":
    app()
