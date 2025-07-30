"""
This module contains the BaseClient class for handling common HTTP operations
and token management using a simplified, credential-focused approach.
"""

# pylint: disable=C0301

import os
import ssl
from typing import Any, Dict, Optional

import httpx

from autonomize.core.credential import ModelhubCredential
from autonomize.exceptions.core.credentials import (
    ModelHubAPIException,
    ModelHubBadRequestException,
    ModelHubConflictException,
    ModelhubMissingCredentialsException,
    ModelHubResourceNotFoundException,
    ModelhubUnauthorizedException,
)
from autonomize.types.core.base_client import VerifySSLTypes
from autonomize.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseClient:
    """Base client for handling common HTTP operations with ModelhubCredential integration."""

    def __init__(
        self,
        credential: ModelhubCredential,
        client_id: Optional[str] = None,
        copilot_id: Optional[str] = None,
        timeout: int = 10,
        verify_ssl: VerifySSLTypes = True,
    ):
        """
        Initialize a new instance of the BaseClient class.

        Args:
            credential (ModelhubCredential): Credential object for token management and base URL.
            client_id (Optional[str]): Client ID for API URL construction.
                                       Defaults to CLIENT_ID env var if not provided.
            copilot_id (Optional[str]): Copilot ID for API URL construction.
                                        Defaults to COPILOT_ID env var if not provided.
            timeout (int, optional): Request timeout in seconds. Defaults to 10.
            verify_ssl (VerifySSLTypes): Whether to verify SSL certificates. Defaults to True.

        Raises:
            ModelhubMissingCredentialsException: If required credential information is missing.
        """
        # Store the credential
        self.credential = credential

        # Get client and copilot IDs from args or environment
        self.client_id = (
            client_id or os.getenv("GENESIS_CLIENT_ID") or os.getenv("CLIENT_ID")
        )
        self.copilot_id = (
            copilot_id or os.getenv("GENESIS_COPILOT_ID") or os.getenv("COPILOT_ID")
        )

        # Other configuration
        self.timeout = timeout

        # SSL configuration
        self.verify_ssl = verify_ssl
        if isinstance(self.verify_ssl, str):
            if os.path.isdir(self.verify_ssl):
                self.verify_ssl = ssl.create_default_context(capath=self.verify_ssl)
            self.verify_ssl = ssl.create_default_context(cafile=self.verify_ssl)  # type: ignore[arg-type]

        # Create HTTP clients with retry configured
        self.client = self._setup_client()
        self.async_client = self._setup_async_client()

        # Validate we can construct API URL
        try:
            api_url = self.api_url
            logger.debug("Initializing client with API URL: %s", api_url)
        except Exception as e:
            logger.error("Failed to construct API URL: %s", str(e))
            raise ModelhubMissingCredentialsException(
                "Unable to construct API URL. Ensure ModelhubCredential has a valid modelhub_url."
            ) from e

    @property
    def api_url(self) -> str:
        """
        Get the complete API URL by combining the base URL with client and copilot IDs.

        Returns:
            str: The complete API URL.

        Raises:
            ModelhubMissingCredentialsException: If required IDs are missing.
        """
        # Get the base URL from the credential
        base_url = getattr(self.credential, "_modelhub_url", None)
        if not base_url:
            raise ModelhubMissingCredentialsException(
                "ModelhubCredential must have a valid modelhub_url."
            )

        # Check if we have client and copilot IDs
        if not self.client_id or not self.copilot_id:
            raise ModelhubMissingCredentialsException(
                "Client ID and Copilot ID are required for API URL construction."
            )

        # Construct the full API URL
        return (
            f"{base_url}/modelhub/api/v1/client/{self.client_id}/"
            f"copilot/{self.copilot_id}"
        )

    def _setup_client(self) -> httpx.Client:
        """
        Set up a synchronous HTTPX client with retry configuration.

        Returns:
            httpx.Client: Configured client object.
        """
        transport = httpx.HTTPTransport(
            verify=self.verify_ssl,   #patch done for molina ssl issue
            retries=3,  # Total number of retries
        )

        return httpx.Client(
            transport=transport,
            timeout=self.timeout,
            follow_redirects=True,
            verify=self.verify_ssl,
        )

    def _setup_async_client(self) -> httpx.AsyncClient:
        """
        Set up an asynchronous HTTPX client with retry configuration.

        Returns:
            httpx.AsyncClient: Configured async client object.
        """
        transport = httpx.AsyncHTTPTransport(
            retries=3,  # Total number of retries
        )

        return httpx.AsyncClient(
            transport=transport,
            timeout=self.timeout,
            follow_redirects=True,
            verify=self.verify_ssl,
        )

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers using the credential.

        Returns:
            Dict[str, str]: Headers dictionary with authorization token.
        """
        token = self.credential.get_token()
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    async def _aget_auth_headers(self) -> Dict[str, str]:
        """
        Asynchronously get authentication headers using the credential.

        Returns:
            Dict[str, str]: Headers dictionary with authorization token.
        """
        token = await self.credential.aget_token()
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    def _handle_error_status(self, response: httpx.Response) -> None:
        """
        Handle common HTTP error status codes.

        Args:
            response (httpx.Response): The HTTP response.

        Raises:
            ModelHubResourceNotFoundException: For 404 errors.
            ModelHubBadRequestException: For 400 errors.
            ModelhubUnauthorizedException: For 401/403 errors.
            ModelHubConflictException: For 409 errors.
            ModelHubAPIException: For other HTTP errors.
        """
        if response.status_code == 404:
            raise ModelHubResourceNotFoundException(
                f"Resource not found: {response.url}"
            )
        if response.status_code == 400:
            raise ModelHubBadRequestException(f"Bad request: {response.text}")
        if response.status_code in (401, 403):
            raise ModelhubUnauthorizedException(f"Unauthorized: {response.text}")
        if response.status_code == 409:
            raise ModelHubConflictException(f"Conflict: {response.text}")
        if response.status_code >= 400:
            raise ModelHubAPIException(
                f"API error {response.status_code}: {response.text}"
            )

    def request(
        self,
        method: str,
        endpoint: str,
        retry_auth: bool = True,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Send a request with automatic token handling and optional retry.

        Args:
            method (str): The HTTP method for the request.
            endpoint (str): The endpoint to send the request to.
            retry_auth (bool, optional): Whether to retry on auth failure. Defaults to True.
            headers (Optional[Dict[str, str]], optional): Additional headers. Defaults to None.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            Dict[str, Any]: The response data.

        Raises:
            ModelHubResourceNotFoundException: If the resource is not found.
            ModelHubBadRequestException: If the request is invalid.
            ModelhubUnauthorizedException: If unauthorized.
            ModelHubAPIException: For other API errors.
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        logger.debug("Making %s request to: %s", method, url)

        # Prepare headers with auth token
        request_headers = headers or {}
        auth_headers = self._get_auth_headers()

        # If files are being uploaded, don't include Content-Type in auth_headers
        if "files" in kwargs:
            auth_headers = {"Authorization": auth_headers["Authorization"]}

        merged_headers = {**auth_headers, **request_headers}

        try:
            # Make the initial request
            response = self.client.request(
                method, url, headers=merged_headers, **kwargs
            )

            # If we get a 401, retry with a fresh token
            if response.status_code == 401 and retry_auth:
                logger.debug("Received 401, refreshing token and retrying")
                # Force credential to get a new token
                self.credential.reset_token()  # Use the proper method instead of direct access
                auth_headers = self._get_auth_headers()
                merged_headers = {**auth_headers, **request_headers}

                # Retry the request with the new token
                response = self.client.request(
                    method, url, headers=merged_headers, **kwargs
                )

                # If still unauthorized, handle the error
                if response.status_code == 401:
                    self._handle_error_status(response)

            # Handle any error status codes
            if response.status_code >= 400:
                self._handle_error_status(response)

            # Parse and return the response
            return handle_response(response)

        except httpx.HTTPError as e:
            logger.error("Request failed: %s", str(e))
            if isinstance(e, httpx.HTTPStatusError):
                self._handle_error_status(e.response)
            raise ModelHubAPIException(f"Request failed: {str(e)}") from e

    async def arequest(
        self,
        method: str,
        endpoint: str,
        retry_auth: bool = True,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Send an asynchronous request with automatic token handling and optional retry.

        Args:
            method (str): The HTTP method for the request.
            endpoint (str): The endpoint to send the request to.
            retry_auth (bool, optional): Whether to retry on auth failure. Defaults to True.
            headers (Optional[Dict[str, str]], optional): Additional headers. Defaults to None.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            Dict[str, Any]: The response data.

        Raises:
            ModelHubResourceNotFoundException: If the resource is not found.
            ModelHubBadRequestException: If the request is invalid.
            ModelhubUnauthorizedException: If unauthorized.
            ModelHubAPIException: For other API errors.
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        logger.debug("Making async %s request to: %s", method, url)

        # Prepare headers with auth token
        request_headers = headers or {}
        auth_headers = await self._aget_auth_headers()
        merged_headers = {**auth_headers, **request_headers}

        try:
            # Make the initial request
            response = await self.async_client.request(
                method, url, headers=merged_headers, **kwargs
            )

            # If we get a 401, retry with a fresh token
            if response.status_code == 401 and retry_auth:
                logger.debug("Received 401, refreshing token and retrying (async)")
                # Force credential to get a new token
                self.credential.reset_token()  # Use the proper method instead of direct access
                auth_headers = await self._aget_auth_headers()
                merged_headers = {**auth_headers, **request_headers}

                # Retry the request with the new token
                response = await self.async_client.request(
                    method, url, headers=merged_headers, **kwargs
                )

                # If still unauthorized, handle the error
                if response.status_code == 401:
                    self._handle_error_status(response)

            # Handle any error status codes
            if response.status_code >= 400:
                self._handle_error_status(response)

            # Parse and return the response
            return await ahandle_response(response)

        except httpx.HTTPError as e:
            logger.error("Async request failed: %s", str(e))
            if isinstance(e, httpx.HTTPStatusError):
                self._handle_error_status(e.response)
            raise ModelHubAPIException(f"Request failed: {str(e)}") from e

    # Convenience methods for common HTTP operations

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send a GET request to the specified endpoint."""
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send a POST request to the specified endpoint."""
        return self.request(
            "POST", endpoint, json=json, data=data, files=files, **kwargs
        )

    def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send a PUT request to the specified endpoint."""
        return self.request("PUT", endpoint, json=json, **kwargs)

    def patch(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send a PATCH request to the specified endpoint."""
        return self.request("PATCH", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a DELETE request to the specified endpoint."""
        return self.request("DELETE", endpoint, **kwargs)

    # Asynchronous convenience methods

    async def aget(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send an asynchronous GET request to the specified endpoint."""
        return await self.arequest("GET", endpoint, params=params, **kwargs)

    async def apost(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Send an asynchronous POST request to the specified endpoint."""
        return await self.arequest(
            "POST", endpoint, json=json, data=data, files=files, **kwargs
        )

    async def aput(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send an asynchronous PUT request to the specified endpoint."""
        return await self.arequest("PUT", endpoint, json=json, **kwargs)

    async def apatch(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Send an asynchronous PATCH request to the specified endpoint."""
        return await self.arequest("PATCH", endpoint, json=json, **kwargs)

    async def adelete(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Send an asynchronous DELETE request to the specified endpoint."""
        return await self.arequest("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close the HTTPX clients when done."""
        self.client.close()

    async def aclose(self) -> None:
        """Asynchronously close the HTTPX async client when done."""
        await self.async_client.aclose()


def handle_response(response: httpx.Response) -> Dict[str, Any]:
    """
    Synchronously handle the response from an HTTP request.

    Args:
        response (httpx.Response): The response object from the HTTP request.

    Returns:
        dict: The JSON response from the HTTP request.

    Raises:
        httpx.HTTPError: If the HTTP response status code is an error.
        ValueError: If the response is not a valid JSON.
    """
    try:
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logger.error("HTTP error: %s", str(e))
        raise
    except ValueError as e:
        logger.error("Invalid JSON response: %s", str(e))
        raise


async def ahandle_response(response: httpx.Response) -> Dict[str, Any]:
    """
    Asynchronously handles the response from an HTTP request.

    Args:
        response (httpx.Response): The response object from the HTTP request.

    Returns:
        dict: The JSON response from the HTTP request.

    Raises:
        httpx.HTTPError: If the HTTP response status code is an error.
        ValueError: If the response is not a valid JSON.
    """
    try:
        response.raise_for_status()
        # Use sync version for simplicity - httpx.Response.json()
        # is not a coroutine in current versions
        return response.json()
    except httpx.HTTPError as e:
        logger.error("HTTP error: %s", str(e))
        raise
    except ValueError as e:
        logger.error("Invalid JSON response: %s", str(e))
        raise
