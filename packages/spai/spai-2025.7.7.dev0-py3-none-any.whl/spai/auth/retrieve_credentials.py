from ..repos import APIRepo


def retrieve_credentials(user):
    repo = APIRepo()
    data, error = repo.retrieve_user(user)
    if error:
        raise Exception(error)
    access_key = data.get("access_key")
    secret_key = data.get("secret_key")
    if not access_key or not secret_key:
        raise Exception("No credentials found.")
    return {"AWS_ACCESS_KEY_ID": access_key, "AWS_SECRET_ACCESS_KEY": secret_key}
