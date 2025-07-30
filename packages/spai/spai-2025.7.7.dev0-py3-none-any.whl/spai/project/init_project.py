import shutil
from pathlib import Path
import json


def init_project(path, project_name):
    # copy template
    template = Path(__file__).parent / "project-template"
    shutil.copytree(template, path / project_name)
    # change name to project in spai.config.yaml
    config = path / project_name / "spai.config.yaml"
    # read json and change name
    with open(config, "r") as f:
        json = f.read()
    json = json.replace("project-template", project_name)
    with open(config, "w") as f:
        f.write(json)
