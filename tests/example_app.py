from instarest import (
    AppBase,
    DeclarativeBase,
    RouterBase,
    SchemaBase,
    CRUDBase,
    config,
    logging,
    Initializer,
)

from sqlalchemy import Column, String, Boolean

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
sentence_router = RouterBase(
    schema_base=crud_schemas,
    crud_base=crud_test,
    prefix="/test",
    allow_delete=True,
)

# setup base up from routers
app_base = AppBase(crud_routers=[sentence_router], app_name="Test App API")

# automagic and version app
auto_app = app_base.get_autowired_app()

#core underlying app
app = app_base.get_core_app()
