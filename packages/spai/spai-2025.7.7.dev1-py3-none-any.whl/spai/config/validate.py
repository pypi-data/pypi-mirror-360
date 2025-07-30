import os
import json
import yaml
from ..models import Config
from rich import print
from typing import List
from pathlib import Path


def validate_folder(dir, folder, typer):
    if not os.path.exists(dir / folder):
        raise typer.BadParameter(f"No {folder} directory found in '{dir}'.")


def validate_item(dir, folder, item, name, typer, file="main.py", check_file=True):
    # check name
    if not item.name:
        raise typer.BadParameter(f"{name} '{item.name}' is missing 'name' attribute.")
    # check folder has folder with item name
    if not os.path.exists(dir / folder / item.name):
        raise typer.BadParameter(
            f"{name} '{item.name}' cannot be found in {dir}/{folder}."
        )
    # check folder has file
    if not file in os.listdir(dir / folder / item.name):
        if check_file:
            raise typer.BadParameter(f"{name} '{item.name}' is missing file 'main.py'.")
        # print(
        #     f"Warning: file 'main.py' not found in {dir}/{folder}/{item.name}, skipping file check."
        # )
    # TODO: check optionals: reqs, env...


def validate_storage(storage, typer, cloud):
    if storage.type == "local" and cloud:
        raise typer.BadParameter(
            f"Local storage not allowed in cloud deployment, please use S3 storage."
        )
    # if storage.type == "s3" and not storage.credentials:
    #     typer.echo(
    #         f"S3 storage credentials not provided, an S3 bucket will be created if it does not already exist."
    #     )

def load_config(dir):
    dir = Path(dir).resolve()
    # check dir exists
    if not dir.exists():
        raise Exception(f"Directory '{dir}' does not exist.")
    # check dir is a spai project
    if not "spai.config.yaml" in os.listdir(
        dir
    ) and not "spai.config.yml" in os.listdir(dir):
        raise Exception(
            f"Directory '{dir}' is not a spai project. No spai.config.yaml file found."
        )
    # load config
    config = {}
    with open(dir / "spai.config.yaml", "r") as f:
        config = yaml.safe_load(f)
    if not config:
        raise Exception(f"spai.config.yaml file is empty.")
    config.update(dir=dir)
    config = Config(**config)
    # TODO: check if project name is already taken in cloud, locally is not a problem
    config.project = dir.name if not config.project else config.project
    return config

def load_and_validate_config(dir, typer, verbose=False, cloud=False):
    config = load_config(dir)
    # check storage
    if config.storage:
        names = []
        for storage in config.storage:
            if storage.name in names:
                raise typer.BadParameter(
                    f"Found multiple storages with name '{storage.name}', please use unique names for your storage."
                )
            validate_storage(storage, typer, cloud)
            names.append(storage.name)
    # check scripts
    if config.scripts:
        # check project has scripts folder
        validate_folder(dir, "scripts", typer)
        for script in config.scripts:
            validate_item(dir, "scripts", script, "script", typer)
    # check apis
    if config.apis:
        # check project has apis folder
        validate_folder(dir, "apis", typer)
        for api in config.apis:
            validate_item(dir, "apis", api, "api", typer)
    # check uis
    if config.uis:
        # check project has uis folder
        validate_folder(dir, "uis", typer)
        for ui in config.uis:
            validate_item(dir, "uis", ui, "ui", typer, check_file=False)
    # check notebooks
    if config.notebooks:
        # check project has notebooks folder
        validate_folder(dir, "notebooks", typer)
        for notebook in config.notebooks:
            validate_item(dir, "notebooks", notebook, "notebook", typer, "main.ipynb")  
    return config
