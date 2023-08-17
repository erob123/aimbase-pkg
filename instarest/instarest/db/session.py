from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from instarest.core.config import get_core_settings

engine = create_engine(get_core_settings().sqlalchemy_database_uri, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
