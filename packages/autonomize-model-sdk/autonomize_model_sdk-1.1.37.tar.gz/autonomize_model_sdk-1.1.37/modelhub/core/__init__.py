"""
This module provides the core functionality for the ModelHub SDK.

Classes:
- BaseClient: The base client class for interacting with the ModelHub API.
- ModelhubCredential: Credential class for ModelHub authentication.

Functions:
- handle_response: Helper function for handling API responses.
"""

# Import from autonomize-core package
from autonomize.core import BaseClient, ahandle_response, handle_response
from autonomize.core.credential import ModelhubCredential
from autonomize.exceptions.core.credentials import (
    ModelHubAPIException,
    ModelHubBadRequestException,
    ModelHubConflictException,
    ModelHubException,
    ModelhubInvalidTokenException,
    ModelhubMissingCredentialsException,
    ModelHubParsingException,
    ModelHubResourceNotFoundException,
    ModelhubTokenRetrievalException,
    ModelhubUnauthorizedException,
)

__all__ = [
    "BaseClient",
    "ModelhubCredential",
    "handle_response",
    "ahandle_response",
    "ModelHubException",
    "ModelHubAPIException",
    "ModelHubBadRequestException",
    "ModelHubConflictException",
    "ModelHubResourceNotFoundException",
    "ModelhubMissingCredentialsException",
    "ModelhubUnauthorizedException",
    "ModelhubInvalidTokenException",
    "ModelhubTokenRetrievalException",
    "ModelHubParsingException",
]
