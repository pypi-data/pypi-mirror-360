from pydantic import BaseModel
from typing import Union, List
from pathlib import Path
from typing import Optional

from .StorageConfig import LocalStorageConfig, S3StorageConfig

class Resources(BaseModel):
    cpu: Optional[Union[str, float]] = None
    memory: Optional[str] = None
    gpu: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        # make sure that if gpu is set, cpu and memory are not
        if self.gpu is not None:
            if self.cpu is not None or self.memory is not None:
                raise ValueError("When GPU is set, CPU and memory must not be set.")
            # gpu should be 0 or 1
            if self.gpu < 0 or self.gpu > 1:
                raise ValueError("GPU must be 0 or 1.")
        # make sure cpu and gpu are positive
        if self.cpu is not None and self.cpu < 0:
            raise ValueError("CPU must be positive.")
        if self.gpu is not None and self.gpu < 0:
            raise ValueError("GPU must be positive.")
    
            
class Autoscaling(BaseModel):
    min: Optional[int] = 0
    max: Optional[int] = 1
    keep_alive: Optional[int] = 300 # seconds

    def __init__(self, **data):
        super().__init__(**data)
        if self.max < self.min:
            raise ValueError("Max must be larger than min.")
        if self.max > 3:
            raise ValueError("Max must be 3 or less.")
        if self.keep_alive < 60:
            raise ValueError("Keep alive must be 60 or more.")
        # make sure min is not negative
        if self.min is not None and self.min < 0:
            raise ValueError("Min must be 0 or more.")

class ScriptConfig(BaseModel):
    name: str
    run_on_start: bool = True
    command: Optional[str] = None
    run_every: Optional[int] = None  # seconds (in cloud minutes)
    storage: Optional[str] = None  # folder to bind in cloud
    type: str = "script"
    resources: Resources = Resources()

    def __init__(self, **data):
        super().__init__(**data)
        # make sure that at least run_on_start or run_every is set
        if not self.run_on_start and not self.run_every:
            raise ValueError(
                f"Script {self.name} must have either run_on_start or run_every set."
            )
        # make sure storage is None, we set it later (user should not set it)
        if self.storage is not None:
            raise ValueError("Storage should not be set by the user.")
        

class NotebookConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    storage: Union[str, None] = None  # folder to bind in cloud
    port: int = 8888
    host: str = "0.0.0.0"
    type: str = "notebook"
    resources: Resources = Resources()
    autoscaling: Autoscaling = Autoscaling()
    domain: str = None

    def __init__(self, **data):
        super().__init__(**data)
        # make sure storage is None, we set it later (user should not set it)
        if self.storage is not None:
            raise ValueError("Storage should not be set by the user.")
        # make sure autoscaling max is 1
        if self.autoscaling.max != 1:
            raise ValueError("Autoscaling max must be 1 for notebooks.")
        if self.domain is not None and not self.domain.endswith(".earthpulse.ai"):
            raise ValueError("domain must end in .earthpulse.ai")

class APIConfig(BaseModel):
    name: str
    command: Union[str, None] = None
    port: int = 8000
    host: str = "0.0.0.0"
    reload: bool = False
    storage: Union[str, None] = None  # folder to bind in cloud
    type: str = "api"
    resources: Resources = Resources()
    autoscaling: Autoscaling = Autoscaling()
    domain: str = None

    # make sure storage is None, we set it later (user should not set it)
    def __init__(self, **data):
        super().__init__(**data)
        if self.storage is not None:
            raise ValueError("Storage should not be set by the user.")
        if self.domain is not None and not self.domain.endswith(".earthpulse.ai"):
            raise ValueError("domain must end in .earthpulse.ai")

class UIConfig(BaseModel):
    name: str
    command: str  # steamlit, javascript, ...
    port: int = 3000
    host: str = "0.0.0.0"
    env: dict = {}  # can accept the name of another service as a url placeholder
    type: str = "ui"
    resources: Resources = Resources()
    autoscaling: Autoscaling = Autoscaling()
    domain: str = None
    def __init__(self, **data):
        super().__init__(**data)
        # make sure is not using GPU
        if self.resources.gpu is not None:
            raise ValueError("GPU is not supported for UIs.")
        if self.domain is not None and not self.domain.endswith(".earthpulse.ai"):
            raise ValueError("domain must end in .earthpulse.ai")

class Config(BaseModel):
    dir: Path
    project: str
    scripts: List[ScriptConfig] = []
    notebooks: List[NotebookConfig] = []
    apis: List[APIConfig] = []
    uis: List[UIConfig] = []
    storage: List[Union[LocalStorageConfig, S3StorageConfig]] = []
    workspace: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)

    # iterator for all the services
    def __iter__(self):
        # if self.storage:
        #     for storage in self.storage:
        #         yield storage
        if self.scripts:
            for script in self.scripts:
                yield script
        if self.notebooks:
            for notebook in self.notebooks:
                yield notebook
        if self.apis:
            for api in self.apis:
                yield api
        if self.uis:
            for ui in self.uis:
                yield ui
        if self.storage:
            for storage in self.storage:
                yield storage

    def type2folder(self, type):
        return type + "s"
