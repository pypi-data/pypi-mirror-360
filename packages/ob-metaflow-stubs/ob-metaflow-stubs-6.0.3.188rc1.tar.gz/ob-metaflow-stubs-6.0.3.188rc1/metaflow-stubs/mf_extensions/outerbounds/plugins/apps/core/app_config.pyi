######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.18.1+obcheckpoint(0.2.4);ob(v1)                                                   #
# Generated on 2025-07-07T22:26:05.431172                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing

from .cli_to_config import build_config_from_options as build_config_from_options

CODE_PACKAGE_PREFIX: str

CAPSULE_DEBUG: bool

class classproperty(property, metaclass=type):
    def __get__(self, owner_self, owner_cls):
        ...
    ...

class AppConfigError(Exception, metaclass=type):
    """
    Exception raised when app configuration is invalid.
    """
    ...

class AuthType(object, metaclass=type):
    @classmethod
    def enums(cls):
        ...
    @property
    def default(cls):
        ...
    ...

class AppConfig(object, metaclass=type):
    """
    Class representing an Outerbounds App configuration.
    """
    def __init__(self, config_dict: typing.Dict[str, typing.Any]):
        """
        Initialize configuration from a dictionary.
        """
        ...
    def set_state(self, key, value):
        ...
    def get_state(self, key, default = None):
        ...
    def dump_state(self):
        ...
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """
        Get a configuration value by key.
        """
        ...
    def validate(self):
        """
        Validate the configuration against the schema.
        """
        ...
    def set_deploy_defaults(self, packaging_directory: str):
        """
        Set default values for fields that are not provided.
        """
        ...
    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Return the configuration as a dictionary.
        """
        ...
    def to_yaml(self) -> str:
        """
        Return the configuration as a YAML string.
        """
        ...
    def to_json(self) -> str:
        """
        Return the configuration as a JSON string.
        """
        ...
    @classmethod
    def from_file(cls, file_path: str) -> "AppConfig":
        """
        Create a configuration from a file.
        """
        ...
    def update_from_cli_options(self, options):
        """
        Update configuration from CLI options using the same logic as build_config_from_options.
        This ensures consistent handling of CLI options whether they come from a config file
        or direct CLI input.
        """
        ...
    ...

