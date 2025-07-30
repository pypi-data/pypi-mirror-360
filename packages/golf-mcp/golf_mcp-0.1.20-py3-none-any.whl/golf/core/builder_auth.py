"""Authentication integration for the GolfMCP build process.

This module adds support for injecting authentication configuration
into the generated FastMCP application during the build process.
"""

from golf.auth import get_auth_config
from golf.auth.api_key import get_api_key_config


def generate_auth_code(
    server_name: str,
    host: str = "127.0.0.1",
    port: int = 3000,
    https: bool = False,
    opentelemetry_enabled: bool = False,
    transport: str = "streamable-http",
) -> dict:
    """Generate authentication components for the FastMCP app.

    Returns a dictionary with:
        - imports: List of import statements
        - setup_code: Auth setup code (provider configuration, etc.)
        - fastmcp_args: Dict of arguments to add to FastMCP constructor
        - has_auth: Whether auth is configured
    """
    # Check for API key configuration first
    api_key_config = get_api_key_config()
    if api_key_config:
        return generate_api_key_auth_components(
            server_name, opentelemetry_enabled, transport
        )

    # Otherwise check for OAuth configuration
    original_provider_config, required_scopes_from_config = get_auth_config()

    if not original_provider_config:
        # If no auth config, return empty components
        return {"imports": [], "setup_code": [], "fastmcp_args": {}, "has_auth": False}

    # Build auth components
    auth_imports = [
        "import os",
        "import sys  # For stderr output",
        "from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions",
        "from golf.auth.provider import ProviderConfig as GolfProviderConfigInternal # Alias to avoid conflict if user also has ProviderConfig",
        "from golf.auth.oauth import GolfOAuthProvider",
        "# get_access_token and create_callback_handler are used by generated auth_routes",
        "from golf.auth import get_access_token, create_callback_handler",
    ]

    setup_code_lines = []

    # Code to determine runtime server address configuration
    setup_code_lines.extend(
        [
            "# Determine runtime server address configuration",
            f"runtime_host = os.environ.get('HOST', {repr(host)})",
            f"runtime_port = int(os.environ.get('PORT', {repr(port)}))",
            f"runtime_protocol = 'https' if os.environ.get('HTTPS', {repr(str(https)).lower()}).lower() in ('1', 'true', 'yes') else 'http'",
            "",
            "# Determine proper issuer URL at runtime for this server instance",
            "include_port = (runtime_protocol == 'http' and runtime_port != 80) or (runtime_protocol == 'https' and runtime_port != 443)",
            "if include_port:",
            "    runtime_issuer_url = f'{runtime_protocol}://{runtime_host}:{runtime_port}'",
            "else:",
            "    runtime_issuer_url = f'{runtime_protocol}://{runtime_host}'",
            "",
        ]
    )

    # Code to load secrets from environment variables AT RUNTIME in server.py
    setup_code_lines.extend(
        [
            "# Load secrets from environment variables using names specified in pre_build.py ProviderConfig",
            f"runtime_client_id = os.environ.get({repr(original_provider_config.client_id_env_var)})",
            f"runtime_client_secret = os.environ.get({repr(original_provider_config.client_secret_env_var)})",
            f"runtime_jwt_secret = os.environ.get({repr(original_provider_config.jwt_secret_env_var)})",
            "",
            "# Check and warn if essential secrets are missing",
            "if not runtime_client_id:",
            f"    print(f\"AUTH WARNING: Environment variable '{original_provider_config.client_id_env_var}' for OAuth Client ID is not set. Authentication will likely fail.\", file=sys.stderr)",
            "if not runtime_client_secret:",
            f"    print(f\"AUTH WARNING: Environment variable '{original_provider_config.client_secret_env_var}' for OAuth Client Secret is not set. Authentication will likely fail.\", file=sys.stderr)",
            "if not runtime_jwt_secret:",
            f"    print(f\"AUTH WARNING: Environment variable '{original_provider_config.jwt_secret_env_var}' for JWT Secret is not set. Using a default insecure fallback. DO NOT USE IN PRODUCTION.\", file=sys.stderr)",
            f"    runtime_jwt_secret = {repr(f'fallback-dev-jwt-secret-for-{server_name}-!PLEASE-CHANGE-THIS!')}",  # Fixed fallback string
            "",
        ]
    )

    # Code to instantiate ProviderConfig using runtime-loaded secrets and other baked-in non-secrets
    setup_code_lines.extend(
        [
            "# Instantiate ProviderConfig with runtime-resolved secrets and other pre-configured values",
            "provider_config_instance = GolfProviderConfigInternal(",  # Use aliased import
            f"    provider={repr(original_provider_config.provider)},",
            f"    client_id_env_var={repr(original_provider_config.client_id_env_var)},",
            f"    client_secret_env_var={repr(original_provider_config.client_secret_env_var)},",
            f"    jwt_secret_env_var={repr(original_provider_config.jwt_secret_env_var)},",
            "    client_id=runtime_client_id,",
            "    client_secret=runtime_client_secret,",
            "    jwt_secret=runtime_jwt_secret,",
            f"    authorize_url={repr(original_provider_config.authorize_url)},",
            f"    token_url={repr(original_provider_config.token_url)},",
            f"    userinfo_url={repr(original_provider_config.userinfo_url)},",
            f"    jwks_uri={repr(original_provider_config.jwks_uri)},",
            f"    scopes={repr(original_provider_config.scopes)},",
            "    issuer_url=runtime_issuer_url,",
            f"    callback_path={repr(original_provider_config.callback_path)},",
            f"    token_expiration={original_provider_config.token_expiration}",
            ")",
            "",
            "auth_provider = GolfOAuthProvider(provider_config_instance)",
            "from golf.auth.helpers import _set_active_golf_oauth_provider  # Ensure helper is imported",
            "_set_active_golf_oauth_provider(auth_provider)  # Make provider instance available",
            "",
        ]
    )

    # AuthSettings creation
    setup_code_lines.extend(
        [
            "# Create auth settings for FastMCP",
            "auth_settings = AuthSettings(",
            "    issuer_url=runtime_issuer_url,",
            "    client_registration_options=ClientRegistrationOptions(",
            "        enabled=True,",
            f"        valid_scopes={repr(original_provider_config.scopes)},",
            f"        default_scopes={repr(original_provider_config.scopes)}",
            "    ),",
            f"    required_scopes={repr(required_scopes_from_config) if required_scopes_from_config else None}",
            ")",
            "",
        ]
    )

    # FastMCP constructor arguments
    fastmcp_args = {"auth_server_provider": "auth_provider", "auth": "auth_settings"}

    return {
        "imports": auth_imports,
        "setup_code": setup_code_lines,
        "fastmcp_args": fastmcp_args,
        "has_auth": True,
    }


def generate_api_key_auth_components(
    server_name: str,
    opentelemetry_enabled: bool = False,
    transport: str = "streamable-http",
) -> dict:
    """Generate authentication components for API key authentication.

    Returns a dictionary with:
        - imports: List of import statements
        - setup_code: Auth setup code (middleware setup)
        - fastmcp_args: Dict of arguments to add to FastMCP constructor
        - has_auth: Whether auth is configured
    """
    api_key_config = get_api_key_config()
    if not api_key_config:
        return {"imports": [], "setup_code": [], "fastmcp_args": {}, "has_auth": False}

    auth_imports = [
        "# API key authentication setup",
        "from golf.auth.api_key import get_api_key_config, configure_api_key",
        "from golf.auth import set_api_key",
        "from starlette.middleware.base import BaseHTTPMiddleware",
        "from starlette.requests import Request",
        "from starlette.responses import JSONResponse",
        "import os",
    ]

    setup_code_lines = [
        "# Recreate API key configuration from pre_build.py",
        "configure_api_key(",
        f"    header_name={repr(api_key_config.header_name)},",
        f"    header_prefix={repr(api_key_config.header_prefix)},",
        f"    required={repr(api_key_config.required)}",
        ")",
        "",
        "# Simplified API key middleware that validates presence",
        "class ApiKeyMiddleware(BaseHTTPMiddleware):",
        "    async def dispatch(self, request: Request, call_next):",
        "        # Debug mode from environment",
        "        debug = os.environ.get('GOLF_API_KEY_DEBUG', '').lower() == 'true'",
        "        ",
        "        # Skip auth for monitoring endpoints",
        "        path = request.url.path",
        "        if path in ['/metrics', '/health']:",
        "            return await call_next(request)",
        "        ",
        "        api_key_config = get_api_key_config()",
        "        ",
        "        if api_key_config:",
        "            # Extract API key from the configured header",
        "            header_name = api_key_config.header_name",
        "            header_prefix = api_key_config.header_prefix",
        "            ",
        "            # Case-insensitive header lookup",
        "            api_key = None",
        "            for k, v in request.headers.items():",
        "                if k.lower() == header_name.lower():",
        "                    api_key = v",
        "                    break",
        "            ",
        "            # Process the API key if found",
        "            if api_key:",
        "                # Strip prefix if configured",
        "                if header_prefix and api_key.startswith(header_prefix):",
        "                    api_key = api_key[len(header_prefix):]",
        "                ",
        "                # Store the API key in request state for tools to access",
        "                request.state.api_key = api_key",
        "                ",
        "                # Also store in context variable for tools",
        "                set_api_key(api_key)",
        "            ",
        "            # Check if API key is required but missing",
        "            if api_key_config.required and not api_key:",
        "                return JSONResponse(",
        "                    {'error': 'unauthorized', 'detail': f'Missing required {header_name} header'},",
        "                    status_code=401,",
        "                    headers={'WWW-Authenticate': f'{header_name} realm=\"MCP Server\"'}",
        "                )",
        "        ",
        "        # Continue with the request",
        "        return await call_next(request)",
        "",
    ]

    # API key auth is handled via middleware, not FastMCP constructor args
    fastmcp_args = {}

    return {
        "imports": auth_imports,
        "setup_code": setup_code_lines,
        "fastmcp_args": fastmcp_args,
        "has_auth": True,
    }


def generate_auth_routes() -> str:
    """Generate code for OAuth routes in the FastMCP app.
    These routes are added to the FastMCP instance (`mcp`) created by `generate_auth_code`.
    """
    # API key auth doesn't need special routes
    api_key_config = get_api_key_config()
    if api_key_config:
        return ""

    provider_config, _ = get_auth_config()  # Used to check if auth is enabled generally
    if not provider_config:
        return ""

    auth_routes_list = [
        "",
        "# Auth-specific routes, using the 'auth_provider' instance defined in the auth setup code",
        "@mcp.custom_route('/auth/callback', methods=['GET'])",
        "async def oauth_callback(request):",
        "    # create_callback_handler is imported in the auth setup code block",
        "    handler = create_callback_handler(auth_provider)",
        "    return await handler(request)",
        "",
        "@mcp.custom_route('/login', methods=['GET'])",
        "async def login(request):",
        "    from starlette.responses import RedirectResponse",
        "    import urllib.parse",
        '    default_redirect_uri = urllib.parse.quote_plus("http://localhost:5173/callback")',
        '    authorize_url = f"/mcp/auth/authorize?client_id=default&response_type=code&redirect_uri={default_redirect_uri}"',
        "    return RedirectResponse(authorize_url)",
        "",
        "@mcp.custom_route('/auth-error', methods=['GET'])",
        "async def auth_error(request):",
        "    from starlette.responses import HTMLResponse",
        "    error = request.query_params.get('error', 'unknown_error')",
        "    error_desc = request.query_params.get('error_description', 'An authentication error occurred')",
        '    html_content = f"""',
        "    <!DOCTYPE html>",
        "    <html><head><title>Authentication Error</title>",
        "    <style> body {{ font-family: system-ui, sans-serif; padding: 2rem; max-width: 600px; margin: auto; }} h1 {{ color: #c53030; }} .error-box {{ background-color: #fed7d7; border: 1px solid #f56565; border-radius: 0.25rem; padding: 1rem; margin: 1rem 0; }} .btn {{ background-color: #4299e1; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.25rem; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 1rem; }} .btn:hover {{ background-color: #2b6cb0; }} </style>",
        "    </head><body><h1>Authentication Failed</h1><div class='error-box'>",
        "    <p><strong>Error:</strong> {error}</p><p><strong>Description:</strong> {error_desc}</p></div>",
        "    <a href='/login' class='btn'>Try Again</a></body></html>\"\"\"",
        "    return HTMLResponse(content=html_content)",
        "",
    ]
    return "\n".join(auth_routes_list)
