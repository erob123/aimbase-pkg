from fastapi import Depends, HTTPException
from pydantic import BaseModel
from aimbase.crud.base import CRUDBaseAIModel
from aimbase.services.sentence_transformer_inference import SentenceTransformerInferenceService
from aimbase.dependencies import get_minio
from instarest import RouterBase
from instarest import SchemaBase
from instarest import get_db
from sqlalchemy.orm import Session
from minio import Minio
from typing import TypeVar

SchemaBaseType = TypeVar("SchemaBaseType", bound=SchemaBase)
CRUDBaseAIModelType = TypeVar("CRUDBaseAIModelType", bound=CRUDBaseAIModel)

class SentenceTransformersRouter(RouterBase[SchemaBaseType, CRUDBaseAIModelType]):
    def __init__(
        self,
        model_name: str,
        schema_base: type[SchemaBaseType],
        crud_base: type[CRUDBaseAIModelType],
        prefix: str = "/",
        allow_delete: bool = False,
    ):
        """
        Router object for Sentence Transformers model, inheriting from instarest.RouterBase.  

        **Parameters**

        Same as instarest.RouterBase, with the addition of:

        * `sentence_transformer_inference_service`: SentenceTransformerInferenceService object, which contains the Sentence Transformers model and inference methods
        """

        super().__init__(schema_base, crud_base, prefix, allow_delete)
        self.model_name = model_name
        self._define_encode()

    def _define_encode(self):

        def build_model_not_initialized_error():
            return HTTPException(
                status_code=500,
                detail=f"{self.model_name} is not initialized",
            )
        
        class Embeddings(BaseModel):
            embeddings: list[list[float]] = []
        
        class Documents(BaseModel):
            documents: list[str] = []

        # ENCODE
        @self.router.post(
            "/encode",
            response_model=Embeddings,
            responses=type(self).responses,
            summary=f"Calculate embeddings for sentences or documents",
            response_description=f"Calculated embeddings",
        )
        async def encode(
            documents: Documents,
            db: Session = Depends(get_db),
            s3: Minio | None = Depends(get_minio),
        ) -> Embeddings:
            
            try:
                service = self._build_sentence_transformer_inference_service(db, s3)
            except Exception as e:
                raise build_model_not_initialized_error()

            embeddings = service.model.encode(documents.documents)
            
            return Embeddings(embeddings=embeddings)
        
    def _build_sentence_transformer_inference_service(self, db: Session, s3: Minio | None = None):
        service = SentenceTransformerInferenceService(
            model_name=self.model_name,
            db=db,
            crud=self.crud_base,
            s3=s3,
            prioritize_internet_download=False,
        )

        service.initialize()
        return service