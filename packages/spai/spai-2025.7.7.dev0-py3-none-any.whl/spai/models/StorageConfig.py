from pydantic import BaseModel, field_validator
from typing import Optional


class StorageConfig(BaseModel):
    type: str
    name: str


class LocalStorageConfig(StorageConfig):
    path: Optional[str] = None

    @field_validator("type")
    @classmethod
    def type_must_be_local(cls, v):
        if not v == "local":
            raise ValueError("type must be local")
        return v

    @field_validator("path", mode="before")
    @classmethod
    def user_name_as_path_if_not_path(cls, v, *, values, **kwargs):
        return v or values["name"]


class S3StorageCredentials(BaseModel):
    url: str
    access_key: str
    secret_key: str
    bucket: str
    region: Optional[str] = (
        None  # en local no hace falta, además afecta a la conexión segura o no
    )


class S3StorageConfig(StorageConfig):
    credentials: Optional[S3StorageCredentials] = None

    @field_validator("type")
    @classmethod
    def type_must_be_s3(cls, v):
        if not v == "s3":
            raise ValueError("type must be s3")
        return v
