# Developer guide to contribute to Devopness MCP Server

## Local Development

To run from source on tools such as Claude, Cursor, Visual Studio Code, Windsurf, etc

1. Find and edit the `mcp.json` file on your favorite tool
1. Add `devopness` MCP Serve as exemplified below

### Using STDIO

Connect using:

#### Cursor (~/.cursor/mcp.json)

```json
{
  "mcpServers": {
    "devopness": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/full/path/to/devopness-ai/mcp-server",
        "devopness-mcp-server",
        "--transport",
        "stdio"
      ],
      "env": {
        "DEVOPNESS_USER_EMAIL": "YOUR_DEVOPNESS_USER_EMAIL",
        "DEVOPNESS_USER_PASSWORD": "YOUR_DEVOPNESS_USER_PASSWORD"
      }
    }
  }
}
```

#### VSCode (~/.config/Code/User/settings.json)

```json
{
  "mcp": {
    "servers": {
      "devopness": {
        "command": "uv",
        "args": [
          "run",
          "--directory",
          "/full/path/to/devopness-ai/mcp-server",
          "devopness-mcp-server",
          "--transport",
          "stdio"
        ],
        "env": {
          "DEVOPNESS_USER_EMAIL": "YOUR_DEVOPNESS_USER_EMAIL",
          "DEVOPNESS_USER_PASSWORD": "YOUR_DEVOPNESS_USER_PASSWORD"
        }
      }
    }
  }
}
```

### Using HTTP server

**Run local HTTP server**:

```shell
cd "/full/path/to/devopness-ai/mcp-server"

uv run devopness-mcp-server --host localhost --port 8000
```

Then connect using:

#### Cursor

```json
{
  "mcpServers": {
    "devopness": {
      "url": "http://localhost:8000",
      "headers": {
        "Devopness-User-Email": "YOUR_DEVOPNESS_USER_EMAIL",
        "Devopness-User-Password": "YOUR_DEVOPNESS_USER_PASSWORD"
      }
    }
  }
}
```

#### VSCode

```json
{
  "mcp": {
    "servers": {
      "devopness": {
        "type": "http",
        "url": "http://localhost:8000/",
        "headers": {
          "Devopness-User-Email": "YOUR_DEVOPNESS_USER_EMAIL",
          "Devopness-User-Password": "YOUR_DEVOPNESS_USER_PASSWORD"
        }
      }
    }
  }
}
```

## Testing and Debugging

### Run with MCP Inspector

```shell
# Using FastMCP official MCP Inspector
cd "/full/path/to/devopness-ai/mcp-server/src/devopness_mcp_server"

uv run fastmcp dev main.py

# Environment variables must be set in the inspector web interface:
#   DEVOPNESS_MCP_SERVER_TRANSPORT=stdio
#   DEVOPNESS_USER_EMAIL=<YOUR_DEVOPNESS_USER_EMAIL>
#   DEVOPNESS_USER_PASSWORD=<YOUR_DEVOPNESS_USER_PASSWORD>

# Using alpic.ai MCP Inspector
cd "/full/path/to/devopness-ai/mcp-server"

npx -y @alpic-ai/grizzly uv run devopness-mcp-server --transport stdio

# Environment variables must be set in the inspector web interface:
#   DEVOPNESS_USER_EMAIL=<YOUR_DEVOPNESS_USER_EMAIL>
#   DEVOPNESS_USER_PASSWORD=<YOUR_DEVOPNESS_USER_PASSWORD>
```

### Run on Postman

Follow Postman guide to [create an MCP Request](https://learning.postman.com/docs/postman-ai-agent-builder/mcp-requests/create/)

* Choose `STDIO`
* Use the server command:

```shell
uv run --directory "/full/path/to/devopness-ai/mcp-server" devopness-mcp-server --transport stdio
```
