import os
from typing import Any
from pydantic import BaseModel, validator
from aimbase.src.core.constants import MODEL_CACHE_BASEDIR
from aimbase.src.crud.base import CRUDBaseAIModel
from aimbase.src.db.base import BaseAIModel
from minio import Minio
from sqlalchemy.orm import Session
from pathlib import Path
from aimbase.src.core.minio import download_folder_from_minio
from instarest import LogConfig
from logging import Logger

class BaseAIInferenceService(BaseModel):

    # one of sha256 or model_name must be provided
    sha256: str | None = None
    model_name: str | None = None

    # db and crud objects must be provided
    db: Session
    crud: CRUDBaseAIModel

    # optional objects, must be provided if minio is used
    s3: Minio | None = None
    prioritize_internet_download: bool = True

    # internal objects, not to be used by external callers
    db_object: BaseAIModel | None = None
    model: Any | None = None
    initialized: bool = False
    logger: Logger | None = None

    # pydantic validator to ensure that one of sha256 or model_name is provided
    @validator("model_name", pre=True, always=True)
    def either_sha256_or_model_name(cls, v, values):
        if v is None and values["sha256"] is None:
            raise ValueError("Either 'sha256' or 'model_name' must be provided.")
        return v

    @validator("logger", pre=True, always=True)
    def set_logger(cls, v):
        return v or LogConfig(cls.__name__).build_logger()

    def initialize(self):
        """
        Initialize the service object by downloading the model from Minio and/or the internet, and caching it locally.
        """

        if self.sha256 is not None:
            self.db_object = self.get_obj_by_sha256()
            
            #validate that model name on db_object matches self.model_name if self.model_name is not None
            if self.model_name is not None and self.db_object.model_name != self.model_name:
                raise ValueError(f"Model name {self.model_name} does not match model name {self.db_object.model_name} on DB object")
            
        elif self.model_name is not None:
            self.db_object = self.get_obj_by_model_name()

        if self.db_object is None:
            raise ValueError("SHA256 or model name not found in the database.")

        # TODO: verify
        model_cache_path = os.path.join(MODEL_CACHE_BASEDIR, self.db_object.model_name)

        # try to load the model from the cache & close out if successful
        if os.path.isdir(model_cache_path):
            try:
                self.load_model_from_cache(model_cache_path)
                self.initialized = True
                return
            except:
                pass

        # Create the directory if it doesn't exist
        Path(model_cache_path).mkdir(parents=True, exist_ok=True)

        model_hash = self.download_model(model_cache_path)

        # if self.sha256 is not None, validate that the hash matches
        if self.sha256 is None:
            self.sha256 = model_hash
        elif self.sha256 != model_hash:
            raise ValueError(f"SHA256 hash {self.sha256} does not match downloaded model hash {model_hash}")
            
        self.load_model_from_cache(model_cache_path)
        self.initialized = True

    def download_model(self, model_cache_path: str):
        """
        Download the model from the internet or Minio and cache it locally.
        Prioritizes Minio if prioritize_internet_download is False, but 
        will try both ways.
        """

        try: 
            if self.prioritize_internet_download:
                # try internet download first
                try:
                    self.download_model_internet(model_cache_path)
                except:
                    # if that fails, try Minio
                    self.download_model_minio(model_cache_path)
            else:
                # try Minio first
                try:
                    self.download_model_minio(model_cache_path)
                except:
                    # if that fails, try internet
                    self.download_model_internet(model_cache_path)
        except:
            raise ValueError("Could not download model from internet or Minio.")

    def download_model_minio(self, model_cache_path: str):
        """
        Download the model from Minio and cache it locally.
        Do not override this method.
        """

        # throw error if s3 is None
        if self.s3 is None:
            raise ValueError("Minio client is not set.")

        # download the model folder from minio
        self.logger.info(f"Downloading model from Minio to {model_cache_path}")
        download_folder_from_minio(s3=self.s3, dir_name=model_cache_path)
        self.logger.info(f"Downloaded model from Minio to {model_cache_path}")

    
    def load_model_from_cache(self, model_cache_path: str):
        """
        Load the model from the cache into self.model.
        Overriden by child classes as needed.
        """

        self.model = "replace me"

    def get_obj_by_sha256(self):
        """
        Get the DB object by SHA256.
        Overriden by child classes as needed.
        """

        return self.crud.get_by_sha256(self.db, sha256=self.sha256)
    
    def get_obj_by_model_name(self):
        """
        Get the DB object by model_name.
        Overriden by child classes as needed.
        """

        return self.crud.get_by_model_name(self.db, model_name=self.model_name)
    
    def download_model_internet(self, model_cache_path: str):
        """
        Download the model from the internet and cache it locally.
        Returns the SHA256 hash of the downloaded model.
        Overriden by child classes as needed.
        """

        return "12345"


# TODO: add upsert / training service that keeps minio and DB in line
## if model name and using FT model, pull latest version if minio
# save base models in minio as default_bucket/model_name/<any files>
# 