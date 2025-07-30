from pydantic import BaseModel


class GetLogs:
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        user: dict
        project: str
        service: str
        name: str

    class Outputs(BaseModel):
        logs: str

    def __call__(self, inputs: Inputs) -> Outputs:
        logs = self.repo.get_logs(
            inputs.user, inputs.project, inputs.service, inputs.name
        )
        return self.Outputs(logs=logs)
