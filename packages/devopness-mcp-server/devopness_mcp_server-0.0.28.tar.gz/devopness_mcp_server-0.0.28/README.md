# Devopness - MCP Server

This is the source code for the Devopness MCP Server - <https://mcp.devopness.com/mcp/>

## Quick Start - Connect to Production Server

The easiest way to get started is to connect directly to our hosted MCP server.

### AI-Powered IDEs (Cursor, VSCode, Windsurf, etc.)

Add the Devopness MCP server to your IDE's configuration file:

#### Cursor (~/.cursor/mcp.json)

```json
{
  "mcpServers": {
    "devopness": {
      "url": "https://mcp.devopness.com/mcp",
      "headers": {
        "Devopness-User-Email": "YOUR_DEVOPNESS_USER_EMAIL",
        "Devopness-User-Password": "YOUR_DEVOPNESS_USER_PASSWORD"
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
        "type": "http",
        "url": "https://mcp.devopness.com/mcp/",
        "headers": {
          "Devopness-User-Email": "YOUR_DEVOPNESS_USER_EMAIL",
          "Devopness-User-Password": "YOUR_DEVOPNESS_USER_PASSWORD"
        }
      }
    }
  }
}
```

## Development & Testing

To contribute with improvements to this package, follow instructions on [CONTRIBUTING.md](CONTRIBUTING.md).
