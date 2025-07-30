from pydantic import BaseModel
from typing import List


class StopService:
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        user: dict
        project: str
        service: str
        name: str

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        message = self.repo.stop_service(
            inputs.user, inputs.project, inputs.service, inputs.name
        )
        return self.Outputs(message=message)
