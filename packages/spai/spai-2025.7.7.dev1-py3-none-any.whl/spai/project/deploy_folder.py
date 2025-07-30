import os
import zipfile
import shutil

from ..config import load_and_validate_config
from ..repos import APIRepo


def create_zip_from_folders(folders, files, zip_path, root):
    # parent_root = os.path.dirname(root)
    parent_root = root
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for folder in folders:
            for folderName, subfolders, filenames in os.walk(folder):
                if "node_modules" in folderName:
                    continue
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipf.write(filePath, os.path.relpath(filePath, parent_root))
        for file in files:
            zipf.write(file, os.path.relpath(file, parent_root))


def deploy_folder(user, path, variables, typer, verbose=False):
    config = load_and_validate_config(path, typer, verbose=verbose, cloud=True)
    typer.echo(f"Deploying...")
    # zip the folder
    folders, files = [], []
    for script in config.scripts:
        folders.append(f"{path}/scripts/{script.name}")
    for api in config.apis:
        folders.append(f"{path}/apis/{api.name}")
    for ui in config.uis:
        folders.append(f"{path}/uis/{ui.name}")
    for notebook in config.notebooks:
        folders.append(f"{path}/notebooks/{notebook.name}")
    files.append(f"{path}/spai.config.yaml")
    if os.path.isfile(f"{path}/spai.vars.json"):
        files.append(f"{path}/spai.vars.json")
    dst_path = f"/tmp/spai"
    os.makedirs(dst_path, exist_ok=True)
    zip_path = f"{dst_path}/{config.project}.zip"
    create_zip_from_folders(folders, files, zip_path, root=config.project)
    if config.workspace:
        if variables.get("workspace"):
            raise Exception(
                "Multiple workspace names provided in variables and config. Please provide only one."
            )
        variables.update({"workspace": config.workspace})
    # send to api for deployment
    repo = APIRepo()
    data, error = repo.deploy_folder(user, zip_path, variables)
    # clean up
    shutil.rmtree(dst_path)
    if data:
        typer.echo(
            f"Check status at {os.getenv('SPAI_UI_URL', 'https://spai.earthpulse.ai')}/projects/{data['project_id']}"
        )
        return
    raise Exception(f"Error: {error}")
