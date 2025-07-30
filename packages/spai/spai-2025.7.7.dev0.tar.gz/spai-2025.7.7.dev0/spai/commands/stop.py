import typer

from ..project import (
    get_services,
    stop_service,
    stop_service_by_name,
    get_projects
)
from ..project import get_services, stop_service, get_projects_names_in_workspace
from ..auth import auth



app = typer.Typer(help="Stop projects and/or services")


@app.command(help="Stop services in a project")
def project(
    project_name: str = typer.Argument(help="Project name"),
    workspace_name: str = typer.Option("default", "--workspace", "-w", help="Workspace name"),
):
    try:
        user = auth()
        projects = get_projects_names_in_workspace(user, workspace_name)
        
        for project in projects:
            if project != project_name:
                continue

            services = get_services(user, project)
            if len(services) == 0:
                typer.echo(f"No services running in project '{project}'.")
                return
            typer.echo(f"Stopping all services in project '{project}'...")
            for service in services:
                stop_service(user, service["id"])
            typer.echo(f"Stopped all services in project '{project}'.")
            return
        else:
            raise Exception(f"Project {project_name} not found in workspace {workspace_name}")
    except Exception as e:
        return typer.echo(e)


@app.command(help="Stop a specific service by providing service type and name")
def service(
    project_name: str = typer.Argument(help="Project name"),
    service_type: str = typer.Argument(help="Service type"),
    service_name: str = typer.Argument(help="Service name"),
    workspace_name: str = typer.Option("default", "--workspace", "-w", help="Workspace name"),
):
    try:
        user = auth()
        projects = get_projects_names_in_workspace(user, workspace_name)
        
        if not projects:
            return typer.echo(f"No projects found in workspace '{workspace_name}'.")

        for project in projects:
            if project != project_name:
                continue
            # check where stop_service_by_name is used
            service = stop_service_by_name(user, project, service_type, service_name, workspace_name)
            if service is None:
                typer.echo(f"Service '{service_name}' not found in project '{project}'.")
                return
            typer.echo(f"Stopped service '{service_name}' in project '{project}'.")
        return
    except Exception as e:
        return typer.echo(e)
    

@app.command(help="Stop all projects in one or all workspaces")
def all_projects(
    workspace_name: str = typer.Argument("default", help="Workspace name"),
    all_workspaces: bool = typer.Option(
        False, "-aw", "--all-workspaces", help="Stop all projects in all workspaces"
    ),
):
    try:
        user = auth()
        if all_workspaces:
            projects = get_projects(user)
        else:
            projects = get_projects_names_in_workspace(user, workspace_name)
        
        if not projects:
            return typer.echo(f"No projects found in workspace '{workspace_name}'.")

        for project in projects:
            services = get_services(user, project)
            if len(services) == 0:
                typer.echo(f"No services running in project '{project}'.")
                continue
            typer.echo(f"Stopping all services in project '{project}'...")
            for service in services:
                stop_service(user, service["id"])
            typer.echo(f"Stopped all services in project '{project}'.")
        return
    except Exception as e:
        return typer.echo(e)
