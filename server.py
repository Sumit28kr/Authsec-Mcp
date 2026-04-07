"""
AuthSec MCP Server — No SDK, pure Python
"""

import os
import sys
import json
import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
JWT_TOKEN = os.environ.get("AUTHSEC_JWT_TOKEN", "")
TENANT_ID = os.environ.get("AUTHSEC_TENANT_ID", "")
USER_EMAIL = os.environ.get("AUTHSEC_EMAIL", "")
APP_DOMAIN = os.environ.get("AUTHSEC_DOMAIN", "")
BASE_URL = os.environ.get("AUTHSEC_BASE_URL", "https://prod.api.authsec.ai")


def log(msg):
    """All debug output goes to stderr, never stdout."""
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# AuthSec API
# ---------------------------------------------------------------------------

def auth_headers():
    return {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": f"https://{APP_DOMAIN}",
        "Referer": f"https://{APP_DOMAIN}/",
        "X-Tenant-ID": TENANT_ID,
        "tenant_id": TENANT_ID,
    }


def api_create_client(name: str):
    url = f"{BASE_URL}/clientms/tenants/{TENANT_ID}/clients/create"
    payload = {
        "name": name,
        "email": USER_EMAIL,
        "agent_type": "mcp-agent",
        "client_type": "application",
        "project_id": "00000000-0000-0000-0000-000000000000",
        "platform": "",
        "platform_config": {"namespace": "", "service_account": ""},
        "react_app_url": APP_DOMAIN,
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_clients():
    url = f"{BASE_URL}/clientms/tenants/{TENANT_ID}/clients/getClients"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_delete_client(client_id: str):
    url = f"{BASE_URL}/clientms/tenants/{TENANT_ID}/clients/delete-complete"
    payload = {
        "tenant_id": TENANT_ID,
        "client_id": client_id,
        "project_id": "00000000-0000-0000-0000-000000000000",
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    try:
        body = response.json()
    except Exception:
        body = {"raw_text": response.text}
    return response.status_code, body


def api_get_admin_users():
    url = f"{BASE_URL}/uflow/admin/users/list"
    payload = {
        "page": 1,
        "limit": 10,
        "tenant_id": TENANT_ID,
        "client_id": "80e67968-2e4f-48e5-939c-db88bdd0e78e",
        "project_id": "00000000-0000-0000-0000-000000000000",
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_end_users():
    url = f"{BASE_URL}/uflow/admin/enduser/list"
    payload = {
        "page": 1,
        "limit": 10,
        "tenant_id": TENANT_ID,
        "client_id": "",
        "project_id": "00000000-0000-0000-0000-000000000000",
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_permissions():
    url = f"{BASE_URL}/uflow/admin/permissions"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

app = Server("authsec-mcp")


@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="get_admin_users",
            description="Get admin users from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_end_users",
            description="Get end users from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_permissions",
            description="Get permissions from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_clients",
            description="Get all clients from the AuthSec dashboard for the configured tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="create_client",
            description="Create a new client in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the client to create",
                    }
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="delete_client",
            description="Delete a client in the AuthSec dashboard by client id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "The AuthSec client id to delete",
                    }
                },
                "required": ["client_id"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_admin_users":
        try:
            status_code, result = api_get_admin_users()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "get_end_users":
        try:
            status_code, result = api_get_end_users()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "get_permissions":
        try:
            status_code, result = api_get_permissions()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "get_clients":
        try:
            status_code, result = api_get_clients()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "create_client":
        client_name = arguments.get("name", "").strip()
        if not client_name:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": "Client name is required."
            }))]
        try:
            status_code, result = api_create_client(client_name)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "client_id": result.get("client_id") or result.get("id"),
                    "name": result.get("name", client_name),
                    "message": result.get("message", "Client registered successfully"),
                }))]
            else:
                return [types.TextContent(type="text", text=json.dumps({
                    "created": False,
                    "error": result.get("message") or result.get("error") or str(result),
                    "status_code": status_code,
                }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
            }))]

    if name == "delete_client":
        client_id = arguments.get("client_id", "").strip()
        if not client_id:
            return [types.TextContent(type="text", text=json.dumps({
                "deleted": False, "error": "client_id is required."
            }))]
        try:
            status_code, result = api_delete_client(client_id)
            if status_code in (200, 202, 204):
                return [types.TextContent(type="text", text=json.dumps({
                    "deleted": True,
                    "client_id": client_id,
                    "status_code": status_code,
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "deleted": False,
                "client_id": client_id,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "deleted": False, "error": str(e)
            }))]

    return [types.TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio

    log("=" * 50)
    log("  AuthSec MCP Server starting...")
    log(f"  Tenant : {TENANT_ID}")
    log(f"  Email  : {USER_EMAIL}")
    log(f"  Token  : {'SET' if JWT_TOKEN else 'MISSING'}")
    log("=" * 50)

    if not JWT_TOKEN:
        log("[ERROR] AUTHSEC_JWT_TOKEN is not set in .env!")
        sys.exit(1)
    if not TENANT_ID:
        log("[ERROR] AUTHSEC_TENANT_ID is not set in .env!")
        sys.exit(1)

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    asyncio.run(main())
