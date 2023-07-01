from app.db import base
from app.aimodels.bertopic import schemas

##########

import inspect as ins
from pydantic import UUID4
from typing import TYPE_CHECKING, Any, Optional, Generator
from sqlalchemy import (
    Boolean,
    DateTime,
    UUID,
    String,
    Enum,
    inspect,
)
from ..models.base import EntityModel


def _remove_endstr(str: str, sub: str) -> str:
    if str.endswith(sub):
        return str[: -len(sub)]
    return str


def gen_column_attrs(
    ModelType: EntityModel,
) -> Generator[tuple[str, tuple[type | Any, ...]], None, None]:
    """
    Generator for pulling attributes and types from the declared model.
    Includes foreign keys if actually saved in the table, but does not
    include attributes back-populated via relationships.

    **Parameters**

    * `ModelType`: A SQLAlchemy model class

    **Yields**
    * (field_name, (field_type, ...)) where field name is the name of the
    field (string) for this column, and field_type is the class
    of the type as it would be expected to be used in a
    pydantic schema
    """
    mapper = inspect(ModelType)

    for column in mapper.column_attrs:
        # name of the attribute, will be returned
        field_name = column.key

        # pull the actual attribute from the class
        field = getattr(ModelType, field_name)

        # find the type for being returned
        field_type = Any
        if isinstance(field.expression.type, UUID):
            field_type = UUID4

        if isinstance(field.expression.type, Boolean):
            field_type = bool

        yield field_name, (field_type, ...)

def gen_optional_column_attrs(
    ModelType: EntityModel,
) -> Generator[tuple[str, tuple[type | Any | None, ...]], None, None]:
    """
    Generator that yields same values as gen_column_attrs, 
    except that every field_type is made optional (for use
    in base pydantic schemas)

    **Parameters**

    See gen_column_attrs

    **Yields**

    See gen_column_attrs
    """

    for field_name, (field_type, _ ) in gen_column_attrs(ModelType):
        yield field_name, (field_type | None, ...)

def gen_relationship_attrs(
    ModelType: EntityModel, schema_pkg: Optional[Any] = None
) -> Generator[tuple[str, tuple[type | Any, ...]], None, None]:
    """
    Generator for pulling attributes and types from the declared model.
    Includes foreign keys if actually saved in the table, but does not
    include attributes back-populated via relationships.

    **Parameters**

    * `ModelType`: A SQLAlchemy model class
    * `schema_pkg`: A package containing imported pydantic schemas

    **Yields**
    * (field_name, (field_type, ...)) where field name is the name of the
    field (string) associated with this relationship, and field_type is
    either the schema class if found (requires schema package to be set) or Any
    """
    mapper = inspect(ModelType)

    for relationship in mapper.relationships:
        # name of the attribute, will be returned
        field_name = relationship.key

        # pull the actual attribute from the class
        field = getattr(ModelType, field_name)

        # get the name of the tables for the other end of this relationship
        table_name = ""
        if field.expression.left.description == "id":
            table_name = field.expression.left.table.description
        elif field.expression.right.description == "id":
            table_name = field.expression.right.table.description

        # try to map other table name to a known schema if schema package is defined
        field_type = Any
        if schema_pkg:
            for _, cls in ins.getmembers(schema_pkg):
                if ins.isclass(cls) and cls.__name__.lower() == _remove_endstr(
                    table_name, "model"
                ):
                    field_type = cls

        yield field_name, (field_type, ...)


for field_name, field_type in gen_column_attrs(EntityModel):
    print(field_name, field_type)


for field_name, field_type in gen_relationship_attrs(EntityModel, schemas):
    print(field_name, field_type)
