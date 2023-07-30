import os
import enum
from typing import Optional, Any
from pydantic import BaseSettings, PostgresDsn, validator

# load the environment name, local, test, staging, or production
class EnvironmentSettings(BaseSettings):
    environment: str = "test"

# object to get other env vars
class Settings(BaseSettings):
    # general settings
    docs_ui_root_path: str = ""
    log_level: str = "INFO"

    # postgreSQL settings
    postgres_user: str = ""
    postgres_password: str
    postgres_server: str = "db"
    postgres_port: str = "5432"
    postgres_db: str
    sqlalchemy_database_uri: Optional[PostgresDsn] = None

    @validator("sqlalchemy_database_uri", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        # pylint: disable=no-self-argument

        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_server"),
            port=values.get("postgres_port"),
            path=f"/{values.get('postgres_db') or ''}",
        )

def get_env_file(environment_settings_in):
    # get the base directory
    BASEDIR = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), "env_var")

    # final output, settings object, is built
    env_file = ""

    if environment_settings_in.environment == 'production':
        env_file = os.path.join(BASEDIR, "production.env")
    elif environment_settings_in.environment == 'staging':
        env_file = os.path.join(BASEDIR, "staging.env")
    elif environment_settings_in.environment == 'local':
        # put local secrets into secrets.env and ensure on .gitignore, K8s injects staging and prod into env vars
        env_file = (os.path.join(BASEDIR, "local.env"),
                    os.path.join(BASEDIR, "secrets.env"))
    elif environment_settings_in.environment == 'development':
        env_file = (os.path.join(BASEDIR, "development.env"),
                    os.path.join(BASEDIR, "secrets.env"))
    else:
        env_file = os.path.join(BASEDIR, "test.env")

    return env_file

environment_settings = EnvironmentSettings()
settings = Settings(_env_file=get_env_file(
    environment_settings), _env_file_encoding='utf-8')