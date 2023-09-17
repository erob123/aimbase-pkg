import os
from fastapi import Depends, APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from instarest import get_db, RouterBase
from sqlalchemy.orm import Session
from .retrieval_service import RetrievalService


class QueryRetrievalRouterBase(RouterBase):
    """
    FastAPI Router object wrapper to perform query retrieval.
    Uses pydantic BaseModel for validation.

    **Parameters**
    See RouterBase for additional parameters.

    * `retrieval_service`: RetrievalService object to use for query retrieval.
    """

    # specific to this router
    retrieval_service: RetrievalService

    def _initialize_router(self):
        self.router = APIRouter(prefix=self.prefix, tags=[self.description])

    def _add_endpoints(self):
        @self.router.get(
            "/",
            response_class=HTMLResponse,
            summary="Query retrieval endpoint",
            response_description="Answered query with sources",
        )
        async def query_retrieval_get(
            query: str, db: Session = Depends(get_db)
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
