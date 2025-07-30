"""Provide Comet functionality for Plurk API 2.0.

This module extends PlurkOAuth to include the Comet feature,
enabling real-time updates and notifications from the Plurk API.

Example usage:
    async with aiohttp.ClientSession() as session:
        cred = OAuthCred(
            consumer_key="your_key",
            consumer_secret="your_secret",
            token="your_token",
            token_secret="your_token_secret"
        )
        comet = PlurkComet(cred, session)
        async for update in comet.connect():
            print(f"Received update: {update}")
"""

import asyncio
import json
import logging
import re
from collections.abc import AsyncGenerator
from typing import Any

import aiohttp

from .oauth import PlurkOAuth, PlurkOAuthError

logger = logging.getLogger(__name__)


class OffsetValueError(TypeError):
    """Exception raised when offset value is less than zero."""

    pass


class PlurkCometError(PlurkOAuthError):
    """Exception raised for Comet-specific errors."""

    pass


class PlurkComet(PlurkOAuth):
    """Plurk Comet Client.

    Handles real-time updates from the Plurk API using Comet long-polling.
    Inherits from PlurkOAuth to handle authentication and API requests.
    """

    def __init__(
        self,
        credentials,
        session: aiohttp.ClientSession,
        retry_delay: int = 5,
        max_retries: int = 3,
    ) -> None:
        """Initialize PlurkComet.

        Parameters
        ----------
        credentials : OAuthCred
            Authentication credentials.
        session : aiohttp.ClientSession
            HTTP session for making requests.
        retry_delay : int, optional
            Delay before retrying after a failure, in seconds (default is 5).
        max_retries : int, optional
            Maximum number of retry attempts (default is 3).

        """
        super().__init__(credentials, session)
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.comet_server: str | None = None
        self.channel_name: str | None = None
        self.offset: int = 0

    async def initialize(self) -> None:
        """Initialize the Comet connection by obtaining the user channel.

        Raises
        ------
        PlurkCometError
            If the user channel cannot be retrieved.

        """
        response = {}
        try:
            response = await self.request("/APP/Realtime/getUserChannel")
        except PlurkOAuthError as e:
            raise PlurkCometError("Error initializing Comet connection.") from e

        self.comet_server = response.get("comet_server")
        self.channel_name = response.get("channel_name")
        if not self.comet_server or not self.channel_name:
            raise PlurkCometError("Failed to retrieve comet server or channel name.")
        self.offset = 0  # Reset offset on successful initialization
        logger.info(f"Initialized Comet channel: {self.channel_name}")

    async def connect(self) -> AsyncGenerator[dict[str, Any], None]:
        """Connect to the Comet long-polling service and yield updates.

        Yields
        ------
        dict
            Updates from the Plurk API.

        Raises
        ------
        PlurkCometError
            If the connection fails after the maximum number of retries.

        """
        if not self.comet_server or not self.channel_name:
            await self.initialize()

        consecutive_offset_errors = 0  # Counter for consecutive OffsetValueErrors

        while True:
            try:
                async with self.session.get(self._build_comet_url(), timeout=aiohttp.ClientTimeout(60)) as response:
                    if not response.ok:
                        raise PlurkCometError(f"Unexpected status code: {response.status}")

                    comet_content = await response.text()
                    match = re.search(r"CometChannel.scriptCallback\((.*)\);", comet_content)
                    if not match:
                        logger.error("Failed to extract JSON from response.")
                        continue  # Continue without retry for this type of error

                    try:
                        json_content = json.loads(match.group(1))
                    except json.JSONDecodeError as err:
                        logger.error(f"JSON Error: {err}")
                        continue  # Continue without retry for this type of error

                    self._process_comet_response(json_content)
                    consecutive_offset_errors = 0  # Reset on successful processing

                    for update in json_content.get("data", []):
                        yield update
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Error in Comet connection: {e}")
                consecutive_offset_errors = 0  # Reset offset error counter on connection error
                if not await self._retry_connection():
                    raise PlurkCometError("Failed to reconnect after multiple attempts.") from e
            except OffsetValueError as e:
                logger.error(f"Offset value error: {e}")
                consecutive_offset_errors += 1
                if consecutive_offset_errors >= self.max_retries:
                    raise PlurkCometError("Received invalid offset after multiple attempts.") from e
                # Attempt to re-initialize and reset offset
                try:
                    await self.initialize()  # This will reset self.offset to 0
                except PlurkCometError as init_e:
                    logger.error(f"Failed to re-initialize after offset error: {init_e}")
                    # If re-initialization fails, we should probably give up
                    raise PlurkCometError(
                        "Failed to re-initialize after offset error and multiple attempts."
                    ) from init_e
                await asyncio.sleep(self.retry_delay)
            except PlurkCometError as e:
                raise e

    async def knock_comet(self) -> bool:
        """Send a knock request to the Plurk Comet generic endpoint to check status."""
        if not self.channel_name:
            return False

        url = "https://www.plurk.com/_comet/generic"
        params = {"channel": self.channel_name}
        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(10)) as response:
                return response.ok
        except aiohttp.ClientError as e:
            logger.error(f"Error knocking Comet: {e}")
            return False

    def _process_comet_response(self, json_content: dict[str, Any]) -> None:
        """Process the comet response and update the offset."""
        new_offset = json_content.get("new_offset")
        if new_offset is not None:
            self.offset = new_offset
            if self.offset < 0:
                raise OffsetValueError(f"Offset Error: {self.offset}")

    def _build_comet_url(self) -> str:
        """Build the URL for the Comet request.

        Returns
        -------
        str
            The complete URL for the Comet request.

        """
        if not self.comet_server or not self.channel_name:
            raise PlurkCometError("Comet server or channel name not initialized.")
        return f"{self.comet_server}&channel={self.channel_name}&offset={self.offset}"

    async def _retry_connection(self) -> bool:
        """Attempt to retry the Comet connection.

        Returns
        -------
        bool
            True if reconnection was successful, False otherwise.

        """
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Retrying connection (attempt {attempt}/{self.max_retries})...")
            await asyncio.sleep(self.retry_delay)
            try:
                await self.initialize()
                return True
            except PlurkCometError as e:
                logger.error(f"Retry attempt {attempt} failed: {e}")
        return False
