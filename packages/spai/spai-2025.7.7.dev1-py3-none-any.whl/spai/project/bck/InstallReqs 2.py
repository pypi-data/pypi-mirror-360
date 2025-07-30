from pydantic import BaseModel
from pathlib import Path
import os
from ...models import Config


class InstallReqs:
    def __init__(self, logger=None):
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        config: Config

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # install requirements.txt in each service folder
        for service in inputs.config:
            self.logger(f"Installing requirements for service '{service.name}'...")
            service_path = (
                inputs.config.dir
                / inputs.config.type2folder(service.type)
                / service.name
            )
            reqs_path = service_path / "requirements.txt"
            if not reqs_path.exists():
                self.logger(f"No requirements.txt found for service '{service.name}'.")
                continue
            os.system(f"pip install -r {str(reqs_path)}")
        return self.Outputs(message="done")
