import os
from typing import Any, Generic, TypeVar
from pydantic import BaseSettings, PostgresDsn, validator

environment_settings = None # :meta private:
settings = None # :meta private:

# object to get other env vars
class CoreSettings(BaseSettings):
    # general settings
    docs_ui_root_path: str = ""
    log_level: str = "INFO"

    # postgreSQL settings
    postgres_user: str
    postgres_password: str
    postgres_server: str
    postgres_port: str
    postgres_db: str
    sqlalchemy_database_uri: PostgresDsn | None = None

    @validator("sqlalchemy_database_uri", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
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


CoreSettingsType = TypeVar("CoreSettingsType", bound=CoreSettings)

# load the environment name, local, test, staging, or production
class EnvironmentSettings(BaseSettings, Generic[CoreSettingsType]):
    environment: str
    """
    Environment name, e.g., "local", "test", "staging", "production".  Needs
    to match the name of the environment file in the env_vars folder.
    """

    secrets: bool = False
    """
    Whether to load secrets from the secrets.env file.  This is only used for
    local and development environments.
    """

    env_var_folder: str = "./env_vars"
    """
    Folder where environment files are stored.
    """

    settings_type: CoreSettingsType = CoreSettings
    """
    Type of settings object to return.
    """

    class Config:
        arbitrary_types_allowed = True


    def pull_settings(self) -> CoreSettingsType:
        """
        Pull settings from environment variables, and load them into the environment.
        """
        # load environment variables from file
        env_file = os.path.join(self.env_var_folder, f"{self.environment}.env")

        # if file doesnt exist, raise error
        if not os.path.exists(env_file):
            raise FileNotFoundError(
                f"Environment file {env_file} not found.  Please create it.")

        if self.secrets:
            secrets_file = os.path.join(
                self.env_var_folder, "secrets.env")
            
            if not os.path.exists(secrets_file):
                raise FileNotFoundError(
                    f"Secrets file {secrets_file} not found.  Please create it.")
            
            env_file = (env_file, secrets_file)

        return self.settings_type(_env_file=env_file, _env_file_encoding='utf-8')

def set_core_settings(new_environment_settings: EnvironmentSettings) -> None:
    """
    Set the environment settings and core settings objects.
    """
    global environment_settings, settings

    environment_settings = new_environment_settings
    settings = environment_settings.pull_settings()

def get_core_settings() -> CoreSettings:
    """
    Get the core settings object.
    """
    global settings

    if settings is None:
        raise ValueError("Settings not initialized.  Please call set_core_settings() first.")

    return settings

def get_environment_settings() -> EnvironmentSettings:
    """
    Get the environment settings object.
    """
    global environment_settings

    if environment_settings is None:
        raise ValueError("Settings not initialized.  Please call set_core_settings() first.")

    return environment_settings