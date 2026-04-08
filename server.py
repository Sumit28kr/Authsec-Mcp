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
SUPPORTED_CLIENT_TYPES = {
    "mcp_server": "MCP Server",
    "ai_agent": "AI Agent",
    "claw_bot": "Claw Bot",
}


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


def api_create_client(
    name: str,
    client_type: str,
    platform: str = "",
    selectors: dict | None = None,
    redirect_url: str = "",
):
    if client_type not in SUPPORTED_CLIENT_TYPES:
        raise ValueError(
            f"Unsupported client_type '{client_type}'."
        )

    url = f"{BASE_URL}/clientms/tenants/{TENANT_ID}/clients/create"
    if client_type == "mcp_server":
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
    elif client_type == "ai_agent":
        if not platform:
            raise ValueError(
                "platform is required for ai_agent. Supported platforms are docker, kubernetes, and unix."
            )
        if platform not in ("docker", "kubernetes", "unix"):
            raise ValueError(
                f"Platform '{platform}' is not implemented yet for ai_agent. "
                "Supported platforms today are docker, kubernetes, and unix."
            )
        if not isinstance(selectors, dict) or not selectors:
            raise ValueError(
                "selectors are required for ai_agent. "
                "Provide platform-specific selector key/value pairs."
            )
        payload = {
            "name": name,
            "email": USER_EMAIL,
            "client_type": "ai_agent",
            "agent_type": "mcp-agent",
            "platform": platform,
            "selectors": selectors,
        }
    elif client_type == "claw_bot":
        payload = {
            "name": name,
            "email": USER_EMAIL,
            "agent_type": "claw_auth",
            "client_type": "claw_auth",
            "platform": "",
            "platform_config": {"namespace": "", "service_account": ""},
            "project_id": "00000000-0000-0000-0000-000000000000",
            "react_app_url": APP_DOMAIN,
            "redirect_url": redirect_url,
        }
    else:
        raise ValueError(f"Client type '{client_type}' is not implemented yet.")

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


def api_get_resources():
    url = f"{BASE_URL}/uflow/admin/permissions/resources"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_create_permission(resource: str, action: str):
    url = f"{BASE_URL}/uflow/admin/permissions"
    payload = {
        "resource": resource,
        "action": action,
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


def api_get_admin_role_bindings():
    url = f"{BASE_URL}/uflow/admin/bindings"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_roles():
    url = f"{BASE_URL}/uflow/admin/roles/{TENANT_ID}"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_create_role(name: str, permission_ids: list[str]):
    url = f"{BASE_URL}/uflow/admin/roles"
    payload = {
        "tenant_id": TENANT_ID,
        "client_id": "80e67968-2e4f-48e5-939c-db88bdd0e78e",
        "name": name,
        "permission_ids": permission_ids,
        "project_id": "00000000-0000-0000-0000-000000000000",
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_create_scope(scope_name: str, resources: list[str]):
    url = f"{BASE_URL}/uflow/admin/scopes"
    payload = {
        "scope_name": scope_name,
        "resources": resources,
        "tenant_id": TENANT_ID,
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_assign_role(user_id: str, role_id: str, scope_type: str, client_id: str, conditions: dict | None = None):
    url = f"{BASE_URL}/uflow/admin/bindings"
    payload = {
        "user_id": user_id,
        "client_id": client_id,
        "project_id": "00000000-0000-0000-0000-000000000000",
        "role_id": role_id,
        "scope": {
            "id": "*",
            "type": scope_type,
        },
        "tenant_id": TENANT_ID,
        "conditions": conditions or {},
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_scopes():
    url = f"{BASE_URL}/uflow/admin/scopes/mappings"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_assign_user_role(user_id: str, role_id: str, scope_type: str, client_id: str, conditions: dict | None = None):
    url = f"{BASE_URL}/uflow/user/rbac/bindings"
    payload = {
        "user_id": user_id,
        "client_id": client_id,
        "project_id": "00000000-0000-0000-0000-000000000000",
        "role_id": role_id,
        "scope": {
            "id": "*",
            "type": scope_type,
        },
        "tenant_id": TENANT_ID,
        "conditions": conditions or {},
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_user_scopes():
    url = f"{BASE_URL}/uflow/user/scopes/mappings"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_user_permissions():
    url = f"{BASE_URL}/uflow/user/rbac/permissions"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_user_role_bindings():
    url = f"{BASE_URL}/uflow/user/rbac/bindings"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_get_user_resources():
    url = f"{BASE_URL}/uflow/user/rbac/permissions/resources?tenant_id={TENANT_ID}"
    log(f"[authsec] GET {url}")
    response = httpx.get(url, headers=auth_headers(), timeout=15)
    log(f"[authsec] status: {response.status_code}")
    log(f"[authsec] response: {response.text}")
    return response.status_code, response.json()


def api_create_user_permission(resource: str, action: str):
    url = f"{BASE_URL}/uflow/user/rbac/permissions"
    payload = {
        "resource": resource,
        "action": action,
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


def api_create_user_scope(scope_name: str, resources: list[str]):
    url = f"{BASE_URL}/uflow/user/scopes"
    payload = {
        "scope_name": scope_name,
        "resources": resources,
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


def api_create_user_role(name: str, permission_ids: list[str]):
    url = f"{BASE_URL}/uflow/user/rbac/roles"
    payload = {
        "tenant_id": TENANT_ID,
        "client_id": "80e67968-2e4f-48e5-939c-db88bdd0e78e",
        "name": name,
        "permission_ids": permission_ids,
        "project_id": "00000000-0000-0000-0000-000000000000",
    }
    log(f"[authsec] POST {url}")
    log(f"[authsec] payload: {json.dumps(payload)}")
    response = httpx.post(url, json=payload, headers=auth_headers(), timeout=15)
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
            name="get_resources",
            description="Get resources from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="create_permission",
            description="Create a permission in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "Resource name for the permission, for example clients or testing",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action name, for example read, create, update, delete, manage",
                    },
                },
                "required": ["resource", "action"],
            },
        ),
        types.Tool(
            name="get_roles",
            description="Get roles from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="list_admin_role_bindings",
            description="List admin RBAC role bindings from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="create_role",
            description="Create a role in the AuthSec dashboard and map permissions to it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Role name, for example tester or admin-auditor",
                    },
                    "permission_ids": {
                        "type": "array",
                        "description": "List of AuthSec permission ids to attach to the role",
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": ["name", "permission_ids"],
            },
        ),
        types.Tool(
            name="create_scope",
            description="Create a scope in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope_name": {
                        "type": "string",
                        "description": "Name of the scope to create",
                    },
                    "resources": {
                        "type": "array",
                        "description": "List of resources to include in the scope",
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": ["scope_name", "resources"],
            },
        ),
        types.Tool(
            name="assign_role",
            description="Assign a role to a user with a scope binding in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The AuthSec user id to bind the role to",
                    },
                    "role_id": {
                        "type": "string",
                        "description": "The AuthSec role id to assign",
                    },
                    "scope_type": {
                        "type": "string",
                        "description": "Scope type name, for example demo-scope",
                    },
                    "client_id": {
                        "type": "string",
                        "description": "The AuthSec client id associated with the user",
                    },
                    "conditions": {
                        "type": "object",
                        "description": "Optional conditions JSON for the binding. Leave empty to send empty conditions.",
                    },
                },
                "required": ["user_id", "role_id", "scope_type", "client_id"],
            },
        ),
        types.Tool(
            name="create_binding",
            description="Create a role binding in the AuthSec dashboard. Use binding_type 'admin' for admin RBAC bindings or 'user' for end-user RBAC bindings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "binding_type": {
                        "type": "string",
                        "description": "Type of binding to create: admin or user",
                        "enum": ["admin", "user"],
                    },
                    "user_id": {
                        "type": "string",
                        "description": "The AuthSec user id to bind the role to",
                    },
                    "role_id": {
                        "type": "string",
                        "description": "The AuthSec role id to assign",
                    },
                    "scope_type": {
                        "type": "string",
                        "description": "Scope type name, for example demo-scope or kk",
                    },
                    "client_id": {
                        "type": "string",
                        "description": "The AuthSec client id associated with the user",
                    },
                    "conditions": {
                        "type": "object",
                        "description": "Optional conditions JSON for the binding. Leave empty to send empty conditions.",
                    },
                },
                "required": ["binding_type", "user_id", "role_id", "scope_type", "client_id"],
            },
        ),
        types.Tool(
            name="get_scopes",
            description="Get scopes from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="assign_user_role",
            description="Assign an end-user role to a user with a scope binding in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The AuthSec end-user id to bind the role to",
                    },
                    "role_id": {
                        "type": "string",
                        "description": "The AuthSec end-user role id to assign",
                    },
                    "scope_type": {
                        "type": "string",
                        "description": "End-user scope type name, for example kk",
                    },
                    "client_id": {
                        "type": "string",
                        "description": "The AuthSec client id associated with the end user",
                    },
                    "conditions": {
                        "type": "object",
                        "description": "Optional conditions JSON for the binding. Leave empty to send empty conditions.",
                    },
                },
                "required": ["user_id", "role_id", "scope_type", "client_id"],
            },
        ),
        types.Tool(
            name="list_user_scopes",
            description="List end-user RBAC scope mappings from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="list_user_permissions",
            description="List end-user RBAC permissions from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="list_user_role_bindings",
            description="List end-user RBAC role bindings from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="list_user_resources",
            description="List end-user RBAC resources from the AuthSec dashboard tenant.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="create_user_permission",
            description="Create an end-user RBAC permission in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource": {
                        "type": "string",
                        "description": "Resource name for the end-user permission",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action name, for example read, create, update, delete, manage",
                    },
                },
                "required": ["resource", "action"],
            },
        ),
        types.Tool(
            name="create_user_scope",
            description="Create an end-user RBAC scope in the AuthSec dashboard.",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope_name": {
                        "type": "string",
                        "description": "Name of the end-user scope to create",
                    },
                    "resources": {
                        "type": "array",
                        "description": "List of resources to include in the end-user scope",
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": ["scope_name", "resources"],
            },
        ),
        types.Tool(
            name="create_user_role",
            description="Create an end-user RBAC role in the AuthSec dashboard and map permissions to it.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "End-user role name, for example worker or premium-user",
                    },
                    "permission_ids": {
                        "type": "array",
                        "description": "List of end-user permission ids to attach to the role",
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": ["name", "permission_ids"],
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
            description="Onboard a new client in the AuthSec dashboard. Always ask in this order when details are missing: 1. client_type (choose MCP Server, AI Agent, or Claw Bot), 2. auth_method (choose basic_auth, oidc, or saml), 3. name, 4. type-specific fields. For ai_agent, ask for platform and then selectors. For claw_bot, ask whether the user wants to provide an optional redirect_url before creating it. If auth_method is oidc or saml, note that advanced auth setup is a follow-up step after client creation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_type": {
                        "type": "string",
                        "description": "Ask this first. Type of client to onboard. Use one of: mcp_server, ai_agent, claw_bot",
                        "enum": ["mcp_server", "ai_agent", "claw_bot"],
                    },
                    "auth_method": {
                        "type": "string",
                        "description": "Ask this second, after client_type is known. Authentication method to prepare for: basic_auth, oidc, or saml",
                        "enum": ["basic_auth", "oidc", "saml"],
                    },
                    "name": {
                        "type": "string",
                        "description": "Ask this third, after client_type and auth_method are known. Name of the client to create",
                    },
                    "platform": {
                        "type": "string",
                        "description": "Ask this only after client_type is ai_agent. Platform for ai_agent. Use one of: docker, kubernetes, unix. Omit for mcp_server and claw_bot.",
                        "enum": ["docker", "kubernetes", "unix"],
                    },
                    "selectors": {
                        "type": "object",
                        "description": "Ask this only after client_type is ai_agent and platform is known. Platform-specific selector key/value pairs for ai_agent. For docker use keys like docker:label:app, docker:image-id, docker:container-id. For kubernetes use keys like k8s:ns and k8s:sa. For unix use keys like unix:uid.",
                    },
                    "redirect_url": {
                        "type": "string",
                        "description": "Ask this only after client_type is claw_bot. Optional redirect URL for claw_bot onboarding. Before creating a claw_bot client, ask the user whether they want to provide this URL.",
                    }
                },
                "required": ["client_type", "auth_method", "name"],
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

    if name == "get_resources":
        try:
            status_code, result = api_get_resources()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "create_permission":
        resource = arguments.get("resource", "").strip()
        action = arguments.get("action", "").strip()
        if not resource or not action:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "resource and action are required."
            }))]
        try:
            status_code, result = api_create_permission(resource, action)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "status_code": status_code,
                    "permission_id": result.get("id"),
                    "full_string": result.get("full_string"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
            }))]

    if name == "get_roles":
        try:
            status_code, result = api_get_roles()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "list_admin_role_bindings":
        try:
            status_code, result = api_get_admin_role_bindings()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "create_role":
        role_name = arguments.get("name", "").strip()
        permission_ids = arguments.get("permission_ids", [])
        if not role_name or not isinstance(permission_ids, list) or not permission_ids:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "name and a non-empty permission_ids array are required."
            }))]
        try:
            status_code, result = api_create_role(role_name, permission_ids)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "status_code": status_code,
                    "role_id": result.get("id"),
                    "name": result.get("name", role_name),
                    "permissions_count": result.get("permissions_count"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
            }))]

    if name == "create_scope":
        scope_name = arguments.get("scope_name", "").strip()
        resources = arguments.get("resources", [])
        if not scope_name or not isinstance(resources, list) or not resources:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "scope_name and a non-empty resources array are required."
            }))]
        try:
            status_code, result = api_create_scope(scope_name, resources)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "status_code": status_code,
                    "scope_name": scope_name,
                    "resources": resources,
                    "message": result.get("message", "Scope created successfully"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
            }))]

    if name == "assign_role":
        user_id = arguments.get("user_id", "").strip()
        role_id = arguments.get("role_id", "").strip()
        scope_type = arguments.get("scope_type", "").strip()
        client_id = arguments.get("client_id", "").strip()
        conditions = arguments.get("conditions")
        if not user_id or not role_id or not scope_type or not client_id:
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "error": "user_id, role_id, scope_type, and client_id are required."
            }))]
        try:
            status_code, result = api_assign_role(user_id, role_id, scope_type, client_id, conditions)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "assigned": True,
                    "status_code": status_code,
                    "binding_id": result.get("id"),
                    "status": result.get("status"),
                    "role_name": result.get("role_name"),
                    "scope_description": result.get("scope_description"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False, "error": str(e)
            }))]

    if name == "create_binding":
        binding_type = arguments.get("binding_type", "").strip().lower()
        user_id = arguments.get("user_id", "").strip()
        role_id = arguments.get("role_id", "").strip()
        scope_type = arguments.get("scope_type", "").strip()
        client_id = arguments.get("client_id", "").strip()
        conditions = arguments.get("conditions")
        if binding_type not in ("admin", "user"):
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "error": "binding_type must be either 'admin' or 'user'."
            }))]
        if not user_id or not role_id or not scope_type or not client_id:
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "error": "binding_type, user_id, role_id, scope_type, and client_id are required."
            }))]
        try:
            if binding_type == "admin":
                status_code, result = api_assign_role(user_id, role_id, scope_type, client_id, conditions)
            else:
                status_code, result = api_assign_user_role(user_id, role_id, scope_type, client_id, conditions)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "assigned": True,
                    "binding_type": binding_type,
                    "status_code": status_code,
                    "binding_id": result.get("id"),
                    "status": result.get("status"),
                    "role_name": result.get("role_name"),
                    "scope_description": result.get("scope_description"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "binding_type": binding_type,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False, "error": str(e)
            }))]

    if name == "get_scopes":
        try:
            status_code, result = api_get_scopes()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "assign_user_role":
        user_id = arguments.get("user_id", "").strip()
        role_id = arguments.get("role_id", "").strip()
        scope_type = arguments.get("scope_type", "").strip()
        client_id = arguments.get("client_id", "").strip()
        conditions = arguments.get("conditions")
        if not user_id or not role_id or not scope_type or not client_id:
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "error": "user_id, role_id, scope_type, and client_id are required."
            }))]
        try:
            status_code, result = api_assign_user_role(user_id, role_id, scope_type, client_id, conditions)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "assigned": True,
                    "status_code": status_code,
                    "binding_id": result.get("id"),
                    "status": result.get("status"),
                    "role_name": result.get("role_name"),
                    "scope_description": result.get("scope_description"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "assigned": False, "error": str(e)
            }))]

    if name == "list_user_scopes":
        try:
            status_code, result = api_get_user_scopes()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "list_user_permissions":
        try:
            status_code, result = api_get_user_permissions()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "list_user_role_bindings":
        try:
            status_code, result = api_get_user_role_bindings()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "list_user_resources":
        try:
            status_code, result = api_get_user_resources()
            return [types.TextContent(type="text", text=json.dumps({
                "ok": status_code == 200,
                "status_code": status_code,
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "ok": False, "error": str(e)
            }))]

    if name == "create_user_permission":
        resource = arguments.get("resource", "").strip()
        action = arguments.get("action", "").strip()
        if not resource or not action:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "resource and action are required."
            }))]
        try:
            status_code, result = api_create_user_permission(resource, action)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "status_code": status_code,
                    "permission_id": result.get("id"),
                    "full_string": result.get("full_string"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
            }))]

    if name == "create_user_scope":
        scope_name = arguments.get("scope_name", "").strip()
        resources = arguments.get("resources", [])
        if not scope_name or not isinstance(resources, list) or not resources:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "scope_name and a non-empty resources array are required."
            }))]
        try:
            status_code, result = api_create_user_scope(scope_name, resources)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "status_code": status_code,
                    "scope_name": scope_name,
                    "resources": resources,
                    "message": result.get("message", "Scope created successfully"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
            }))]

    if name == "create_user_role":
        role_name = arguments.get("name", "").strip()
        permission_ids = arguments.get("permission_ids", [])
        if not role_name or not isinstance(permission_ids, list) or not permission_ids:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "name and a non-empty permission_ids array are required."
            }))]
        try:
            status_code, result = api_create_user_role(role_name, permission_ids)
            if status_code in (200, 201):
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "status_code": status_code,
                    "role_id": result.get("id"),
                    "name": result.get("name", role_name),
                    "permissions_count": result.get("permissions_count"),
                    "result": result,
                }))]
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "status_code": status_code,
                "error": result.get("message") or result.get("error") or str(result),
                "result": result,
            }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": str(e)
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
        client_type = arguments.get("client_type", "").strip().lower()
        auth_method = arguments.get("auth_method", "").strip().lower()
        platform = arguments.get("platform", "").strip().lower()
        selectors = arguments.get("selectors")
        redirect_url = arguments.get("redirect_url", "").strip()
        if not client_name:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False, "error": "Client name is required."
            }))]
        if auth_method not in ("basic_auth", "oidc", "saml"):
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "auth_method is required and must be one of: basic_auth, oidc, saml.",
            }))]
        if not client_type:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "client_type is required.",
                "available_client_types": SUPPORTED_CLIENT_TYPES,
            }))]
        if client_type not in SUPPORTED_CLIENT_TYPES:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": f"Unsupported client_type '{client_type}'.",
                "available_client_types": SUPPORTED_CLIENT_TYPES,
            }))]
        if client_type == "ai_agent" and not platform:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "platform is required for ai_agent.",
                "available_platforms": ["docker", "kubernetes", "unix"],
            }))]
        if client_type == "ai_agent" and (not isinstance(selectors, dict) or not selectors):
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": "selectors are required for ai_agent.",
                "docker_selector_keys": ["docker:label:app", "docker:image-id", "docker:container-id"],
                "kubernetes_selector_keys": ["k8s:ns", "k8s:sa"],
                "unix_selector_keys": ["unix:uid"],
            }))]
        try:
            status_code, result = api_create_client(
                client_name,
                client_type,
                platform,
                selectors,
                redirect_url,
            )
            if status_code in (200, 201):
                follow_up = None
                if auth_method in ("oidc", "saml"):
                    follow_up = (
                        f"Client created for auth_method '{auth_method}'. "
                        f"The next step is to configure {auth_method.upper()} settings for this client."
                    )
                return [types.TextContent(type="text", text=json.dumps({
                    "created": True,
                    "client_id": result.get("client_id") or result.get("id"),
                    "name": result.get("name", client_name),
                    "client_type": client_type,
                    "auth_method": auth_method,
                    "platform": platform or None,
                    "redirect_url": redirect_url or None,
                    "message": result.get("message", "Client registered successfully"),
                    "next_step": follow_up,
                }))]
            else:
                return [types.TextContent(type="text", text=json.dumps({
                    "created": False,
                    "error": result.get("message") or result.get("error") or str(result),
                    "status_code": status_code,
                }))]
        except Exception as e:
            return [types.TextContent(type="text", text=json.dumps({
                "created": False,
                "error": str(e),
                "available_client_types": SUPPORTED_CLIENT_TYPES,
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
