import os
from .validate import load_config

class SPAIConfig:
    def __init__(self):
        current_dir = os.getcwd()
        max_tries, current_try = 3, 1
        self.config = None
        while current_try <= max_tries:
            file_path = current_dir + "/spai.config.yaml"
            if os.path.isfile(file_path):
                print(f"Loading config from {file_path}")
                self.config = load_config(current_dir).model_dump()
                break
            current_try += 1
            # go up one directory
            current_dir = os.path.dirname(current_dir)
        if self.config is None:
            print("No config file found")

    def __getitem__(self, key):
        if self.config and key in self.config:
            return self.config[key]
        else:
            raise KeyError(f"{key} not found in config")

    def __repr__(self) -> str:
        if self.config:
            return str(self.config)
