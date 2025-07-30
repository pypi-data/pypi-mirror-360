import os
from .BaseStorage import BaseStorage
from .S3Storage import S3Storage
from .LocalStorage import LocalStorage


class Storage(BaseStorage):
    def __init__(self):
        super().__init__()
        self.storages_names = os.environ.get("SPAI_STORAGE_NAMES", None)
        self.storages = {}
        if self.storages_names:
            self.storages_names = self.storages_names.split(",")
            self.initialize_storage()

    def __getitem__(self, name):
        try:
            return self.storages[name]
        except KeyError:
            raise KeyError(f"Storage '{name}' not found")

    def initialize_storage(self):
        for storage_name in self.storages_names:
            envs = {
                key: value
                for key, value in os.environ.items()
                if key.startswith(f"SPAI_STORAGE_{storage_name.upper()}")
            }
            envs = {key.split("_")[-1].lower(): value for key, value in envs.items()}
            if storage_name.split("_")[0] == "local":
                self.initialize_local(storage_name, envs)
            elif storage_name.split("_")[0] == "s3":
                self.initialize_s3(storage_name, envs)

    def initialize_local(self, name, envs):
        self.storages[f"{name.split('_')[1]}"] = LocalStorage(**envs)

    def initialize_s3(self, name, envs):
        self.storages[f"{name.split('_')[1]}"] = S3Storage(**envs)
