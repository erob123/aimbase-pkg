from typing import Any
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.llms.base import BaseLLM
from .retrieval_service import RetrievalService
from aimbase.core import config as aimbase_config


class OpenAIRetrieveSummarizeService(RetrievalService):
    """
    OpenAI Retrieve Summarize Service
    Retrieve documents relevant to a query and summarize them.

    To use, you should have the ``openai`` python package installed, and the
    environment variable ``OPENAI_API_KEY`` set with your API key.
    """

    llm: BaseLLM | None = None

    def __init__(self, **kwargs: Any):
        """Initialize the pydantic object and llm."""
        super().__init__(**kwargs)

        self.llm = OpenAI(
            temperature=0.8,
            openai_api_key=aimbase_config.get_aimbase_settings().openai_api_key,
        )

    def _get_documents(self, query=None, retriever=None):
        # TODO: address FAISS chunking and add metadata
        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            input_key="input",
            return_source_documents=True,
            verbose=True,
        )

        result = chain({"input": f"{query}"})
        return result
