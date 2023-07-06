from typing import TYPE_CHECKING
from sqlalchemy import (
    Column,
    Boolean,
    UUID,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from instarest.db.base_class import DeclarativeBase
import uuid


if TYPE_CHECKING:
    from instarest.aimodels.bertopic.models.bertopic_embedding_pretrained import (
        BertopicEmbeddingPretrainedModel,
    )  # noqa: F401

class EntityModel(DeclarativeBase):
    id = Column(UUID, primary_key=True, unique=True, default=uuid.uuid4)
    uploaded = Column(Boolean(), default=False)
    embedding_pretrained_id = Column(
        UUID, ForeignKey("bertopicembeddingpretrainedmodel.id")
    )
    embedding_pretrained = relationship(
        "BertopicEmbeddingPretrainedModel", back_populates="entity_model"
    )
