# this is a basic model file for "Test" entity
from sqlalchemy import Column, UUID, Boolean, String
from instarest.db.base_class import DeclarativeBase
import uuid

class EmptyTestModel(DeclarativeBase):
    id = Column(UUID, primary_key=True, unique=True, default=uuid.uuid4)
    bool_field = Column(Boolean(), default=False)
    title = Column(String(), default="title")
