from ..repos import APIRepo


def get_services(user, project_name, format=False):
    repo = APIRepo()
    data, error = repo.retrieve_project_by_name(user, project_name)
    services = []
    if data and "services" in data:
        if not format:
            return data["services"]
        for service in data["services"]:
            data, error = repo.retrieve_service(user, service["id"])
            if error:
                print("Something went wrong.\n" + error)
            if data["type"] == "s3":
                services.append(
                    {
                        "type": data["type"],
                        "url": data["url"],
                        "bucket": data["bucket"],
                        "region": data["region"],
                    }
                )
                continue
            if data["type"] == "script":
                services.append(
                    {
                        "type": data["type"],
                        "name": data["name"],
                    }
                )
                continue
            if (
                data["type"] == "api"
                or data["type"] == "ui"
                or data["type"] == "notebook"
            ):
                services.append(
                    {
                        "type": data["type"],
                        "name": data["name"],
                        "url": data["url"],
                    }
                )
                continue
            raise Exception("Invalid service type")
        return services
    raise Exception("Something went wrong.\n" + error)
