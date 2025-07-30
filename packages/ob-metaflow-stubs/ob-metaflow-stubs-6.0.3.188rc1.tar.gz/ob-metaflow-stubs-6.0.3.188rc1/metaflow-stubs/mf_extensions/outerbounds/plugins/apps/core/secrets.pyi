######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.15.18.1+obcheckpoint(0.2.4);ob(v1)                                                   #
# Generated on 2025-07-07T22:26:05.432608                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.mf_extensions.outerbounds.plugins.apps.core.secrets

from .utils import safe_requests_wrapper as safe_requests_wrapper
from .utils import TODOException as TODOException

class OuterboundsSecretsException(Exception, metaclass=type):
    ...

class SecretNotFound(OuterboundsSecretsException, metaclass=type):
    ...

class OuterboundsSecretsApiResponse(object, metaclass=type):
    def __init__(self, response):
        ...
    @property
    def secret_resource_id(self):
        ...
    @property
    def secret_backend_type(self):
        ...
    ...

class SecretRetriever(object, metaclass=type):
    def get_secret_as_dict(self, secret_id, options = {}, role = None):
        """
        Supports a special way of specifying secrets sources in outerbounds using the format:
            @secrets(sources=["outerbounds.<integrations_name>"])
        
        When invoked it makes a requests to the integrations secrets metadata endpoint on the
        keywest server to get the cloud resource id for a secret. It then uses that to invoke
        secrets manager on the core oss and returns the secrets.
        """
        ...
    ...

