## ************ ENV VAR INIT BEFORE IMPORTS ************ ##
# Make sure to set ENVIRONMENT, ENV_VAR_FOLDER, and SECRETS in your environment,
# outside of any .env file.  This is to ensure that the correct environment
# variables are loaded before the app is initialized.
# Default values are: ENVIRONMENT=local, ENV_VAR_FOLDER=./env_vars, SECRETS=False if not set here
import os

os.environ["ENVIRONMENT"] = "local"
os.environ["ENV_VAR_FOLDER"] = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "env_vars"
)
os.environ["SECRETS"] = "False"
## ************ ENV VAR INIT BEFORE IMPORTS ************ ##

from aimbase.crud.base import CRUDBaseAIModel
from aimbase.db.base import BaseAIModel, FineTunedAIModel, FineTunedAIModelWithBaseModel
from aimbase.initializer import AimbaseInitializer
from aimbase.routers.sentence_transformer_router import SentenceTransformersRouter
from aimbase.dependencies import get_minio
from instarest import (
    AppBase,
    DeclarativeBase,
    SchemaBase,
    Initializer,
    get_db,
)

from aimbase.services.sentence_transformer_inference import (
    SentenceTransformerInferenceService,
)

# TODO: import to __init__.py for aimbase and update imports here
Initializer(DeclarativeBase).execute()
AimbaseInitializer().execute()

# built pydantic data transfer schemas automagically
crud_schemas = SchemaBase(BaseAIModel)

# build db service automagically
crud_test = CRUDBaseAIModel(BaseAIModel)

## ************ DEV INITIALIZATION ONLY (if desired to simulate
#  no internet connection...will auto init on first endpoint hit, but 
#  will not auto-upload to minio) ************ ##
SentenceTransformerInferenceService(
    model_name="all-MiniLM-L6-v2",
    db=next(get_db()),
    crud=crud_test,
    s3=get_minio(),
    prioritize_internet_download=False,
).dev_init()
## ************ DEV INITIALIZATION ONLY ************ ##

# build ai router automagically
test_router = SentenceTransformersRouter(
    model_name="all-MiniLM-L6-v2",
    schema_base=crud_schemas,
    crud_base=crud_test,
    prefix="/sentences",
    allow_delete=True,
)

# setup base up from routers
app_base = AppBase(
    crud_routers=[test_router], app_name="Aimbase Inference Test App API"
)

# automagic and version app
auto_app = app_base.get_autowired_app()

# core underlying app
app = app_base.get_core_app()
