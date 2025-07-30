######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.18.1+obcheckpoint(0.2.4);ob(v1)                                                   #
# Generated on 2025-07-07T22:26:05.436396                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow._vendor.click.types
    import metaflow.mf_extensions.outerbounds.plugins.apps.core.app_cli
    import metaflow.mf_extensions.outerbounds.plugins.apps.core.app_config

from ......_vendor import click as click
from .app_config import AppConfig as AppConfig
from .app_config import AppConfigError as AppConfigError
from .app_config import AuthType as AuthType
from .perimeters import PerimeterExtractor as PerimeterExtractor
from .cli_to_config import build_config_from_options as build_config_from_options
from .utils import MultiStepSpinner as MultiStepSpinner
from . import experimental as experimental
from .validations import deploy_validations as deploy_validations
from .code_package.code_packager import CodePackager as CodePackager
from .capsule import CapsuleDeployer as CapsuleDeployer
from .capsule import list_and_filter_capsules as list_and_filter_capsules
from .capsule import CapsuleApi as CapsuleApi
from ._state_machine import DEPLOYMENT_READY_CONDITIONS as DEPLOYMENT_READY_CONDITIONS
from .capsule import CapsuleApiException as CapsuleApiException
from .capsule import CapsuleDeploymentException as CapsuleDeploymentException
from .dependencies import bake_deployment_image as bake_deployment_image

CODE_PACKAGE_PREFIX: str

CAPSULE_DEBUG: bool

class KeyValueDictPair(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class KeyValuePair(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class MountMetaflowArtifact(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        """
        Convert a string like "flow=MyFlow,artifact=my_model,path=/tmp/abc" or
        "pathspec=MyFlow/123/foo/345/my_model,path=/tmp/abc" to a dict.
        """
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class MountSecret(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        """
        Convert a string like "id=my_secret,path=/tmp/secret" to a dict.
        """
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

class CommaSeparatedList(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

KVPairType: KeyValuePair

MetaflowArtifactType: MountMetaflowArtifact

SecretMountType: MountSecret

CommaSeparatedListType: CommaSeparatedList

KVDictType: KeyValueDictPair

class ColorTheme(object, metaclass=type):
    ...

class CliState(object, metaclass=type):
    ...

def print_table(data, headers):
    """
    Print data in a formatted table.
    """
    ...

def parse_commands(app_config: metaflow.mf_extensions.outerbounds.plugins.apps.core.app_config.AppConfig, cli_command_input):
    ...

def deployment_instance_options(func):
    ...

def common_deploy_options(func):
    ...

def common_run_options(func):
    """
    Common options for running and deploying apps.
    """
    ...

