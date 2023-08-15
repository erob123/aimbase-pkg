import os
from aimbase.src.crud.base import CRUDBaseAIModel
from aimbase.src.db.base import BaseAIModel
from aimbase.src.initializer import AimbaseInitializer
from aimbase.src.routers.sentence_transformer_router import SentenceTransformersRouter
from instarest import (
    AppBase,
    DeclarativeBase,
    SchemaBase,
    Initializer,
)
from aimbase.src.core import config as aimbase_config

# tell the app where to find the environment variables
ENV_VAR_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "env_vars")

aimbase_environment_settings = aimbase_config.AimbaseEnvironmentSettings(
    environment="local", env_var_folder=ENV_VAR_FOLDER
)
aimbase_config.set_aimbase_settings(aimbase_environment_settings)

Initializer(DeclarativeBase).execute()
AimbaseInitializer().execute()

# built pydantic data transfer schemas automagically
crud_schemas = SchemaBase(BaseAIModel)

# build db service automagically
crud_test = CRUDBaseAIModel(BaseAIModel)

# build ai router automagically
test_router = SentenceTransformersRouter(
    model_name="all-MiniLM-L6-v2",
    schema_base=crud_schemas,
    crud_base=crud_test,
    prefix="/sentences",
    allow_delete=True,
)

# setup base up from routers
app_base = AppBase(crud_routers=[test_router], app_name="Aimbase Inference Test App API")

# automagic and version app
auto_app = app_base.get_autowired_app()

# core underlying app
app = app_base.get_core_app()
