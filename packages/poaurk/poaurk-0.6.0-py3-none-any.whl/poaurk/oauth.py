"""Provide basic OAuth1 operations for Plurk API 2.0.

This module facilitates OAuth1 authentication for accessing the Plurk API 2.0.
It includes functionality for obtaining request tokens, authorizing access, and
retrieving access tokens.

Example usage:
    async with aiohttp.ClientSession() as session:
        cred = OAuthCred(
            customer_key="your_key",
            customer_secret="your_secret",
            token=None,
            token_secret=None
        )
        client = PlurkOAuth(cred, session)
        await client.authorize()
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin

import aiohttp
import oauthlib.oauth1
from aiohttp import FormData

HTTP_BAD_REQUEST = 400

# Set up logging
logger = logging.getLogger(__name__)


class PlurkOAuthError(Exception):
    """Base exception for Plurk OAuth errors."""

    pass


class PlurkNetworkError(PlurkOAuthError):
    """Raised when network communication fails."""

    pass


class PlurkBadRequestError(PlurkNetworkError):
    """Raised when a 400 Bad Request with JSON body is received."""

    pass


class PlurkAuthorizationError(PlurkOAuthError):
    """Raised when authorization fails."""

    pass


@dataclass
class OAuthCred:
    """OAuth Credentials Dataclass.

    Attributes
    ----------
    customer_key : str
        The consumer key provided by Plurk.
    customer_secret : str
        The consumer secret provided by Plurk.
    token : Optional[str]
        The OAuth token, initially None.
    token_secret : Optional[str]
        The OAuth token secret, initially None.

    """

    customer_key: str
    customer_secret: str
    token: str | None = None
    token_secret: str | None = None

    def to_client(self) -> oauthlib.oauth1.Client:
        """Convert OAuth credentials to OAuth client.

        Returns
        -------
        oauthlib.oauth1.Client
            Configured OAuth client ready for making authenticated requests.

        """
        return oauthlib.oauth1.Client(
            client_key=self.customer_key,
            client_secret=self.customer_secret,
            resource_owner_key=self.token,
            resource_owner_secret=self.token_secret,
        )


class UserInteraction(ABC):
    """Abstract base class for user interaction during OAuth flow."""

    @staticmethod
    @abstractmethod
    async def get_verification_code(url: str) -> str:
        """Get verification code from user.

        Parameters
        ----------
        url : str
            Authorization URL to be displayed to user.

        Returns
        -------
        str
            Verification code entered by user.

        """
        pass


class CliUserInteraction(UserInteraction):
    """Command-line implementation of user interaction."""

    @staticmethod
    async def get_verification_code(url: str) -> str:
        """Get verification code via command line.

        Parameters
        ----------
        url : str
            Authorization URL to be displayed to user.

        Returns
        -------
        str
            Verification code entered by user.

        Notes
        -----
        Uses asyncio.to_thread to prevent blocking the event loop.

        """
        print("Open the following URL and authorize it.")
        print(url)

        while True:
            verifier = await asyncio.to_thread(input, "Input the verification number: ")
            verified = await asyncio.to_thread(input, "Are you sure? (y/n) ")

            if verified.lower() == "y" and verifier:
                return verifier

            if verified.lower() != "n":
                print("Please answer 'y' or 'n'")


class PlurkOAuth:
    """Plurk OAuth Client.

    Handles OAuth authentication flow for Plurk API 2.0.
    """

    def __init__(
        self,
        cred: OAuthCred,
        session: aiohttp.ClientSession,
        user_interaction: UserInteraction | None = None,
        timeout: int = 60,
        base_url: str = "https://www.plurk.com/",
    ) -> None:
        """Initialize PlurkOAuth.

        Parameters
        ----------
        cred : OAuthCred
            OAuth credentials
        session : aiohttp.ClientSession
            Aiohttp client session
        user_interaction : Optional[UserInteraction]
            Interface for user interaction, defaults to CliUserInteraction
        timeout : int
            Request timeout in seconds
        base_url : str
            Base URL for Plurk API

        """
        self.cred = cred
        self.session = session
        self.user_interaction = user_interaction or CliUserInteraction()
        self.timeout = timeout
        self.base_url = base_url
        self.plurk_error: str | None = None  # Store error messages from Plurk API

        # API endpoints
        self._request_token_url = "OAuth/request_token"
        self._authorization_url = "OAuth/authorize"
        self._access_token_url = "OAuth/access_token"

    @asynccontextmanager
    async def _handle_request_errors(self):
        """Context manager for handling request errors.

        Raises
        ------
        PlurkNetworkError
            When network communication fails
        PlurkAuthorizationError
            When authorization fails
        PlurkOAuthError
            For other OAuth-related errors

        """
        try:
            yield
        except aiohttp.ClientError as e:
            if self.plurk_error:
                reason = self.plurk_error
                self.plurk_error = None  # Reset error after logging
                logger.error(f"Plurk API error: {reason}")
                raise PlurkBadRequestError(f"Plurk API error: {reason}") from e
            logger.error(f"Network error: {e}")
            raise PlurkNetworkError(f"Failed to communicate with Plurk: {e}") from e
        except oauthlib.oauth1.OAuth1Error as e:
            logger.error(f"OAuth error: {e}")
            raise PlurkAuthorizationError(f"OAuth authorization failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise PlurkOAuthError(f"Unexpected error: {e}") from e

    async def authorize(self, access_token: tuple[str, str] | None = None) -> None:
        """Authorize access to Plurk API.

        Parameters
        ----------
        access_token : Optional[Tuple[str, str]]
            Tuple of (token, token_secret) if already available

        """
        async with self._handle_request_errors():
            if access_token:
                self.cred.token, self.cred.token_secret = access_token
            else:
                await self._complete_oauth_flow()

    async def _complete_oauth_flow(self) -> None:
        """Complete the OAuth flow by getting request token, verifier, and access token."""
        await self.get_request_token()
        verifier = await self.get_verifier()
        await self.get_access_token(verifier)

    async def request(
        self,
        method: str,
        data: dict[str, str] | None = None,
        files: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the Plurk API.

        Parameters
        ----------
        method : str
            The API endpoint
        data : Optional[Dict[str, str]]
            Request data
        files : Optional[Dict[str, str]]
            Files to upload

        Returns
        -------
        Dict[str, Any]
            Response data

        """
        async with self._handle_request_errors():
            client = self.cred.to_client()
            uri = urljoin(self.base_url, method)

            # Handle verifier in data
            if data and "verifier" in data:
                client.verifier = data.pop("verifier")

            # Prepare request data and headers
            headers, body_for_signing, request_data_for_aiohttp = await self._prepare_request_data(data, files)

            # Determine if it's a multipart request
            is_multipart = isinstance(request_data_for_aiohttp, FormData)

            if is_multipart:
                # 🚨 Don't pass body to oauthlib — Plurk does NOT want body fields signed
                uri, signed_headers, _ = client.sign(
                    uri=uri,
                    http_method="POST",
                    headers={},  # Do not include Content-Type or anything
                    body=None,  # ← critical
                )

                # Remove oauthlib-signed Content-Type (useless here)
                signed_headers.pop("Content-Type", None)

                final_headers = signed_headers

            else:
                uri, signed_headers, signed_body = client.sign(
                    uri=uri,
                    http_method="POST",
                    body=body_for_signing,
                    headers=headers,
                )
                request_data_for_aiohttp = signed_body
                final_headers = {**headers, **signed_headers}

            # Make the request
            try:
                async with self.session.post(
                    uri,
                    data=request_data_for_aiohttp,
                    headers=final_headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status == HTTP_BAD_REQUEST and response.content_type == "application/json":
                        json_body = await response.json()
                        self.plurk_error = json_body.get("error_text")
                    response.raise_for_status()
                    return await self._parse_response(response)
            finally:
                # Close any opened files to avoid resource leaks
                if hasattr(self, "_opened_files"):
                    for f in self._opened_files:
                        f.close()
                    del self._opened_files

    async def _prepare_request_data(
        self, data: dict[str, str] | None, files: dict[str, str] | None
    ) -> tuple[dict[str, str], Any, Any]:
        """Prepare request data and headers.

        Returns
        -------
        Tuple[Dict[str, str], Any, Any]
            Headers, body for signing, and request data for aiohttp.

        """
        body_for_signing_dict = data.copy() if data else {}
        request_data_for_aiohttp = data

        if files:
            headers = {}  # Let aiohttp handle Content-Type for multipart
            form_data = FormData()
            # Open files and add fields, ensure files are closed after request
            self._opened_files = []
            for key, filepath in files.items():
                f = open(filepath, "rb")
                self._opened_files.append(f)
                form_data.add_field(key, f, filename=filepath.split("/")[-1])
                # Only for OAuth signing: dummy value
                body_for_signing_dict[key] = "file"

            if data:
                for k, v in data.items():
                    form_data.add_field(k, v)

            request_data_for_aiohttp = form_data
            body_for_signing = body_for_signing_dict  # Dict for oauthlib multipart signing
        else:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            body_for_signing = urlencode(body_for_signing_dict) if body_for_signing_dict else ""
            request_data_for_aiohttp = body_for_signing

        return headers, body_for_signing, request_data_for_aiohttp

    @staticmethod
    async def _parse_response(response: aiohttp.ClientResponse) -> dict[str, Any]:
        """Parse API response based on content type.

        Parameters
        ----------
        response : aiohttp.ClientResponse
            Response from Plurk API

        Returns
        -------
        Dict[str, Any]
            Parsed response data

        Raises
        ------
        TypeError
            When content type is not supported

        """
        if response.content_type == "application/json":
            return await response.json()
        if response.content_type == "text/html":
            return dict(parse_qsl(await response.text()))
        raise TypeError(f"Invalid content type: {response.content_type}")

    async def get_request_token(self) -> None:
        """Get OAuth request token."""
        self.cred.token = None
        self.cred.token_secret = None

        response = await self.request(self._request_token_url)
        self.cred.token = response["oauth_token"]
        self.cred.token_secret = response["oauth_token_secret"]

    def get_verifier_url(self) -> str:
        """Get verifier URL.

        Returns
        -------
        str
            URL for user authorization

        Raises
        ------
        PlurkAuthorizationError
            If tokens are not available

        """
        if not self.cred.token or not self.cred.token_secret:
            raise PlurkAuthorizationError("Please request a token first")
        return f"{self.base_url}{self._authorization_url}?oauth_token={self.cred.token}"

    async def get_verifier(self) -> str:
        """Get OAuth verifier code through user interaction.

        Returns
        -------
        str
            OAuth verifier code

        """
        return await self.user_interaction.get_verification_code(self.get_verifier_url())

    async def get_access_token(self, verifier: str) -> None:
        """Get OAuth access token using verifier.

        Parameters
        ----------
        verifier : str
            OAuth verifier code

        """
        response = await self.request(self._access_token_url, data={"verifier": verifier})
        self.cred.token = response["oauth_token"]
        self.cred.token_secret = response["oauth_token_secret"]
