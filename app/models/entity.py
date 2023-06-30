from typing import TYPE_CHECKING
from sqlalchemy import (
    Column,
    Boolean,
    UUID,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base
import uuid


if TYPE_CHECKING:
    from app.aimodels.bertopic.models.bertopic_embedding_pretrained import (
        BertopicEmbeddingPretrainedModel,
    )  # noqa: F401

class EntityModel(Base):
    id = Column(UUID, primary_key=True, unique=True, default=uuid.uuid4)
    uploaded = Column(Boolean(), default=False)
    embedding_pretrained_id = Column(
        UUID, ForeignKey("bertopicembeddingpretrainedmodel.id")
    )
    embedding_pretrained = relationship(
        "BertopicEmbeddingPretrainedModel", back_populates="entity_model"
    )
