from sqlalchemy import (
    Column,
    UUID
)

from sqlalchemy.orm import as_declarative, declared_attr
from uuid import uuid4

@as_declarative()
class DeclarativeBase:
    # all models have UUIDv4 IDs
    id = Column(UUID, primary_key=True, unique=True, default=uuid4)
    __name__: str
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        # pylint: disable=no-self-argument
        return cls.__name__.lower()
