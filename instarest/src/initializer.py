from instarest.src.db.base_class import DeclarativeBase
from instarest.src.db.init_db import init_db, wipe_db
from instarest.src.db.session import SessionLocal
from instarest.src.core.config import get_environment_settings
from instarest.src.core.logging import LogConfig

class Initializer:
    def __init__(self, Base: DeclarativeBase):
        self.logger = LogConfig(self.__class__.__name__).build_logger()
        self.Base = Base

    def init_db(self):
        init_db(self.Base)

    def wipe_db(self):
        wipe_db(self.Base)

    def execute(self, migration_toggle = False) -> None:

        # environment can be one of 'local', 'test', 'staging', 'production'
        environment = get_environment_settings().environment

        self.logger.info(f"Using initialization environment: {environment}")
        self.logger.info(f"Using migration toggle: {migration_toggle}")

        # clear DB if local or staging as long as not actively testing migrating
        if (environment in ['local', 'staging'] and migration_toggle is False):
            self.logger.info("Clearing database")
            self.wipe_db()
            self.logger.info("Database cleared")

        # all environments need to initialize the database
        # prod only if migration toggle is on
        if (environment in ['local', 'development', 'test', 'staging'] or (environment == 'production' and migration_toggle is True)):
            self.logger.info("Creating database schema and tables")
            db = SessionLocal()
            self.init_db()
            self.logger.info("Initial database schema and tables created.")
        else:
            self.logger.info("Skipping database initialization")
