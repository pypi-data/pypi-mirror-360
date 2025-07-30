######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.18.1+obcheckpoint(0.2.4);ob(v1)                                                   #
# Generated on 2025-07-07T22:26:05.433514                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.mf_extensions.outerbounds.plugins.apps.core.app_config

from .app_config import AppConfig as AppConfig
from .app_config import AppConfigError as AppConfigError
from .secrets import SecretRetriever as SecretRetriever
from .secrets import SecretNotFound as SecretNotFound
from .dependencies import bake_deployment_image as bake_deployment_image

def deploy_validations(app_config: metaflow.mf_extensions.outerbounds.plugins.apps.core.app_config.AppConfig, cache_dir: str, logger):
    ...

def run_validations(app_config: metaflow.mf_extensions.outerbounds.plugins.apps.core.app_config.AppConfig):
    ...

