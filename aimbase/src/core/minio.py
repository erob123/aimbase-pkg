
from .config import get_aimbase_settings
from instarest import LogConfig
from fastapi import HTTPException
from minio.error import InvalidResponseError
from minio import Minio
import hashlib
from pathlib import Path
from tqdm import tqdm

logger = LogConfig("minio.py").build_logger()

def build_client():

    if not get_aimbase_settings().minio_region:
        return Minio(
                get_aimbase_settings().minio_endpoint_url,
                access_key=get_aimbase_settings().minio_access_key,
                secret_key=get_aimbase_settings().minio_secret_key,
                secure=get_aimbase_settings().minio_secure
            )

    return Minio(
            get_aimbase_settings().minio_endpoint_url,
            access_key=get_aimbase_settings().minio_access_key,
            secret_key=get_aimbase_settings().minio_secret_key,
            secure=get_aimbase_settings().minio_secure,
            region=get_aimbase_settings().minio_region
        )

def download_folder_from_minio(s3: Minio, folder_name: str) -> str:
    # Create a directory for the downloaded files
    local_folder_path = Path(folder_name)
    local_folder_path.mkdir(parents=True, exist_ok=True)

    # Calculate the SHA256 hash while streaming and downloading files
    hash_object = hashlib.sha256()

    try:
        # List all objects in the bucket with the given prefix (folder_name)
        objects = s3.list_objects(bucket_name=get_aimbase_settings().minio_bucket_name, prefix=folder_name)

        # Sort the objects to ensure a deterministic order of processing files
        sorted_objects = sorted(objects, key=lambda obj: obj.object_name)

        for obj in sorted_objects:
            filename = obj.object_name
            local_file_path = local_folder_path / filename

            # Download and write the file contents to disk while updating the hash
            data = s3.get_object(bucket_name=get_aimbase_settings().minio_bucket_name, object_name=filename)
            with open(local_file_path, 'wb') as f:
                for chunk in tqdm(data.stream(32*1024), unit='B', unit_scale=True):
                    f.write(chunk)
                    hash_object.update(chunk)

    except InvalidResponseError as e:
        logger.error(f"Failed to download file from Minio: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

    finally:
        # Ensure data.close() and data.release_conn() always execute, even if an error occurs
        data.close()
        data.release_conn()

    # Get the final SHA256 hash value
    hex_dig = hash_object.hexdigest()

    return hex_dig