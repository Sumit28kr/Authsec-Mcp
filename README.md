# AuthSec MCP Server

Pure Python MCP server for Claude Desktop that talks to AuthSec APIs using a bearer token from `.env`.

## Current scope

This project is a local `stdio` MCP prototype. It is currently focused on AuthSec management operations and prompt-driven testing through Claude Desktop.

Implemented tools:

- `get_admin_users`
- `get_end_users`
- `get_permissions`
- `get_resources`
- `get_clients`
- `create_client`
- `delete_client`

## Project files

- `server.py` - MCP server and AuthSec API tool definitions
- `requirements.txt` - Python dependencies
- `.env` - local AuthSec credentials and configuration
- `.gitignore` - ignores secrets and local Python artifacts

## Requirements

- Python 3.12 recommended
- Claude Desktop
- Valid AuthSec tenant access
- A fresh AuthSec bearer token in `.env`

## .env values

Expected variables:

```env
AUTHSEC_JWT_TOKEN=your-authsec-jwt-token
AUTHSEC_TENANT_ID=your-tenant-id
AUTHSEC_EMAIL=your-email@example.com
AUTHSEC_DOMAIN=your-subdomain.app.authsec.ai
AUTHSEC_BASE_URL=https://prod.api.authsec.ai
```

Do not commit `.env`.

## Install

```powershell
pip install -r requirements.txt
```

## Run locally

```powershell
python server.py
```

## Claude Desktop config

Example local MCP entry:

```json
{
  "mcpServers": {
    "authsec-mcp": {
      "command": "C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": [
        "C:\\Users\\HP\\OneDrive\\Desktop\\Authsec mcp\\server.py"
      ]
    }
  }
}
```

After changing `server.py`, fully restart Claude Desktop so new tools are loaded.

## Example prompts

```text
Use authsec-mcp to get clients
```

```text
Use authsec-mcp to create a client named Demo Client
```

```text
Use authsec-mcp to delete the client with id <client_id>
```

```text
Use authsec-mcp to get admin users
```

```text
Use authsec-mcp to get end users
```

```text
Use authsec-mcp to get permissions
```

```text
Use authsec-mcp to get resources
```

## Current limitations

- This is a local prototype, not a hosted protected MCP service
- It depends on a manually supplied bearer token in `.env`
- If the token expires, update `.env` and restart Claude Desktop
- Some future features will need different client payloads and feature-specific flows

## Next direction

Planned evolution is to move from individual API tools toward feature workflows such as:

- MCP auth setup
- SSO setup such as OIDC or SAML
- SDK integration into user code
- trust delegation flows
