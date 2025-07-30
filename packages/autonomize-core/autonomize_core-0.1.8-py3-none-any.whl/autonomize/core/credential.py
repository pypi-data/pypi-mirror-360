"""ModelhubCredential Implementation"""

# pylint: disable=line-too-long, invalid-name, duplicate-code

import base64
import json
import os
import ssl
import time
from typing import Optional

import httpx

from autonomize.exceptions.core import (
    ModelhubInvalidTokenException,
    ModelhubMissingCredentialsException,
    ModelhubTokenRetrievalException,
    ModelhubUnauthorizedException,
)
from autonomize.types.core.base_client import VerifySSLTypes
from autonomize.utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelhubCredential:
    """
    ModelhubCredential Class.

    This class instantiates a ModelhubCredential client to authenticate request to Modelhub.

    Example:
    .. code-block:: python

        from autonomize.core.credential import ModelhubCredential

        # Using modelhub_url (recommended)
        modelhub_credential = ModelhubCredential(
            modelhub_url="https://example.com",
            client_id="modelhub-client",
            client_secret="xxx"
        )

        # Using token directly
        modelhub_credential = ModelhubCredential(
            token="xxx"
        )
    """

    def __init__(
        self,
        modelhub_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
        auth_url: Optional[str] = None,  # Kept for backward compatibility
        verify_ssl: VerifySSLTypes = True,
    ):
        """
        Initialize the ModelhubCredential instance.

        Args:
            modelhub_url (Optional[str]): The base URL for ModelHub services. Defaults to None.
            client_id (Optional[str]): The client ID for authentication.
            client_secret (Optional[str]): The client secret for authentication.
            token (Optional[str]): An existing JWT token for authentication.
            auth_url (Optional[str]): The direct authentication URL (legacy parameter).
            verify_ssl (VerifySSLTypes): Either `True` to use an SSL context with the default CA bundle, False to disable verification, or an instance of `ssl.SSLContext` to use a custom context.

        Raises:
            ModelhubMissingCredentialsException: If neither (client_id and client_secret) nor token is provided.
        """
        # Initialize base URL
        self._modelhub_url = modelhub_url or (
            os.getenv("MODELHUB_URI", "").strip()
            or os.getenv("MODELHUB_BASE_URL", "").strip()
            or None
        )
        self._client_id = client_id or (
            os.getenv("MODELHUB_AUTH_CLIENT_ID", "").strip()
            or os.getenv("MODELHUB_CLIENT_ID", "").strip()
            or None
        )
        self._client_secret = client_secret or (
            os.getenv("MODELHUB_AUTH_CLIENT_SECRET", "").strip()
            or os.getenv("MODELHUB_CLIENT_SECRET", "").strip()
            or None
        )
        self._token = token

        # Derive auth_url from modelhub_url if available, otherwise use provided auth_url or default
        if self._modelhub_url:
            self._auth_url = f"{self._modelhub_url}/ums/api/v1/auth/get-token"
        elif auth_url:
            # Legacy support for direct auth_url
            self._auth_url = auth_url
            logger.warning(
                "Using direct auth_url is deprecated. Please use modelhub_url instead."
            )
        else:
            # Default URL as a fallback
            self._auth_url = "https://auth.sprint.autonomize.dev/realms/autonomize/protocol/openid-connect/token"

        # SSL Config
        self.verify_ssl = verify_ssl
        if isinstance(self.verify_ssl, str):
            if os.path.isdir(self.verify_ssl):
                self.verify_ssl = ssl.create_default_context(capath=self.verify_ssl)
            self.verify_ssl = ssl.create_default_context(cafile=self.verify_ssl)  # type: ignore[arg-type]

        # Validate credentials
        if self._client_id is None or self._client_secret is None:
            if self._token is None:
                raise ModelhubMissingCredentialsException(
                    "Either (`client_id` and `client_secret`) or `token` must be provided."
                )
            logger.warning(
                "It is recommended to provide `client_id` and `client_secret` over `token` "
                "because token gets expired within 24 hours. "
                "You can use `ModelhubCredential.is_token_expired(your_token)` to check if it has expired or not."
            )

    @property
    def auth_url(self) -> str:
        """Get the authentication URL."""
        return self._auth_url

    def reset_token(self) -> None:
        """Reset the token to force a new token fetch on next request."""
        self._token = None  # pragma: no cover
        logger.debug(
            "Token reset, will fetch a new token on next request"
        )  # pragma: no cover

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Checks whether the provided JWT token is expired or not.

        Args:
            token (str): The JWT token to check if its expired or not.

        Returns:
            bool: True if token has expired, otherwise False.

        Raises:
            ModelhubInvalidTokenException: When the token provided is ill-formatted.
        """

        # Split the token by `.` to get it in list
        b64_components = token.split(".")

        # The token should have three components: header, payload and signature.
        if len(b64_components) != 3:
            raise ModelhubInvalidTokenException(
                "Ill-formatted token provided. Please recheck your token."
            )

        # Divide it into, header, payload and signature,
        # but we don't need header and signature.
        _, payload_b64, _ = b64_components

        payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode("utf-8")
        payload = json.loads(payload_json)

        # Get expiry time in Unix-epoch time.
        token_expiry_time = payload["exp"]

        return token_expiry_time < int(time.time())

    def get_token(self) -> str:
        """
        Obtains a JWT token for authorization if token is not provided or has expired.

        Returns:
            str: JWT token.
        """
        if not self._token or ModelhubCredential.is_token_expired(self._token):
            if not self._client_id or not self._client_secret:
                raise ModelhubMissingCredentialsException(  # pragma: no cover
                    "client_id and client_secret must be provided to fetch JWT token."
                )

            with httpx.Client(timeout=None, verify=self.verify_ssl) as client:
                response = client.post(
                    self.auth_url,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "scope": "openid",
                    },
                )

                if response.status_code == 401:
                    raise ModelhubUnauthorizedException(
                        "Client Error `401 Unauthorized`: client_id or client_secret is invalid."
                    )
                response.raise_for_status()

                # Handle different response formats
                json_response = response.json()
                if "id_token" in json_response:
                    self._token = json_response["id_token"]
                elif (
                    "token" in json_response
                    and "access_token" in json_response["token"]
                ):
                    self._token = json_response["token"]["access_token"]
                elif "access_token" in json_response:
                    self._token = json_response["access_token"]
                else:
                    raise ModelhubTokenRetrievalException(
                        f"Could not find token in response: {json_response}"
                    )

        # Ensure token is not None before returning
        if not self._token:
            raise ModelhubTokenRetrievalException(  # pragma: no cover
                "Token could not be retrieved."
            )
        return self._token

    async def aget_token(self) -> str:
        """
        Asynchronously obtains a JWT token for authorization if token is not provided or has expired.

        Returns:
            str: JWT token.
        """
        if not self._token or ModelhubCredential.is_token_expired(self._token):
            if not self._client_id or not self._client_secret:
                raise ModelhubMissingCredentialsException(
                    "client_id and client_secret must be provided to fetch JWT token."
                )

            async with httpx.AsyncClient(
                timeout=None, verify=self.verify_ssl
            ) as client:
                response = await client.post(
                    self.auth_url,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "scope": "openid",
                    },
                )

                if response.status_code == 401:
                    raise ModelhubUnauthorizedException(
                        "Client Error `401 Unauthorized`: client_id or client_secret is invalid."
                    )
                response.raise_for_status()

                # Handle different response formats
                json_response = response.json()
                if "id_token" in json_response:
                    self._token = json_response["id_token"]
                elif (
                    "token" in json_response
                    and "access_token" in json_response["token"]
                ):
                    self._token = json_response["token"]["access_token"]
                elif "access_token" in json_response:
                    self._token = json_response["access_token"]
                else:
                    raise ModelhubTokenRetrievalException(
                        f"Could not find token in response: {json_response}"
                    )

        # Ensure token is not None before returning
        if not self._token:
            raise ModelhubTokenRetrievalException(
                "Token could not be retrieved."
            )  # pragma: no cover
        return self._token
