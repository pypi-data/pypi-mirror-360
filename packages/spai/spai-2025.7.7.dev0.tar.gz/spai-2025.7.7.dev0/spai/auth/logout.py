from ..repos import AuthRepo, APIRepo


def generate_logout_url():
    repo, api_repo = AuthRepo(), APIRepo()
    repo.logout()
    return api_repo.logout_url()
