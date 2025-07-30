import json
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from poaurk.comet import PlurkComet, PlurkCometError
from poaurk.oauth import OAuthCred


@pytest.fixture
async def mock_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
def oauth_credentials():
    return OAuthCred(
        customer_key="test_key",
        customer_secret="test_secret",
        token="test_token",
        token_secret="test_token_secret",
    )


@pytest.fixture
async def comet_client(oauth_credentials, mock_session):
    return PlurkComet(oauth_credentials, mock_session)


@pytest.mark.asyncio
async def test_initialize_comet(comet_client):
    mock_response = {
        "comet_server": "https://comet03.plurk.com/comet/123456789/",
        "channel_name": "generic-4-abcdef1234567890",
    }

    with patch.object(comet_client, "request", new=AsyncMock(return_value=mock_response)):
        await comet_client.initialize()
        assert comet_client.comet_server == mock_response["comet_server"]
        assert comet_client.channel_name == mock_response["channel_name"]


@pytest.mark.asyncio
async def test_initialize_comet_failure(comet_client):
    with patch.object(comet_client, "request", new=AsyncMock(return_value={})):
        with pytest.raises(PlurkCometError, match="Failed to retrieve comet server or channel name"):
            await comet_client.initialize()


@pytest.mark.asyncio
async def test_connect_with_updates(comet_client):
    comet_client.comet_server = "https://comet03.plurk.com/comet/123456789/"
    comet_client.channel_name = "generic-4-abcdef1234567890"

    mock_response = {"new_offset": 21, "data": [{"plurk_id": 123456, "type": "new_plurk"}]}

    with patch.object(comet_client.session, "get") as mock_get:
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.text.return_value = f"CometChannel.scriptCallback({json.dumps(mock_response)});"
        mock_response_obj.__aenter__.return_value = mock_response_obj
        mock_response_obj.__aexit__.return_value = None
        mock_get.return_value = mock_response_obj
        async for update in comet_client.connect():
            assert update["plurk_id"] == 123456  # noqa: PLR2004
            assert update["type"] == "new_plurk"
            break


@pytest.mark.asyncio
async def test_connect_retry_on_error(comet_client):
    comet_client.comet_server = "https://comet03.plurk.com/comet/123456789/"
    comet_client.channel_name = "generic-4-abcdef1234567890"

    # Configure mock_initialize to raise PlurkCometError on each call
    # This will simulate initialize failing during retries
    mock_initialize_side_effect = [PlurkCometError("Initialization failed")] * comet_client.max_retries

    with (
        patch.object(comet_client.session, "get") as mock_get,
        patch.object(
            comet_client, "initialize", new=AsyncMock(side_effect=mock_initialize_side_effect)
        ) as mock_initialize,
        patch("asyncio.sleep", new=AsyncMock()),  # Mock sleep to speed up tests
    ):
        # Configure mock_get to raise ClientError on the first attempt
        mock_get.return_value.__aenter__.side_effect = aiohttp.ClientError("Connection failed")
        mock_get.return_value.__aexit__.return_value = None

        with pytest.raises(PlurkCometError, match="Failed to reconnect after multiple attempts."):
            async for _ in comet_client.connect():
                pass

        assert mock_initialize.call_count == comet_client.max_retries


@pytest.mark.asyncio
async def test_connect_handles_no_data(comet_client):
    comet_client.comet_server = "https://comet03.plurk.com/comet/123456789/"
    comet_client.channel_name = "generic-4-abcdef1234567890"

    mock_response = {"new_offset": -1}

    with patch.object(comet_client.session, "get") as mock_get:
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.text.return_value = f"CometChannel.scriptCallback({json.dumps(mock_response)});"
        mock_response_obj.__aenter__.return_value = mock_response_obj
        mock_response_obj.__aexit__.return_value = None
        mock_get.return_value = mock_response_obj
        with pytest.raises(PlurkCometError, match="Failed to re-initialize after offset error and multiple attempts."):
            async for _ in comet_client.connect():
                pass


@pytest.mark.asyncio
async def test_connect_retries_on_offset_value_error(comet_client):
    comet_client.comet_server = "https://comet03.plurk.com/comet/123456789/"
    comet_client.channel_name = "generic-4-abcdef1234567890"

    # Prepare a response with offset < 0 to trigger OffsetValueError
    mock_response = {"new_offset": -2, "data": []}

    with (
        patch.object(comet_client.session, "get") as mock_get,
        patch.object(comet_client, "initialize", new=AsyncMock()) as mock_initialize,
        patch("asyncio.sleep", new=AsyncMock()),  # Mock sleep to speed up tests
    ):
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.text.return_value = f"CometChannel.scriptCallback({json.dumps(mock_response)});"
        mock_response_obj.__aenter__.return_value = mock_response_obj
        mock_response_obj.__aexit__.return_value = None
        mock_get.return_value = mock_response_obj

        with pytest.raises(PlurkCometError, match="Received invalid offset after multiple attempts."):
            async for _ in comet_client.connect():
                pass

        assert mock_initialize.call_count == comet_client.max_retries - 1


@pytest.mark.asyncio
async def test_connect_handles_invalid_offset(comet_client):
    comet_client.comet_server = "https://comet03.plurk.com/comet/123456789/"
    comet_client.channel_name = "generic-4-abcdef1234567890"

    mock_response = {"new_offset": -3}

    with (
        patch.object(comet_client.session, "get") as mock_get,
        patch.object(comet_client, "initialize", new=AsyncMock()) as _mock_initialize,
    ):
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.text.return_value = f"CometChannel.scriptCallback({json.dumps(mock_response)});"
        mock_response_obj.__aenter__.return_value = mock_response_obj
        mock_response_obj.__aexit__.return_value = None
        mock_get.return_value = mock_response_obj
        with pytest.raises(PlurkCometError, match="Received invalid offset after multiple attempts."):
            async for _ in comet_client.connect():
                pass


@pytest.mark.asyncio
async def test_build_comet_url(comet_client):
    comet_client.comet_server = "https://comet03.plurk.com/comet/123456789/"
    comet_client.channel_name = "generic-4-abcdef1234567890"
    comet_client.offset = 10

    expected_url = "https://comet03.plurk.com/comet/123456789/&channel=generic-4-abcdef1234567890&offset=10"
    assert comet_client._build_comet_url() == expected_url
