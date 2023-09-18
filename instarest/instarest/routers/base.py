from typing import Any
from abc import ABC, abstractmethod
from fastapi import APIRouter
from pydantic import BaseModel

class RouterBase(BaseModel, ABC):
    """
    FastAPI Router object wrapper.

    **Parameters**

    * `prefix`: Path prefix following same rules as fastapi.APIRouter (e.g., "/" or "/example"). Defaults to "/".
    * `description`: Description of the router. Defaults to None.
    """

    prefix: str = "/"
    description: str | None = None

    # internal to this class, do not set on init
    router: APIRouter | None = None # :meta private:

    # pydantic config
    class Config:
        arbitrary_types_allowed = True

    class ErrorMessage(BaseModel):
        detail: str = ""

    responses: dict = {
        "400": {"model": ErrorMessage, "description": "Bad or Improper Request"},
        "422": {"model": ErrorMessage, "description": "Unprocessable Entity"},
    }

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._initialize_router()
        self._add_endpoints()

    def get_router(self):
        return self.router

    @abstractmethod
    def _initialize_router(self):
        """Initialize the FastAPI router."""

    @abstractmethod
    def _add_endpoints(self):
        """Add endpoints to the FastAPI router."""
        