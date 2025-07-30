from fastmcp import FastMCP

from devopness_mcp_server.lib.tools import register_tools

server: FastMCP = FastMCP("Devopness")

register_tools(server)
