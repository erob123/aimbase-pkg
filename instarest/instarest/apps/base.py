from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_versioning import VersionedFastAPI

from instarest.routers.base import RouterBase
from ..core.config import get_core_settings
from ..core.logging import LogConfig
from ..dependencies import httpx_client

class AppBase:
     
    def __init__(
        self,
        crud_routers: list[RouterBase],
        app_name: str = "API"
    ):
        """
        FastAPI App object to auto-launch the underlying crud packages.

        **Parameters**

        * `crud_routers`: list containing crud routers to launch in app
        """

        for router in crud_routers:
            assert isinstance(router, RouterBase)

        # DO NOT REORDER
        self.logger = LogConfig(LOGGER_NAME=self.__class__.__name__).build_logger()
        self.crud_routers = crud_routers
        self.app_name = app_name
        self.setup() # sets up self.core_app
        self.autowire() #autowires self.autowired_app

    def get_core_app(self):
        return self.core_app
    
    def get_autowired_app(self):
        return self.autowired_app

    def add_routers(self, routers: list):
        for router in routers:
            self.core_app.include_router(router)

        self.autowire()

    def setup(self):
        # initiate the app and tell it that there is a proxy prefix of /api that gets stripped
        # (only effects the loading of the swagger and redoc UIs)
        self.core_app = FastAPI(title=str(self.app_name), root_path=get_core_settings().docs_ui_root_path,
                    responses={404: {"description": "Not found"}})
        
        for router_base in self.crud_routers:
            self.core_app.include_router(router_base.get_router())

    def autowire(self):
        """
        Wires up and returns a versioned FastAPI app with loggger, CORS, httpx initialized
        """
        self.logger.info("Dummy Info")
        self.logger.error("Dummy Error")
        self.logger.debug("Dummy Debug")
        self.logger.warning("Dummy Warning")
        self.logger.info("UI Root: %s", get_core_settings().docs_ui_root_path)
        self.logger.info("log_level: %s", get_core_settings().log_level)
        self.logger.warning("Test filtering this_should_be_filtered_out")

        origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:8080",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3004",
        ]

        # setup for major versioning
        # ensure to copy over all the non-title args to the original FastAPI call...read docs here: https://pypi.org/project/fastapi-versioning/
        self.autowired_app = VersionedFastAPI(self.core_app,
                                        version_format='{major}',
                                        prefix_format='/v{major}', default_api_version=1, root_path=get_core_settings().docs_ui_root_path)

        # add middleware here since this is the app that deploys
        self.autowired_app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # close the httpx client when app is shutdown
        # see here: https://stackoverflow.com/questions/73721736/what-is-the-proper-way-to-make-downstream-https-requests-inside-of-uvicorn-fasta
        @self.autowired_app.on_event('shutdown')
        async def shutdown_event():
            await httpx_client.aclose()