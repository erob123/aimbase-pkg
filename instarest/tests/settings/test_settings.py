import os
from unittest import mock
from instarest.src.core.config import (
    EnvironmentSettings,
    CoreSettings,
    get_core_settings,
    set_core_settings,
    get_environment_settings,
    get_env_file,
)
from instarest.tests.example_app import (
    environment_settings as example_environment_settings,
)

BASEDIR = os.path.join(
    os.path.abspath(os.path.dirname("./instarest/core/config.py")), "env_var"
)


def test_settings_exists():
    # use the same settings as example app to avoid invalidating other tests
    set_core_settings(example_environment_settings)
    assert isinstance(get_core_settings(), CoreSettings)
    assert isinstance(get_environment_settings(), EnvironmentSettings)


@mock.patch.dict(
    os.environ, clear=True
)  # clear=True is needed to clear the environment variables
def test_environment_test_default():
    environment_settings = EnvironmentSettings()
    assert environment_settings.environment == "test"


@mock.patch.dict(os.environ, {"ENVIRONMENT": "test"})
def test_env_file_name_test():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == os.path.join(BASEDIR, "test.env")


@mock.patch.dict(os.environ, {"ENVIRONMENT": "local"})
def test_env_file_name_local():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == (
        os.path.join(BASEDIR, "local.env"),
        os.path.join(BASEDIR, "secrets.env"),
    )


@mock.patch.dict(os.environ, {"ENVIRONMENT": "development"})
def test_env_file_name_development():
    environment_settings = EnvironmentSettings()
    env_file = get_env_file(environment_settings)
    assert env_file == (
        os.path.join(BASEDIR, "development.env"),
        os.path.join(BASEDIR, "secrets.env"),
    )


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
