from datetime import datetime
from pydantic import BaseConfig, create_model, UUID4
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)




class SchemaBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        """
        Schema object with default data validation for the api.

        **Parameters**

        * `model`: A SQLAlchemy model class
        """
        self.model = model

    # shared properties
    EntityBase = create_model(
    'EntityBase', 
    foo=(str, ...), bar=(int, ...)
    )

    # Properties to receive on Entity creation
    EntityCreate = create_model('EntityCreate', __base__= EntityBase)

    # Properties to receive on BertopicEmbeddingPretrained update
    EntityUpdate = create_model('EntityUpdate', __base__= EntityBase)

    # Properties shared by models stored in DB
    EntityInDBBase = create_model(
    'EntityInDBBase',
    __config__= BaseConfig(orm_mode=True),
    __base__= EntityBase,
    foo=(str, ...), bar=(int, ...)
    )

    # Properties to return to client
    # includes relationships by default 
    Entity = create_model(
    'Entity',
    __base__= EntityInDBBase,
    foo=(str, ...), bar=(int, ...)
    )

    # Properties properties stored in DB
    EntityInDB = create_model('EntityInDB', __base__= EntityInDBBase)
