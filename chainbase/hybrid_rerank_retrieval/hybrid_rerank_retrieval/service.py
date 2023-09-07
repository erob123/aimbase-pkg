import re
from typing import Any
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from pydantic import BaseModel, validator
from aimbase.services import (
    SentenceTransformerInferenceService,
    CrossEncoderInferenceService,
)

from .marco_rerank_retriever import MarcoRerankRetriever
from .stis_embeddings import STISEmbeddings

# from app.core.errors import ValidationError
# from app.core.minio import download_pickled_object_from_minio
# from app.core.model_cache import MODEL_CACHE_BASEDIR

from sqlalchemy.orm import Session
from minio import Minio

# from app.aimodels.bertopic.crud import bertopic_embedding_pretrained

# from sample_data import CHAT_DATASET_1_PATH


class RetrievalService(BaseModel):
    # must be provided and initialized (see validators)
    sentence_inference_service: SentenceTransformerInferenceService
    cross_encoder_inference_service: CrossEncoderInferenceService

    # optional
    db: Session | None = None
    s3: Minio | None = None

    @validator("sentence_inference_service", pre=True, always=True)
    def model_must_be_initialized(
        cls, v: SentenceTransformerInferenceService
    ) -> SentenceTransformerInferenceService:
        if not v.initialized:
            raise ValueError(
                "sentence_inference_service not initialized.  Please call initialize() on the SentenceTransformerInferenceService first."
            )
        return v

    @validator("cross_encoder_inference_service", pre=True, always=True)
    def model_must_be_initialized(
        cls, v: CrossEncoderInferenceService
    ) -> CrossEncoderInferenceService:
        if not v.initialized:
            raise ValueError(
                "cross_encoder_inference_service not initialized.  Please call initialize() on the CrossEncoderInferenceService first."
            )
        return v

    class Config:
        arbitrary_types_allowed = True

    def retrieve(self, query: str, summarize=False):
        if not (isinstance(query, str) and isinstance(summarize, bool)):
            raise ValueError("must input query as str and summarize as bool")

        # TODO: how to build dataset, version control or DB?
        retriever = self._build_retriever(channel_names=[CHAT_DATASET_1_PATH])

        if summarize:
            pass
            # llm = self.completion_inference._build_llm(query)
            # results = self._retrieve_and_summarize(
            #     llm,
            #     query=query,
            #     retriever=retriever,
            # )
        else:
            results = self._retrieve_only(
                query=query,
                retriever=retriever,
            )

        return results

    def _build_retriever(
        self,
        channel_names=[],
    ):
        local_embeddings = STISEmbeddings(
            sentence_inference_service=self.sentence_inference_service
        )

        path = channel_names[0]






        # get DocumentModel objects from the database
        document_models = document_crud.get_by_created_date_range(
            db=self.db, start_date=None, end_date=None
        )

        # convert DocumentModel objects to Document objects
        documents = []
        for doc_model in document_models:
            source_link = (
                ""
                if not doc_model.mattermost_document
                or len(doc_model.mattermost_document) == 0
                else f"{settings.mm_aoc_base_url}/pl/{doc_model.mattermost_document[0].message_id}"
            )

            document = Document(
                page_content=doc_model.text,
                metadata={
                    "originated_from": doc_model.originated_from,
                    "original_created_time": doc_model.original_created_time,
                    "link": source_link,
                },
            )

            documents.append(document)






        chat_texts = CSVLoader(path).load()
        chat_retriever = FAISS.from_documents(
            chat_texts, local_embeddings
        ).as_retriever()
        chat_retriever.search_kwargs = {"k": 25}

        def bm25_preprocess_func(text):
            # replace non alphanumeric characters with whitespace
            text = re.sub(r"[^a-zA-Z0-9]", " ", text)

            # lowercase and split on whitespace
            return text.lower().split()

        # initialize the bm25 retriever
        bm25_retriever = BM25Retriever.from_documents(
            chat_texts, preprocess_func=bm25_preprocess_func
        )
        bm25_retriever.k = 25

        # initialize the ensemble retriever
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, chat_retriever], weights=[0.5, 0.5]
        )

        rerank_retriever = MarcoRerankRetriever(
            base_retriever=ensemble_retriever,
            rerank_model_name_or_path="cross-encoder/ms-marco-TinyBERT-L-6",
            max_relevant_documents=10,
        )

        return rerank_retriever

    def _retrieve_only(self, query=None, retriever=None):
        result = {"input": query, "result": "No LLM used to summarize"}
        result["source_documents"] = retriever.get_relevant_documents(query)
        return result

    # def _retrieve_and_summarize(self, llm, query=None, retriever=None):
    #     ###Unknown: how to address FAISS chunking and add metadata
    #     chain = RetrievalQA.from_chain_type(
    #         llm=llm,
    #         chain_type="stuff",
    #         retriever=retriever,
    #         input_key="input",
    #         return_source_documents=True,
    #         verbose=True,
    #     )

    #     result = chain({"input": f"{query}"})
    #     return result
