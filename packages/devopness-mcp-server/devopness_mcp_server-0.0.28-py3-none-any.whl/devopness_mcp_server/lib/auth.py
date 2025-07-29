import os
from base64 import b64encode

from fastmcp import Context
from starlette.requests import Request

from .devopness_api import DevopnessCredentials
from .types import MCP_TRANSPORT_PROTOCOL, EnvironmentVariable


def get_credentials(ctx: Context) -> DevopnessCredentials:
    transport: MCP_TRANSPORT_PROTOCOL = os.environ.get(
        EnvironmentVariable.SERVER_TRANSPORT
    )  # type: ignore

    if transport == "stdio":
        return credentials_stdio(ctx)

    if transport == "streamable-http":
        return credentials_http_stream(ctx)

    raise ValueError(f"Unknown transport: {transport}")


def credentials_stdio(ctx: Context) -> DevopnessCredentials:
    user_email = os.environ.get("DEVOPNESS_USER_EMAIL")
    user_pass = os.environ.get("DEVOPNESS_USER_PASSWORD")

    if user_email and user_pass:
        return credentials_stdio_email_password(user_email, user_pass)

    # TODO: add support for api-token (eg: DEVOPNESS_API_TOKEN)
    #       and call `credentials_stdio_api_token(user_token)`

    raise RuntimeError(
        "ERROR: Devopness Credentials."
        "\nThe environment variables DEVOPNESS_USER_EMAIL and"
        " DEVOPNESS_USER_PASSWORD must be set."
    )


def credentials_stdio_email_password(
    user_email: str,
    user_pass: str,
) -> DevopnessCredentials:
    return DevopnessCredentials(
        type="email_password",
        data=b64encode(f"{user_email}:{user_pass}".encode()).decode("utf-8"),
    )


def credentials_http_stream(ctx: Context) -> DevopnessCredentials:
    request: Request = ctx.request_context.request  # type: ignore

    user_email = request.headers.get("Devopness-User-Email")
    user_pass = request.headers.get("Devopness-User-Password")

    if user_email and user_pass:
        return credentials_http_stream_email_password(user_email, user_pass)

    # TODO: add support for api-token (eg: Devopness-Api-Token) and
    #       call `credentials_http_stream_api_token(user_token)`

    raise RuntimeError(
        "ERROR: Devopness Credentials."
        "\nThe headers Devopness-User-Email and"
        " Devopness-User-Password must be set."
    )


def credentials_http_stream_email_password(
    user_email: str,
    user_pass: str,
) -> DevopnessCredentials:
    return DevopnessCredentials(
        type="email_password",
        data=b64encode(f"{user_email}:{user_pass}".encode()).decode("utf-8"),
    )
