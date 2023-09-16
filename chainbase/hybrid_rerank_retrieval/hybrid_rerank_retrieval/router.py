import os
from typing import Any
from fastapi import Depends, APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from instarest import get_db
from sqlalchemy.orm import Session
from .retrieval_service import RetrievalService


# TODO: turn into base router class
class QueryRetrievalRouterBase(BaseModel):
    """
    FastAPI Router object wrapper to perform query retrieval.

    **Parameters**

    * `prefix`: Path prefix following same rules as fastapi.APIRouter (e.g., "/" or "/example"). Defaults to "/".
    """

    prefix: str = "/" # /retrieval
    description: str | None = None  # "Document Query Retrieval"

    # internal to this class, do not set on init
    router: APIRouter | None = None # :meta private:

    # specific to this router
    retrieval_service: RetrievalService

    class ErrorMessage(BaseModel):
        detail: str = ""

    responses = {
        "400": {"model": ErrorMessage, "description": "Bad or Improper Request"},
        "422": {"model": ErrorMessage, "description": "Unprocessable Entity"},
    }

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._initialize_router()
        self._add_endpoints()

    def _initialize_router(self):
        self.router = APIRouter(
            prefix=self.prefix, tags=[self.description]
        )


    def _add_endpoints(self):
        # raise NotImplementedError(
        #     "Must implement _add_endpoints() in QueryRetrievalRouterBase subclass."
        # )
        @self.router.get(
            "/",
            response_class=HTMLResponse,
            summary="Query retrieval endpoint",
            response_description="Answered query with sources",
        )
        async def query_retrieval_get(
            query: str,
            db: Session = Depends(get_db)
        ) -> (HTMLResponse):
            """
            Query retrieval endpoint.
            """
        
            results = self.retrieval_service.retrieve(db, query)
            return self._render_result_as_html(results)


    # Function to render the result dictionary as HTML
    def _render_result_as_html(result):
        # Create a Jinja2 environment and load the template

        env = Environment(
            loader=FileSystemLoader(os.path.abspath(os.path.dirname(__file__))),
            autoescape=True,
        )

        template = env.get_template("template.html")

        # Render the template with the result dictionary
        html_content = template.render(result=result)
        return HTMLResponse(content=html_content)
