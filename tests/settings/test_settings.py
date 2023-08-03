import os
from unittest import mock
from instarest.core.config import EnvironmentSettings, CoreSettings, settings, get_env_file

BASEDIR = os.path.join(os.path.abspath(os.path.dirname("./instarest/core/config.py")), "env_var")

def test_settings_exists():
    assert isinstance(settings, CoreSettings)

@mock.patch.dict(os.environ, clear=True) # clear=True is needed to clear the environment variables
def test_environment_test_default():
    environment_settings = EnvironmentSettings()
    assert environment_settings.environment == 'test'

@mock.patch.dict(os.environ, {"ENVIRONMENT": "test"})
def test_env_file_name_test():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == os.path.join(BASEDIR, "test.env")

@mock.patch.dict(os.environ, {"ENVIRONMENT": "local"})
def test_env_file_name_local():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == (os.path.join(BASEDIR, "local.env"), os.path.join(BASEDIR, "secrets.env"))


@mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
def test_env_file_name_development():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == (os.path.join(BASEDIR, "development.env"), os.path.join(BASEDIR, "secrets.env"))

@mock.patch.dict(os.environ, {"ENVIRONMENT": "staging"})
def test_env_file_name_staging():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == os.path.join(BASEDIR, "staging.env")

@mock.patch.dict(os.environ, {"ENVIRONMENT": "production"})
def test_env_file_name_production():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == os.path.join(BASEDIR, "production.env")
