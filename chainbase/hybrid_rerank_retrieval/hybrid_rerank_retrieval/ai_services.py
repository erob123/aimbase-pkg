from aimbase import (
    SentenceTransformerInferenceService,
    CRUDBaseAIModel,
    BaseAIModel,
    get_minio,
)
from instarest import get_db

crud_base_ai = CRUDBaseAIModel(BaseAIModel)

marco_service = SentenceTransformerInferenceService(
    model_name="cross-encoder/ms-marco-TinyBERT-L-6",
    db=next(get_db()),
    crud=crud_base_ai,
    s3=get_minio(),
    prioritize_internet_download=False,
)

all_mini_service = SentenceTransformerInferenceService(
    model_name="all-MiniLM-L6-v2",
    db=next(get_db()),
    crud=crud_base_ai,
    s3=get_minio(),
    prioritize_internet_download=False,
)
