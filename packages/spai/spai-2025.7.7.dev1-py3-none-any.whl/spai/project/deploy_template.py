from ..repos import APIRepo
import os


def deploy_template(user, template_name, variables, typer):
    repo = APIRepo()
    data, error = repo.deploy_template(user, template_name, variables)
    if data:
        typer.echo(
            f"Check status at {os.getenv('SPAI_UI_URL', 'https://spai.earthpulse.ai')}/projects/{data['project_id']}"
        )
        return
    raise Exception(f"Error: {error}")
