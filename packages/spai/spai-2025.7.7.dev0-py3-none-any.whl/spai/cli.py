import typer
from pathlib import Path
from typing import List

from .project.get_project_by_name import get_project_by_name

# Add the cli directory to the Python path
# spai_cli_dir = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(spai_cli_dir))

from .commands import auth as _auth
from .commands import list, workspace, stop
from .repos import APIRepo
from .project import (
    init_project,
    install_requirements,
    run_local,
    deploy_folder,
    get_logs,
    download_template,
    deploy_template,
    get_services,
    stop_service,
    delete_project,
    get_projects_names_in_workspace,
    get_project_in_workspace
)

from .auth import auth
from .config import parse_vars
from . import __version__

app = typer.Typer(help="Welcome to SPAI")
app.add_typer(_auth.app, name="auth")
app.add_typer(list.app, name="list")
app.add_typer(workspace.app, name="workspace")
app.add_typer(stop.app, name="stop")


@app.command(help="Create a new project from starter template")
def init(
    project_name=typer.Argument(None, help="Project name"),
    path: Path = typer.Option(Path.cwd(), "-p", "--path", help="Project path"),
    template: str = typer.Option(None, "-t", "--template", help="Template name"),
    force: bool = typer.Option(False, "-f", "--force", help="Force download template"),
):
    try:
        if template:
            user = auth()
            path = download_template(user, template, path, force)
            return typer.echo(f"Project created at {path}")
        assert project_name is not None, "Project name is required."
        init_project(path, project_name)
        typer.echo(f"Project {project_name} created at {path}")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(help="Install requirements for a project")
def install(
    path: Path = typer.Argument(Path.cwd(), help="Project path"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    try:
        install_requirements(path, typer, verbose)
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(help="Run a project locally")
def run(
    path: Path = typer.Argument(Path.cwd(), help="Project path"),
    template: str = typer.Option(None, "-t", "--template", help="Template name"),
    template_path: Path = typer.Option(
        Path.cwd(),
        "-p",
        "--path",
        help="Destination path for the project created from the template",
    ),
    force: bool = typer.Option(False, "-f", "--force", help="Force download template"),
    install_reqs: bool = typer.Option(
        False, "-i", "--install-reqs", help="Install requirements"
    ),
    vars: List[str] = typer.Option(
        [], "--var", "-v", help="Variables to pass to the template"
    ),
):
    try:
        variables = parse_vars(vars)    
        if template is not None:
            user = auth()
            path = download_template(user, template, template_path, force)
        if install_reqs:
            install_requirements(path, typer, False)
        return run_local(path, variables, typer)
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(help="Deploy a project to the cloud")
def deploy(
    path: Path = typer.Argument(Path.cwd(), help="Project path"),
    template: str = typer.Option(None, "-t", "--template", help="Template name"),
    workspace: str = typer.Option(None, "-w", "--workspace", help="Workspace name"),
    verbose: bool = typer.Option(False, "--verbose"),
    vars: List[str] = typer.Option(
        [], "--var", "-v", help="Variables to pass to the template"
    ),
):
    try:
        user = auth()
        variables = parse_vars(vars)
        if workspace:   
            variables.update({"workspace": workspace})
        if template:
            return deploy_template(user, template, variables, typer)
        return deploy_folder(user, path, variables, typer, verbose)
    except Exception as e:
        import traceback
        typer.echo(traceback.format_exc())
        typer.echo(f"Error: {e}")


@app.command(help="Retrieve the logs of a service")
def logs(
    project_name: str = typer.Argument(..., help="Project name"),
    service_type: str = typer.Argument(
        ..., help="Service type (script, api, ui, etc.)"
    ),
    service_name: str = typer.Argument(..., help="Service name"),
):
    try:
        user = auth()
        logs = get_logs(user, project_name, service_type, service_name)
        typer.echo(logs)
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(help="Clone a template")
def clone(
    template: str = typer.Argument(..., help="Template name"),
    path: Path = typer.Option(
        Path.cwd(),
        "-p",
        "--path",
        help="Destination path for the project created from the template",
    ),
    force: bool = typer.Option(False, "-f", "--force", help="Force download template"),
):
    try:
        user = auth()
        path = download_template(user, template, path, force)
        typer.echo(f"Template available at {path}.")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(help="Delete a project")
def delete(
    project_name: str = typer.Argument(help="Project name"),
    workspace_name: str = typer.Option("default", "--workspace", "-w", help="Workspace name"),
    force: bool = typer.Option(
        False, "-f", "--force", help="Force delete project without confirmation"
    ),
):
    try:
        user = auth()
        # check if project exists in workspace
        projects = get_projects_names_in_workspace(user, workspace_name)
        if not projects:
            return typer.echo(f"Project '{project_name}' not found in workspace '{workspace_name}'")

        if force:
            projects = get_projects_names_in_workspace(user, workspace_name)
            for project in projects:
                if project != project_name:
                    continue
                services = get_services(user, project)
                for service in services:
                    stop_service(user, service["id"])

        delete_project(user, project_name)
        return typer.echo(f"Deleted project '{project_name}'.")
    except Exception as e:
        return typer.echo(e)


@app.command(help="get project")
def get_project(
    project_name: str = typer.Argument(..., help="Project name"),
    workspace: str = typer.Argument(..., help="Workspace name")
):
    try:
        user = auth()
        project = get_project_in_workspace(user, workspace, project_name)
        if project:
            typer.echo(f"Project '{project_name}' found in workspace '{workspace}':")
            typer.echo(f"ID: {project['id']}")
            typer.echo(f"Name: {project['name']}")
            typer.echo(f"Description: {project.get('description', 'No description')}")
            typer.echo(f"Created At: {project['created_at']}")
        else:
            typer.echo(f"No project named '{project_name}' found in workspace '{workspace}'.")

    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(help="Get SPAI version")
def version():
    typer.echo(f"SPAI Version: {__version__}")


@app.command(help="Get SPAI API url and status")
def api():
    repo = APIRepo()
    typer.echo(f"SPAI API URL: {repo.url}")
    typer.echo(repo.info())


if __name__ == "__main__":
    app()
