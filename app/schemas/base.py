from pydantic import BaseConfig, create_model
from typing import Any, Generic, TypeVar
from ..db.base_class import Base
from ..utils.models import (
    gen_column_attrs,
    gen_optional_column_attrs,
    gen_relationship_attrs,
)

ModelType = TypeVar("ModelType", bound=Base)
SchemaPkg = TypeVar("SchemaPkg", bound=Any)

class SchemaBase(Generic[ModelType, SchemaPkg]):
    # includes relationships by default, override in subclass if desired
    include_relationships_in_dto = True

    @staticmethod
    def relationships_packed(
        include_relationships: bool, schema_pkg: Any | None = None
    ):
        output = {}
        if include_relationships:
            output = gen_relationship_attrs(ModelType, SchemaPkg)

        return output

    # shared properties
    EntityBase = create_model("EntityBase", **gen_optional_column_attrs(ModelType))

    # Properties to receive on Entity creation
    EntityCreate = create_model("EntityCreate", __base__=EntityBase)

    # Properties to receive on BertopicEmbeddingPretrained update
    EntityUpdate = create_model("EntityUpdate", __base__=EntityBase)

    # Properties shared by models stored in DB
    EntityInDBBase = create_model(
        "EntityInDBBase",
        __config__=BaseConfig(orm_mode=True),
        __base__=EntityBase,
        **gen_column_attrs(ModelType)
    )

    # Properties to return to client
    Entity = create_model(
        "Entity",
        __base__=EntityInDBBase,
        **relationships_packed(include_relationships_in_dto)
    )

    # Properties properties stored in DB
    EntityInDB = create_model("EntityInDB", __base__=EntityInDBBase)
