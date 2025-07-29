import argparse
import logging
import os
from typing import cast, get_args

from devopness_mcp_server.lib.types import MCP_TRANSPORT_PROTOCOL, EnvironmentVariable
from devopness_mcp_server.server import server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def get_command_line_params() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Devopness MCP Server")

    parser.add_argument(
        "--transport",
        required=False,
        choices=list(get_args(MCP_TRANSPORT_PROTOCOL)),
        help="Communication transport protocol for the MCP Server. "
        f"Can also be set via {EnvironmentVariable.SERVER_TRANSPORT}.",
    )

    parser.add_argument(
        "--host",
        required=False,
        type=str,
        help="Network interface address for the server to bind to and listen for"
        " incoming connections. "
        f"Can also be set via {EnvironmentVariable.SERVER_HOST}.",
    )

    parser.add_argument(
        "--port",
        required=False,
        type=int,
        help="Network port number for the server to listen on for"
        " incoming connections. "
        f"Can also be set via {EnvironmentVariable.SERVER_PORT}.",
    )

    return parser.parse_args()


def run() -> None:
    params = get_command_line_params()

    transport = cast(
        MCP_TRANSPORT_PROTOCOL,
        (
            params.transport
            or os.environ.get(EnvironmentVariable.SERVER_TRANSPORT)
            or "streamable-http"
        ),
    )

    # Saving the transport in the environment variable to make the information
    # available to sub-modules.
    # This information is crucial for the functionality of the `lib.auth` module,
    # which performs different operations depending on the `transport`.
    os.environ[EnvironmentVariable.SERVER_TRANSPORT] = transport

    transport_kwargs = {}
    if transport == "streamable-http":
        host = (
            params.host
            or os.environ.get(EnvironmentVariable.SERVER_HOST)
            or "127.0.0.1"
        )

        port = (
            params.port  #
            or os.environ.get(EnvironmentVariable.SERVER_PORT)
            or 8000
        )

        transport_kwargs = {
            "host": host,
            "port": port,
        }

    logging.info(f"Starting Devopness MCP Server ({transport})...")

    # We use `transport_kwargs` to pass host and port only when using "streamable-http".
    # For "stdio", `server.run()` does not accept any extra arguments like host/port,
    # so we keep `transport_kwargs` empty to avoid breaking it.
    server.run(transport, **transport_kwargs)


if __name__ == "__main__":
    run()
