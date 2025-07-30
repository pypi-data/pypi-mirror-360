import os

from ..config import load_and_validate_config


def install_requirements(path, typer, verbose):
    config = load_and_validate_config(path, typer, verbose)
    # install requirements.txt in each service folder
    for service in config:
        service_path = config.dir / config.type2folder(service.type) / service.name
        reqs_path = service_path / "requirements.txt"
        if not reqs_path.exists():
            # typer.echo(
            #     f"No requirements.txt found for {service.type} '{service.name}'."
            # )
            continue
        typer.echo(f"Installing requirements for {service.type} '{service.name}'...")
        os.system(f"pip install -r {str(reqs_path)}")
    return "done"
