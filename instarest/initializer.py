import logging
from instarest.db.base_class import DeclarativeBase
from instarest.db.init_db import init_db, wipe_db
from instarest.db.session import SessionLocal
from instarest.core.config import environment_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Initializer:
    def __init__(self, Base: DeclarativeBase):
        self.Base = Base

    def execute(self, migration_toggle = False) -> None:

        # environment can be one of 'local', 'test', 'staging', 'production'
        environment = environment_settings.environment

        logger.info(f"Using initialization environment: {environment}")
        logger.info(f"Using migration toggle: {migration_toggle}")

        # clear DB if local or staging as long as not actively testing migrating
        if (environment in ['local', 'staging'] and migration_toggle is False):
            logger.info("Clearing database")
            wipe_db(self.Base)
            logger.info("Database cleared")

        # all environments need to initialize the database
        # prod only if migration toggle is on
        if (environment in ['local', 'development', 'test', 'staging'] or (environment == 'production' and migration_toggle is True)):
            logger.info("Creating database schema and tables")
            db = SessionLocal()
            init_db(self.Base)
            logger.info("Initial database schema and tables created.")
        else:
            logger.info("Skipping database initialization")
