"""
Initializes an asynchronous Devopness Client and ensures authentication.
"""

from base64 import b64decode
from dataclasses import dataclass
from typing import Literal

from devopness import DevopnessClientAsync
from devopness.client_config import get_user_agent
from devopness.models import (
    UserLogin,
)

devopness = DevopnessClientAsync(
    {
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": get_user_agent(
                product_name="devopness-mcp-server",
                product_package_name="devopness-mcp-server",
            ),
        },
    }
)


@dataclass
class DevopnessCredentials:
    type: Literal["email_password"]
    data: str


async def ensure_authenticated(credentials: DevopnessCredentials) -> None:
    match credentials.type:
        case "email_password":
            decoded_credentials = b64decode(credentials.data).decode("utf-8")
            user_email, user_pass = decoded_credentials.split(":", 1)

            # TODO: only invoke login if not yet authenticated
            user_data = UserLogin(email=user_email, password=user_pass)
            await devopness.users.login_user(user_data)

        case _:
            raise ValueError(f"Unsupported credentials type: {credentials.type}")
