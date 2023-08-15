import shutil
from typing import Any
from aimbase.src.core.minio import calculate_folder_hash
from aimbase.src.services.base import BaseAIInferenceService


class SentenceTransformerInferenceService(BaseAIInferenceService):
    # all-MiniLM-L6-v2
    # internal only
    sentence_transformer_class: Any | None = None

    def dev_init(self):
        """
        Initialize the service object for development purposes.
        """

        self.download_model_internet()

        # upload model to minio
        self.upload_model_to_minio()

        # delete the model from the cache and all files within directory
        shutil.rmtree(self.get_model_cache_path())

    def initialize(self):
        super().initialize()

        self.initialized = False
        try:
            from sentence_transformers import SentenceTransformer

            self.sentence_transformer_class = SentenceTransformer
            self.initialized = True
        except ImportError:
            raise ImportError(
                "Could not import sentence_transformers python package. "
                "Please install it with `pip install sentence-transformers` "
            )

    def load_model_from_cache(self):
        """
        Load the model from the cache into self.model.
        Overriden by child classes as needed.
        """

        try:
            # load model from cache, note that this will try to download from internet if connection
            # exists and model is not in cache
            self.model = self.sentence_transformer_class(
                model_name_or_path=self.model_name,
                cache_folder=self.get_model_cache_path(),
            )
        except:
            raise Exception("Model not found in cache.")

    def download_model_internet(self):
        """
        Download the model from the internet and cache it locally.
        Returns the SHA256 hash of the downloaded model.
        Overriden by child classes as needed.
        """

        # download model to cache
        self.sentence_transformer_class(
            model_name_or_path=self.model_name, cache_folder=self.get_model_cache_path()
        )

        # calculate sha256 hash of model folder
        return calculate_folder_hash(self.get_model_cache_path())
