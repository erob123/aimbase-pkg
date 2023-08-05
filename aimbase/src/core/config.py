from typing import TypeVar
from instarest.src.core.config import (
    CoreSettings,
    EnvironmentSettings,
    set_core_settings,
)

aimbase_environment_settings = None # :meta private:
aimbase_settings = None # :meta private:

class AimbaseSettings(CoreSettings):
    """
    Settings specific to this application.
    """
    aimbase_specific_setting: str = "aimbase_specific_setting"


AimbaseSettingsType = TypeVar("AimbaseSettingsType", bound=AimbaseSettings)

# make it possible to load AimbaseSettings from environment variables and to inherit from 
# AimbaseEnvironmentSettings with generic settings type
class AimbaseEnvironmentSettings(EnvironmentSettings[AimbaseSettingsType]):
    
    settings_type: AimbaseSettingsType = AimbaseSettings
    """
    Type of settings object to return.
    """

def set_aimbase_settings(new_aimbase_environment_settings: AimbaseEnvironmentSettings) -> None:
    """
    Set the environment settings and aimbase settings objects.
    """
    global aimbase_environment_settings, aimbase_settings

    aimbase_environment_settings = new_aimbase_environment_settings
    aimbase_settings = aimbase_environment_settings.pull_settings()

    # make sure to set the instarest settings as well
    set_core_settings(aimbase_environment_settings)

def get_aimbase_settings() -> AimbaseSettings:
    """
    Get the aimbase settings object.
    """
    global aimbase_settings

    if aimbase_settings is None:
        raise ValueError("Aimbase Settings not initialized.  Please call set_aimbase_settings() first.")

    return aimbase_settings

def get_aimbase_environment_settings() -> AimbaseEnvironmentSettings:
    """
    Get the aimbase environment settings object.
    """
    global aimbase_environment_settings

    if aimbase_environment_settings is None:
        raise ValueError("Aimbase Settings not initialized.  Please call set_aimbase_settings() first.")

    return aimbase_environment_settings
