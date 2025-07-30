from ..repos import AuthRepo


def is_logged():
    repo = AuthRepo()
    return repo.load_creds()
