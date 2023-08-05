import os
from instarest import (
    AppBase,
    DeclarativeBase,
    RouterBase,
    SchemaBase,
    CRUDBase,
    Initializer,
)
from aimbase.src.core import config as aimbase_config

from sqlalchemy import Column, String, Boolean

# tell the app where to find the environment variables
ENV_VAR_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "env_vars")

aimbase_environment_settings = aimbase_config.AimbaseEnvironmentSettings(
    environment="local", env_var_folder=ENV_VAR_FOLDER
)
aimbase_config.set_aimbase_settings(aimbase_environment_settings)


class EmptyTestModel(DeclarativeBase):
    bool_field = Column(Boolean(), default=False)
    title = Column(String(), default="title")


# class DocumentModel()

# Ensure all SQLAlchemy models are defined or imported before initializing
# Otherwise relationships in DB can be defined incorrectly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28
initializer = Initializer(DeclarativeBase)
initializer.execute()

# built pydantic data transfer schemas automagically
crud_schemas = SchemaBase(EmptyTestModel)

# build crud db service automagically
crud_test = CRUDBase(EmptyTestModel)

# build crud router automagically
test_router = RouterBase(
    schema_base=crud_schemas,
    crud_base=crud_test,
    prefix="/test",
    allow_delete=True,
)

# setup base up from routers
app_base = AppBase(crud_routers=[test_router], app_name="Test App API")

# automagic and version app
auto_app = app_base.get_autowired_app()

# core underlying app
app = app_base.get_core_app()
