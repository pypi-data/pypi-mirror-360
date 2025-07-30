from minio import Minio
import os


def get_client():
    """
    Get a Minio client instance.
    """
    if "S3_REGION" in os.environ:
        return Minio(
            endpoint=os.environ["S3_ENDPOINT"],
            access_key=os.environ["ACCESS_KEY_ID"],
            secret_key=os.environ["SECRET_ACCESS_KEY"],
            secure=True,
            region=os.environ["S3_REGION"],
        )
    return Minio(
        endpoint=os.environ["S3_ENDPOINT"],
        access_key=os.environ["ACCESS_KEY_ID"],
        secret_key=os.environ["SECRET_ACCESS_KEY"],
        secure=False,
    )