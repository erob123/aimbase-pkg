import shutil
import traceback
from typing import Any
from aimbase.core.minio import calculate_folder_hash
from aimbase.services.base import BaseAIInferenceService

# TODO: pull tracebacks out of all except blocks and handle at app level
class SentenceTransformerInferenceService(BaseAIInferenceService):
    # all-MiniLM-L6-v2
    # internal only
    sentence_transformer_class: Any | None = None

    def dev_init(self):
        """
        Initialize the service object for development purposes.
        """

        # init imports and download model from internet
        self.initialize()
        

        # upload model to minio
        self.upload_model_to_minio()

        # delete the model from the cache and all files within directory
        shutil.rmtree(self.get_model_cache_path())

    def initialize(self):
        try:
            from sentence_transformers import SentenceTransformer

            self.sentence_transformer_class = SentenceTransformer
        except ImportError:
            msg = (
                "Could not import sentence_transformers python package. "
                "Please install it with `pip install sentence-transformers`"
            )

            self.logger.error(msg)
            traceback.print_exc()
            raise ImportError(msg)

        super().initialize()

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
            msg = (
                "Model not found in cache."
            )
            self.logger.error(msg)
            traceback.print_exc()

            raise Exception(msg)

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
