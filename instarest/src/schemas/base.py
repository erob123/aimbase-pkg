from pydantic import create_model, BaseModel
from pydantic.main import ModelMetaclass
from typing import Generic, TypeVar
from instarest.src.db.base_class import DeclarativeBase
from instarest.src.utils.models import (
    dict_column_attrs_with_id,
    dict_optional_column_attrs_no_id,
    dict_relationship_attrs,
    remove_endstr,
)

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class SchemaBase(Generic[ModelType]):
    def __init__(
        self,
        model: type[ModelType] = DeclarativeBase,
        include_relationship_schemas: list[BaseModel | ModelMetaclass] = []
    ):
        """
        Wrapper class for pydantic schemas needed to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class that inherits from DeclarativeBase.  Defaults to DeclarativeBase.
        * `include_relationship_schemas`: list of pydantic schemas that should be included in the 
        http response whose underlying SQLAlchemy models have a relationship.  Defaults to empty.
        """

        assert issubclass(model, DeclarativeBase)

        # DO NOT REORDER
        self.model = model
        self.include_relationship_schemas = include_relationship_schemas
        self.EntityBase = self._build_entity_base()
        self.EntityCreate = self._build_entity_create()
        self.EntityUpdate = self._build_entity_update()
        self.EntityInDBBase = self._build_entity_in_db_base()
        self.Entity = self._build_entity()
        self.EntityInDB = self._build_entity_in_db()
        # DO NOT REORDER

    def get_model_type(self):
        return self.model
    
    def get_schema_prefix(self):
        return remove_endstr(self.model.__name__, "Model")

    # shared properties
    def _build_entity_base(self):
        return create_model(f"{self.get_schema_prefix()}Base", **dict_optional_column_attrs_no_id(self.model))

    # Properties to receive on Entity creation
    def _build_entity_create(self):
        return create_model(f"{self.get_schema_prefix()}Create", __base__=self.EntityBase)

    # Properties to receive on BertopicEmbeddingPretrained update
    def _build_entity_update(self):
        return create_model(f"{self.get_schema_prefix()}Update", __base__=self.EntityBase)

    # Properties shared by models stored in DB
    def _build_entity_in_db_base(self):

        # separate __base__ and __config__ because pydantic
        # enforces only one at a time for clarity
        db_base_schema = create_model(
            f"{self.get_schema_prefix()}InDBBase",
            __base__=self.EntityBase,
            **dict_column_attrs_with_id(self.model)
        )

        class EntityInDBBase(db_base_schema):
            class Config(db_base_schema.Config):
                orm_mode = True

        return EntityInDBBase

    # Properties to return to client
    def _build_entity(self):
        return create_model(
            f"{self.get_schema_prefix()}",
            __base__=self.EntityInDBBase,
            **dict_relationship_attrs(self.model, self.include_relationship_schemas)
        )

    # Properties properties stored in DB
    def _build_entity_in_db(self):
        return create_model(f"{self.get_schema_prefix()}InDB", __base__=self.EntityInDBBase)


# test = SchemaBase()
# print(test.get_model_type())
# print(test.get_model_type().__name__)
