"""Example script demonstrating Plurk OAuth authentication and Comet connection.

This module shows how to:
- Obtain OAuth credentials
- Connect to Plurk's API
- Set up a Comet connection for real-time updates
"""

import asyncio
import os

from aiohttp import ClientSession

from poaurk import OAuthCred, PlurkComet, PlurkOAuth


async def knock_comet_periodically(comet: PlurkComet, interval: int = 600):
    """Periodically knock the Comet server every `interval` seconds."""
    while True:
        success = await comet.knock_comet()
        status = "successful" if success else "failed"
        print(f"Knock Comet {status}")
        await asyncio.sleep(interval)


async def main() -> None:
    """Program main entry."""
    oauth_cred = OAuthCred(os.environ["POAURK_TEST_KEY"], os.environ["POAURK_TEST_SECRET"], None, None)

    async with ClientSession() as session:
        plurk_oauth = PlurkOAuth(oauth_cred, session)

        # Step 1: Get request token
        await plurk_oauth.get_request_token()
        print(f"Request Token: {oauth_cred.token}")
        print(f"Token Secret: {oauth_cred.token_secret}")

        # Step 2: Get user input for verifier code
        verifier_code = await plurk_oauth.get_verifier()

        # Step 3: Get access token
        await plurk_oauth.get_access_token(verifier_code)
        print(f"Access Token: {oauth_cred.token}")
        print(f"Access Token Secret: {oauth_cred.token_secret}")

        # Step 4: Test request
        app_users_me = await plurk_oauth.request("/APP/Users/me")
        print(app_users_me)

        # Step 5: Test upload picture
        # response = await plurk_oauth.request("/APP/Timeline/uploadPicture", files={"image": "tests/lena.png"})
        # print(response)

        # Step 6: Test comet
        comet = PlurkComet(oauth_cred, session)
        await comet.initialize()
        asyncio.create_task(knock_comet_periodically(comet))
        async for update in comet.connect():
            print(f"Received update: {update}")


if __name__ == "__main__":
    asyncio.run(main())
