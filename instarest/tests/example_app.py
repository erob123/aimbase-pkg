# Make sure to set ENVIRONMENT, ENV_VAR_FOLDER, and SECRETS in your environment,
# outside of any .env file.  This is to ensure that the correct environment
# variables are loaded before the app is initialized.
# Default values are: ENVIRONMENT=local, ENV_VAR_FOLDER=./env_vars, SECRETS=False if not set here
import os
os.environ["ENVIRONMENT"] = "local"
os.environ["ENV_VAR_FOLDER"] = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), "env_vars")
os.environ["SECRETS"] = "false"

from instarest import (
    AppBase,
    DeclarativeBase,
    RESTRouter,
    SchemaBase,
    CRUDBase,
    Initializer,
)

from sqlalchemy import Column, String, Boolean

class EmptyTestModel(DeclarativeBase):
    bool_field = Column(Boolean(), default=False)
    title = Column(String(), default="title")

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
test_router = RESTRouter(
    schema_base=crud_schemas,
    crud_base=crud_test,
    prefix="/test",
    allow_delete=True,
)

# setup base up from routers
app_base = AppBase(crud_routers=[test_router], app_name="Test App API")

# automagic and version app
auto_app = app_base.get_autowired_app()

#core underlying app
app = app_base.get_core_app()
