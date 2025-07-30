import requests
import os
import json


class APIRepo:
    def __init__(
        self, url=os.getenv("SPAI_API_URL", "https://spai-test.earthpulse.ai/")
    ):
        try:
            from bson import ObjectId
        except ImportError:
            raise ImportError(
                "The bson package is required. Please install it with 'pip install bson' and try again."
            )
        self.url = url
        self.url = self.url if self.url.endswith("/") else self.url + "/"
        if not self.url.startswith("http://") and not self.url.startswith("https://"):
            raise Exception(
                "Invalid URL: " + self.url + "\nIt must start with http:// or https://"
            )

    def format_response(self, response):
        if response.status_code == 200:
            return response.json(), None
        return None, response.json()["detail"]

    def info(self):
        return requests.get(self.url).json()

    def login(self):
        return requests.get(self.url + "auth/login")

    def token(self, code):
        return requests.get(self.url + "auth/token?code=" + code)

    def logout_url(self):
        response = requests.get(self.url + "auth/logout")
        return response.json()["logout_url"]

    def get_headers(self, user):
        return {"Authorization": "Bearer " + user["id_token"]}

    def retrieve_user(self, user):
        response = requests.get(self.url + "auth/me", headers=self.get_headers(user))
        return self.format_response(response)

    def retrieve_projects(self, user):
        return requests.get(
            self.url + "projects", headers=self.get_headers(user)
        ).json()

    def retrieve_projects_in_workspace(self, user, workspace_name):
        response = requests.get(
            self.url + "projects/workspace/" + workspace_name,
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def retrieve_project(self, user, project):
        response = requests.get(
            self.url + f"projects/{project}", headers=self.get_headers(user)
        )
        return self.format_response(response)

    def retrieve_project_by_name(self, user, project_name):
        response = requests.get(
            self.url + f"projects?name={project_name}", headers=self.get_headers(user)
        )
        return self.format_response(response)

    def retrieve_workspaces_by_user(self, user):
        response = requests.get(
            self.url + f"workspaces", headers=self.get_headers(user)
        )
        return self.format_response(response)

    def create_workspace_for_user(self, user, workspace_name):
        response = requests.post(
            self.url + f"workspaces",
            json={ "name": workspace_name },
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def stop_service(self, user, service_id):
        response = requests.post(
            self.url + f"stop/{service_id}",
            headers=self.get_headers(user),
        )
        if response.status_code == 200:
            return response.text
        return "Something went wrong.\n" + response.json()["detail"]

    def stop_service_by_name(self, user, project_id, service_type, service_name):
        response = requests.post(
            self.url
            + f"stop?project={project_id}&type={service_type}&name={service_name}",
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def get_logs(self, user, service_id):
        response = requests.get(
            self.url + f"logs/{service_id}",
            headers=self.get_headers(user),
        )
        if response.status_code == 200:
            return response.json()
        return "Something went wrong.\n" + response.json()["detail"]

    def delete_project(self, user, project):
        response = requests.delete(
            self.url + f"projects/{project}", headers=self.get_headers(user)
        )
        # print("delete", response.status_code, response.json())
        return self.format_response(response)

    def retrieve_template(self, user, template):
        return requests.get(
            self.url + f"templates?name={template}", headers=self.get_headers(user)
        )

    def deploy_template(self, user, template, variables):
        response = requests.post(
            self.url + f"deploy/template?name={template}",
            json={"variables": variables},
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def deploy_folder(self, user, zip_path, variables):
        response = requests.post(
            self.url + f"deploy",
            files={"folder": open(zip_path, "rb")},
            data={"variables": json.dumps(variables)},
            headers=self.get_headers(user),
        )
        if response.status_code == 413:
            raise Exception("Your project is too large, it can be a maximum of 100 MB.")
        return self.format_response(response)

    def retrieve_service_by_name_type_project(
        self, user, project_id, service_type, service_name
    ):
        response = requests.get(
            self.url
            + f"services?project={project_id}&type={service_type}&name={service_name}",
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def retrieve_service(self, user, service_id):
        response = requests.get(
            self.url + f"services/{service_id}",
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def create_or_retrieve_s3_bucket(self, user, project_name, storage_name):
        response = requests.get(
            self.url
            + f"services/storage/s3?project={project_name}&name={storage_name}",
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def remove_workspace(self, user, workspace_id):
        response = requests.delete(
            self.url + f"workspaces/{workspace_id}", headers=self.get_headers(user)
        )
        return self.format_response(response)

    def update_workspace(self, user, workspace):
        response = requests.patch(
            self.url + f"workspaces/{workspace['id']}",
            json=workspace,
            headers=self.get_headers(user),
        )
        return self.format_response(response)

    def add_user_to_workspace(self, user,requested_user, workspace_id):
        response = requests.patch(
            self.url + f"workspaces/{workspace_id}/add-user",
            json=requested_user,
            headers=self.get_headers(user)
        )
        return self.format_response(response)

    def set_workspace_user_role(self, user, requested_user, workspace_id):
        response = requests.patch(
            self.url + f"workspaces/{workspace_id}/user-role",
            json=requested_user,
            headers=self.get_headers(user)
        )
        return self.format_response(response)

    def remove_user_from_workspace(self, user, user_email, workspace_id):
        response = requests.delete(
            self.url + f"workspaces/{workspace_id}/remove-user/{user_email}", 
            headers=self.get_headers(user)
            )
        return self.format_response(response)
