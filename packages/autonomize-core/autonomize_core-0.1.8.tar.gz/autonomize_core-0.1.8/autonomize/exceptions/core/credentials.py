"""Exceptions for the modelhub module."""


# Original Exceptions
class ModelhubCredentialException(Exception):
    """Base exception for ModelhubCredential exceptions."""


class ModelhubMissingCredentialsException(ModelhubCredentialException):
    """Raised when modelhub credentials are not provided."""


class ModelhubInvalidTokenException(ModelhubCredentialException):
    """Raised when an ill-formatted or invalid token is provided."""


class ModelhubTokenRetrievalException(ModelhubCredentialException):
    """Raised when the token could not be retrieved."""


class ModelhubUnauthorizedException(ModelhubCredentialException):
    """Raised when the modelhub credentials are invalid."""


# Base exception for ModelHub client
class ModelHubException(Exception):
    """Base exception for all ModelHub client exceptions."""


# API exceptions
class ModelHubAPIException(ModelHubException):
    """Base exception for API-related errors."""


class ModelHubResourceNotFoundException(ModelHubAPIException):
    """Raised when a requested resource is not found."""


class ModelHubBadRequestException(ModelHubAPIException):
    """Raised when the API request is malformed or invalid."""


class ModelHubConflictException(ModelHubAPIException):
    """Raised when there's a conflict with the current state of the resource."""


# Parsing exceptions
class ModelHubParsingException(ModelHubException):
    """Raised when response parsing fails."""
