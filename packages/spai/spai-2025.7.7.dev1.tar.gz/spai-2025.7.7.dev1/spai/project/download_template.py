import requests
import zipfile
import io
import shutil

from ..repos import APIRepo


def download_template(user, template, template_path, force):
    repo = APIRepo()
    response = repo.retrieve_template(user, template)
    if response.status_code == 200:
        data = response.json()
        # raise error if already exists
        path = template_path / data["name"]
        if path.exists():
            print("Project already exists, use -f to re-download")
            if force:
                shutil.rmtree(path)
        if not path.exists() or force:
            # clone github repo with template
            print(f"Downloading {data['name']}...")
            zip_url = (
                data["url"] + "/archive/main.zip"
            )  # OJO asume que la rama se llama main !!!
            r = requests.get(zip_url, stream=True)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(path=template_path)
            # move files to template_path
            repo_name = data["url"].split("/")[-1]
            branch = "main"  # TODO: cambiar
            shutil.move(f"{repo_name}-{branch}", path)
        return path
    raise Exception(response.json()["detail"])
