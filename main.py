import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint
from typing import Tuple
from urllib.parse import urlencode

import jwt
from aiocometd.typing import JsonDumper, JsonLoader, JsonObject
from aiosfstream import Client
from aiosfstream.auth import AuthenticatorBase
from aiohttp import ClientSession


class PrivateKeyAuth(AuthenticatorBase):
    def __init__(
        self,
        client_id: str,
        audience: str,
        username: str,
        private_key_path: Path,
        sandbox: bool = False,
        json_dumps: JsonDumper = json.dumps,
        json_loads: JsonLoader = json.loads,
    ) -> None:
        super().__init__(sandbox, json_dumps, json_loads)
        self.client_id = client_id
        self.audience = audience
        self.username = username
        self.private_key_path = private_key_path

    async def _authenticate(self) -> Tuple[int, JsonObject]:
        # This uses JTW flow
        async with ClientSession(json_serialize=self.json_dumps) as session:
            payload = {
                "iss": self.client_id,  # connected app ID
                "aud": self.audience,  # the login url (test.salesforce.com unless live)
                "sub": self.username,
                "exp": (datetime.now() + timedelta(minutes=5)).timestamp(),
            }

            with open(self.private_key_path) as f:
                pk_content = f.read()

            encode = jwt.encode(
                payload,
                pk_content,
                algorithm="RS256",
                headers={"alg": "RS256"},
            )
            req_params = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": encode,
            }
            response = await session.post(
                f"https://login.salesforce.com/services/oauth2/token?{urlencode(req_params)}"
            )
            response_data = await response.json(loads=self.json_loads)
            return response.status, response_data


async def test():
    auth = PrivateKeyAuth(
        client_id="3MVG9I9urWjeUW04M799o44usjAaDBjyen1gfdUhDSCaHllng7.7WfsJu1PePTsE2n_2iM.5KukmQaoqS7kPf",
        audience="https://test.salesforce.com",
        username="test123415@example.com",
        private_key_path=Path("sf_private_key.pem"),
    )
    async with Client(authenticator=auth) as client:
        # subscribe to topics
        await client.subscribe("/data/ChangeEvents")
        print("ready to recieve events")

        # listen for incoming messages
        async for message in client:
            topic = message["channel"]
            data = message["data"]
            print(f"{topic}")
            pprint(data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
