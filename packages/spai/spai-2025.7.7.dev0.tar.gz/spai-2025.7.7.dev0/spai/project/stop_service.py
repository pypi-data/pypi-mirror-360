from ..repos import APIRepo


def stop_service(user, service_id):
    repo = APIRepo()
    data, error = repo.retrieve_service(user, service_id)
    if error:
        raise Exception("Something went wrong.\n" + error)
    if "type" in data and "name" in data:
        print(f"Stopping service {data['type']}/{data['name']} ...")
        return repo.stop_service(user, service_id)
    return
    

def stop_service_by_name(user, project, service_type, service_name, workspace_name):
    repo = APIRepo()

    projects, error = repo.retrieve_projects_in_workspace(user, workspace_name=workspace_name)
    

    for p in projects:
        if p["name"] == project:
            print(f"Stopping service {service_type}/{service_name} in {p['name']} workspace '{workspace_name}'")
            data, error = repo.stop_service_by_name(
                user, p["id"], service_type, service_name
            )
            if error:
                raise Exception("Something went wrong.\n" + error)
            return data
    raise Exception(f"Project '{project}' not found in workspace '{workspace_name}'")
