from sqlalchemy import Column, DateTime, UUID, String
from uuid import uuid4
from instarest import DeclarativeBase

class DocumentModel(DeclarativeBase):
    id = Column(UUID, primary_key=True, unique=True, default=uuid4)
    original_created_time = Column(DateTime(timezone=True)) # see sqlalchemy datetime info here: https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    text = Column(String)
    source = Column(String) # intentionally flexible, could be a url, a file path, title, page, etc. 

    #TODO: save a list of embeddings based on underlying model for later use
    # embedding_computations = relationship("DocumentEmbeddingComputationModel", back_populates="document")