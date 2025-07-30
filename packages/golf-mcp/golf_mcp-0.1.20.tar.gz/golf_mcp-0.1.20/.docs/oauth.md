Got it. I’ll explore how to design an extensible OAuth2 authentication layer for the Golf build engine that integrates cleanly with FastMCP. I’ll focus on:

* Reviewing FastMCP’s authentication and authorization mechanisms from the official spec.
* Investigating how OAuth2/OIDC is handled in FastAPI/FastMCP ecosystems.
* Identifying libraries (like Authlib) that provide generic but extensible OAuth support.
* Designing an interface pattern (e.g. via middleware or pluggable modules) that Golf can expose in a `pre_build.py` or config.

I’ll get back to you shortly with design options and implementation recommendations.


# Extensible OAuth2 Authentication Design for the Golf Framework

## Overview and Requirements

The **Golf** framework compiles Python component directories into FastMCP server apps, and we need to secure those apps with a flexible OAuth2 authentication layer. The system must meet several key requirements:

* **Global Protection:** Every request to the FastMCP server must go through authentication (e.g. via a global middleware in FastAPI/Starlette). Unauthenticated requests should be rejected (HTTP 401) or redirected to an auth flow. This ensures the entire FastMCP runtime is protected.

* **Multiple OAuth2 Providers:** The auth system should support a wide range of OAuth2 identity providers – common ones like Google and GitHub, as well as arbitrary providers (e.g. enterprise IdPs or any service supporting OAuth2/OpenID Connect). We cannot bake in logic for specific providers; instead, we need a **pluggable abstraction** that makes it easy to integrate new providers without modifying core code.

* **No Hard-Coded Providers:** Rather than hardcoding provider-specific logic, provide an abstraction or configuration layer. For example, define a generic **`OAuthProvider`** interface or config schema where each provider’s endpoints and scopes can be specified. This way, adding a new provider is as simple as providing its OAuth endpoints and credentials, not changing framework internals.

* **User Extensibility:** Golf users (developers using the framework) should be able to extend or customize authentication easily. This could be via a configuration file, hooks/decorators in code, or a special **`pre_build.py`** script that Golf runs before compiling the app. The design should expose the auth integration points so users can add providers or adjust behavior (e.g. specify required scopes, custom token validation, etc.) in their Golf project.

* **Alignment with FastMCP Spec:** We should align with the Model Context Protocol’s authorization spec and best practices (OAuth 2.1 compliance). The MCP spec suggests treating the MCP server as an OAuth2 **resource server** that leverages external authorization servers (identity providers). In practice, this means our Golf-based server will require OAuth2 tokens on incoming requests and will itself implement the necessary OAuth endpoints to obtain and validate those tokens. Notably, the spec (2025-03-26) indicates OAuth flows (like Authorization Code with PKCE) should be used for user authorization, and that MCP servers should ideally expose OAuth2 Authorization Server Metadata or known endpoints for clients. We should follow the standard endpoint patterns (e.g. `/authorize`, `/token`) or publish a `.well-known` metadata document for our server’s auth, to be client-friendly.

* **Use of FastAPI Ecosystem:** Since Golf ultimately produces a FastAPI/ASGI application (FastMCP builds on FastAPI), we can leverage existing libraries and middleware. We should consider proven libraries like **Authlib**, **HTTPX OAuth** (used by FastAPI-Users), or Starlette authentication middleware, instead of writing everything from scratch. This accelerates development and ensures robustness.

Below we design a solution that meets these requirements, with recommendations on libraries and a proposed architecture. The design will show how Golf can incorporate OAuth2 in a configurable, extensible way, including an example of adding a new provider in `pre_build.py` and notes on how this integrates into the generated `build/app.py`.

## Library Choices for OAuth2 in FastAPI

To implement OAuth2 login flows and token validation in a FastAPI-based app, a few Python libraries stand out:

* **Authlib** – A powerful OAuth2/OIDC library that integrates with Starlette/FastAPI. Authlib can handle the client-side flow for third-party providers (redirecting to provider, handling callbacks) and also provides tools for JWT validation and even building an OAuth2 authorization server. FastAPI is built on Starlette, so we can use Authlib’s Starlette integration seamlessly. For example, Authlib allows registering OAuth clients for providers and provides helper methods to redirect and fetch tokens in route handlers. It’s well-maintained and supports OAuth2 best practices (PKCE, token refreshing, etc.).

* **HTTPX OAuth (and FastAPI-Users)** – The `httpx-oauth` library (by the FastAPI-Users project) is a lightweight async OAuth2 client library. It already includes ready-made OAuth2 client classes for common providers (Google, GitHub, etc.), which reduces boilerplate. For instance, using `httpx-oauth`, you can set up a Google OAuth client in two lines of code with your client ID/secret. FastAPI-Users itself provides higher-level user management and social login integration, but if we don’t need a full user database, we can use `httpx-oauth` directly. This library is pure-async and fits well with FastAPI.

* **PyJWT or Python-JOSE** – To issue and verify our own JWTs for session tokens, we can use PyJWT or jose libraries. FastAPI-Users uses Python-JOSE under the hood for JWT encoding/decoding. Authlib also has JOSE utilities. We’ll likely generate JWTs representing the authenticated user session (so that subsequent requests can be authorized by verifying the JWT signature and claims).

**Recommendation:** Use **Authlib** for managing the third-party OAuth flows (it’s comprehensive and supports Starlette). Authlib’s Starlette integration will simplify implementing the `/login` and `/callback` routes for each provider. For issuing our own access tokens, we can either use Authlib’s JWT support or a simple PyJWT implementation. If we want a lighter alternative, `httpx-oauth` could be considered, but Authlib’s all-in-one capabilities (and support for OpenID Connect discovery, etc.) make it ideal for a wide range of providers. We will also use FastAPI/Starlette’s built-in **SessionMiddleware** (to store OAuth state during the login redirect flow) and possibly **FastAPI’s OAuth2PasswordBearer** dependency for easy extraction of `Authorization` headers on requests (though a custom middleware might be more appropriate for a global check).

## Architectural Design: Providers Abstraction and Middleware

**1. Pluggable OAuth2 Provider Abstraction:** We introduce an abstraction (class or config structure) to represent an OAuth2 provider. This could be a base class like `OAuth2ProviderConfig` with fields and methods such as:

* `name`: Identifier (e.g. `"google"`, `"github"`, `"mycompany_idp"`).
* `authorize_url` & `token_url`: The endpoints for initiating auth and exchanging tokens. For OpenID Connect providers, we might also have `userinfo_url` or rely on the ID token.
* `client_id`, `client_secret`: Credentials for our app registered with that provider.
* `scopes`: A list of scopes to request on that provider (e.g. `["openid","email","profile"]` for Google OIDC, or `["read:user"]` for GitHub). These may be configurable by the user.
* Possibly `auth_style` or grant type info (if any provider needs special handling, e.g. GitHub requires `accept: application/json` header for token requests – Authlib handles this internally).
* Optionally, a method to fetch user info or map provider profile data to a user identity.

Golf can provide a few **pre-defined provider configs** for convenience (for Google, GitHub, etc.), but these would just be data presets (URLs and scope defaults), not hardcoded logic. For example, a Google provider config would have `authorize_url="https://accounts.google.com/o/oauth2/v2/auth"`, `token_url="https://oauth2.googleapis.com/token"`, and `userinfo_url="https://openidconnect.googleapis.com/v1/userinfo"`. Similarly, GitHub’s would point to GitHub’s OAuth endpoints. Users can use these presets or define their own. This abstraction ensures new providers can be added easily: either by providing a new config in a file or instantiating a class with the appropriate URLs.

For **generic OAuth2 providers**, we can support **OpenID Connect Discovery**: if the user supplies an `issuer_url` (the base URL of the provider), the system could automatically fetch the `/.well-known/openid-configuration` to get the authorize and token endpoints (and userinfo, JWKS, etc.). This makes integration of standards-compliant IdPs easier – you just give the issuer URL. (If using the underlying MCP SDK’s auth, note that it expects an `issuer_url` in AuthSettings, which aligns with this concept of a base issuer for tokens).

**2. Global Authentication Middleware:** To protect the entire FastMCP app, we will use a **Starlette middleware** (or dependency) that intercepts requests **before** they reach any MCP tool or resource logic. This middleware will:

* Check for a valid **access token** (our “session token”) on the request. This could be provided via the HTTP `Authorization: Bearer <token>` header (common for API clients) or possibly a cookie if a web front-end sets it. We can use FastAPI’s security utilities to parse a bearer token, or just do it manually in the middleware. If no token or an invalid token is present, the middleware will block the request.

* If the request is to a public auth endpoint (like the OAuth routes we will set up: `/login/...`, `/auth/callback`, or perhaps static files), the middleware can skip the auth check for those paths. Everything else (the MCP API endpoints) requires authentication.

* If token is missing or invalid, the middleware returns a `401 Unauthorized` response. We should include the appropriate **WWW-Authenticate** header to conform to OAuth2 Bearer token spec (RFC 6750) – for example:
  `WWW-Authenticate: Bearer realm="FastMCP", error="invalid_token"` for invalid tokens, or simply `Bearer realm="FastMCP"` when no token is provided. This signals to clients that authentication is required. In an interactive scenario, the client or user agent might then initiate the OAuth flow. *(The MCP spec discussions suggest having the client trigger the flow upon 401)/*. In a browser scenario, we might even redirect to the login page on 401, but for API-first design, a 401 + header is standard.

* If a token is present and valid, the middleware **attaches the user identity and scopes** to the request context (e.g. `request.state.user = ...`). This could be a simple object containing user ID/email and their token scopes/claims. Downstream, if needed, MCP tools could access `request.state.user` to know who is calling (for audit or permission checks). This also allows enforcement of scope-based authorization: e.g. if a particular tool requires a certain scope and the token lacks it, the middleware (or a lower-level dependency) can return `403 Forbidden` (with `error="insufficient_scope"`).

We can implement this middleware by subclassing `starlette.middleware.base.BaseHTTPMiddleware` for example, which gives access to request and response. Alternatively, FastAPI’s dependency injection could be used on every route to enforce auth, but that is tedious to attach to every generated route – a middleware is cleaner for a blanket rule.

**3. OAuth2 Flow Endpoints:** The app needs routes to handle the OAuth login flow with external providers. We will set up:

* **Login Endpoint (Authorization Redirect):** For each provider, an endpoint like `/login/{provider_name}`. When an unauthenticated user (or client) hits this, we initiate the OAuth2 Authorization Code flow with that provider. In practice, this route constructs the proper URL to the provider’s authorization endpoint with required query parameters (client\_id, redirect\_uri, scopes, state, and PKCE code challenge if using PKCE). Then it responds with a redirect to that URL. Using Authlib, this is straightforward: e.g. `await oauth.google.authorize_redirect(request, redirect_uri)` will handle storing state and redirecting. The `redirect_uri` will point to our callback endpoint on the Golf server.

* **Callback Endpoint:** After the user authenticates with the provider, the provider will redirect back to our server with an auth code. We handle this at e.g. `/auth/{provider_name}` (or `/auth/callback/{provider_name}`). This route will verify the returned state, then use the auth code to request an access token from the provider’s token endpoint. Authlib again simplifies this: e.g. `token = await oauth.google.authorize_access_token(request)` will do the exchange and give us the token data. We may also retrieve the user’s profile info at this step (for OIDC, the ID token or a userinfo endpoint provides it; for others, we might use the access token to call a profile API like GitHub’s). The result is that our server now knows who the user is (e.g. their email or user ID on the provider) and has obtained credentials (access/refresh token) for that provider.

* **Issuing Our Own Token:** Instead of letting the client use the provider’s token directly, **we issue our own JWT** to represent the session. This is a crucial security design: the Golf/MCP server becomes a *resource server* that trusts the external IdP for authentication but mints its own tokens for client use. As Den Delimarsky notes, *“instead of the \[third-party] access token, we issue a ‘session token’ – a JWT designed to be consumed by the client, with no references to \[the external provider]”*. This JWT (signed with the Golf app’s secret key) will typically include claims such as the user’s identifier (maybe their email or an internal user id), the provider used, and the permitted scopes or roles. It might also include an expiration (so that users have to re-login after some time, or we use refresh flows). The external access token and refresh token are **stored server-side** (e.g. in memory or a database) associated with the user’s session – so the server can use them when it needs to act on behalf of the user (for example, if an MCP tool needs to call the Google API, it can retrieve the Google token). But the client never sees the external token, only the server’s JWT.

* **Completing the Flow (Client Perspective):** Once our server has issued a JWT, we need to deliver it to the client. There are a couple of ways:

  * If there is a browser/front-end involved, the callback endpoint could set the JWT in a secure HTTP-only cookie and then redirect the user to the application’s main page (now authenticated). Any subsequent API calls from the front-end include the cookie, and the middleware will verify the JWT.
  * If the client is a pure API client (e.g. an MCP Python client, or an AI agent), the Golf server might instead redirect to a page that displays the token or instructs the user to copy it. However, the MCP spec envisions a more standardized approach: **issuing an authorization code to the client and using a token endpoint**. In a full spec-compliant flow, our callback would not directly return the JWT to the user agent; instead it would redirect back to the **MCP client** with an intermediate code. The sequence is: our server generates a one-time auth code tied to the user session, and redirects (or responds) in a way that the MCP client receives that code (e.g. via a local server callback or a manual copy). The MCP client (which initiated the auth) then calls our **`/token` endpoint** (on the Golf server) with that code to get the actual JWT. This is essentially the OAuth2 “authorization code grant” where our Golf server is the *authorization server* for the MCP client. This two-step approach is more secure (the final token is obtained directly by the client from our server, and we can authenticate the client if needed).

  For simplicity and MVP design, we might first implement a direct return (especially if a browser UI is present). But to align with the MCP spec and support non-interactive clients, we should plan to implement the **token exchange endpoint**. This `/token` route would accept a POST with the auth code and return the JWT (and possibly a refresh token) to the client, similar to any OAuth2 authorization server. The Cloudflare Agents OAuth library demonstrates this model: the MCP server redirects the browser to itself with a code, then issues a code to the client and finally the client exchanges it for a token. Our design will accommodate adding this endpoint so that the Golf-generated app can serve a proper OAuth2 token flow for MCP clients.

* **Logout (optional):** We might also design a logout route to revoke session tokens. This could simply instruct the client to delete its token/cookie, and if needed, also revoke the third-party token (via the provider’s revocation endpoint) if the user disconnects. Revocation could be handled via the `AuthSettings.revocation_options` if using the MCP SDK’s built-ins, but we can also call the IdP’s revoke URL via Authlib or HTTPX.

**4. Mapping Scopes and Permissions:** The authentication system should integrate with FastMCP’s authorization model. In MCP, tools and resources might be protected by scopes/permissions (for example, an “admin” tool might require an “admin” scope in the token). Our design allows configuring required scopes globally and per-route:

* At server initialization, we can set a **default required scope** for all access (the MCP spec often uses a scope like `mcp.read` or a custom scope that the client must request). In fact, FastMCP’s `AuthSettings` lets you specify `required_scopes=["myscope"]` when enabling auth. If this is set, the middleware will ensure the token contains at least that scope, or else deny access with 403 (insufficient scope). For example, we might require an “mcp” scope in any token to ensure the token was specifically issued for accessing this server.

* For finer control, Golf can let developers annotate particular tools or resources with a required scope or role. For instance, a decorator like `@requires_scope("analytics")` on a tool function would signal that the JWT must carry the “analytics” scope. The middleware or a route dependency can then enforce this check before the tool executes. This is similar to how FastAPI’s `SecurityScopes` mechanism works for OAuth2 scopes. Under the hood, our JWT could include an array of scopes granted to the user. The developer can configure which scopes to request from the IdP and how they map to MCP permissions. (In many cases, a single broad scope like “user” vs “admin” might be used, or even just rely on the fact that any authenticated user has access.)

* We also ensure these scopes appear in the server’s OAuth2 metadata if applicable, so that clients know what scopes to request. In an OIDC scenario, the “scope” parameter will at least include “openid” and perhaps a custom audience/scope for our API.

**5. Integration with FastMCP (`FastMCP` class):** The FastMCP framework itself (underlying the Golf app) provides hooks for auth. When we create the FastMCP server, we can supply our provider and settings. For example, FastMCP 2.2.7+ allows an `auth_server_provider` and an `auth` (AuthSettings) parameter on initialization. In our generated `build/app.py`, after we assemble the FastAPI app and the FastMCP instance, we will likely do something like:

```python
from fastmcp import FastMCP
from mcp.server.auth import AuthSettings
# ... after setting up OAuth routes and middleware in FastAPI ...

mcp = FastMCP(
    name="MyApp",
    auth_server_provider=GolfOAuthProvider(),      # an instance implementing MCP's OAuth provider interface
    auth=AuthSettings(
        issuer_url="https://myapp.example.com",    # the base URL for our server (could be read from config)
        required_scopes=["mcp"]                    # e.g. require the "mcp" scope in tokens
        # ... other settings like token expiration, maybe public key for JWT if asymmetric, etc.
    )
)
```

The `GolfOAuthProvider` in this snippet would be a class we create that implements MCP’s `OAuthAuthorizationServerProvider` interface. This class would tie into our Authlib-based logic: essentially, it needs to define how to handle authorization requests and token requests. In practice, since we are manually managing the FastAPI routes, we might not need to implement every method of that interface – instead, our own FastAPI routes perform those tasks. However, providing this object to FastMCP might ensure the underlying MCP machinery knows auth is enabled and perhaps document the OpenAPI and .well-known endpoints. The **higher-level approach** (and what we’ll focus on) is managing the flow in FastAPI directly, which we have more control over. The key is that our design ultimately supplies FastMCP with the needed hooks so it knows an auth system is in place and can enforce token requirements on MCP operations.

## Configuration and Extensibility for Users

Golf should allow developers to enable and configure authentication without modifying the framework itself. We propose two complementary ways to expose this:

* **Declarative Configuration**: Provide a config file (e.g. `auth.config.json` or YAML) where users list the providers and basic settings. For example, a YAML might look like:

  ```yaml
  auth:
    secret_key: "!env ${AUTH_SECRET}"        # secret for JWT signing (could be env-var substitued)
    token_expiration: 3600                   # 1 hour JWT validity
    required_scopes: ["mcp"]                 # global required scope for all tokens
    providers:
      - name: google
        client_id: "YOUR_GOOGLE_OAUTH_CLIENT_ID"
        client_secret: "!env ${GOOGLE_SECRET}"
        scopes: ["openid", "email", "profile"]
        # Using a known provider key could allow auto-fill of URLs via presets
        kind: google       # indicate to use built-in Google provider settings
      - name: github
        client_id: "YOUR_GITHUB_OAUTH_CLIENT_ID"
        client_secret: "!env ${GITHUB_SECRET}"
        scopes: ["read:user"]
        authorize_url: "https://github.com/login/oauth/authorize"
        token_url: "https://github.com/login/oauth/access_token"
        user_info_url: "https://api.github.com/user"   # needed to fetch profile
  ```

  In this example, Google’s endpoints could be internally known by the framework (since `kind: google` was specified). For GitHub, we explicitly provide the URLs. The `!env` syntax suggests we allow pulling secrets from environment variables for safety. The Golf build process can read this config and use it to register the providers.

* **Programmatic Setup (`pre_build.py`)**: Users who need dynamic logic or more control can use the `pre_build.py` hook. Golf will execute `pre_build.py` before assembling the application. In this script, we can expose an API for registering providers or modifying auth settings. For example, a user might do:

  ```python
  # pre_build.py
  from golf.auth import AuthConfig, ProviderConfig, register_provider

  # Load secrets from a safe store or env:
  import os
  google_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
  google_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

  # Create a provider config for Google
  google_provider = ProviderConfig(
      name="google",
      authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
      token_url="https://oauth2.googleapis.com/token",
      user_info_url="https://openidconnect.googleapis.com/v1/userinfo",
      client_id=google_id,
      client_secret=google_secret,
      scopes=["openid", "email", "profile"]
  )
  register_provider(google_provider)

  # Optionally adjust global auth settings:
  AuthConfig.required_scopes = ["mcp"]        # ensure the "mcp" scope is required in tokens
  AuthConfig.token_expiration = 3600          # set token lifespan
  ```

  In this snippet, `golf.auth` might be a module provided by the framework where `ProviderConfig` is our data class and `register_provider` adds it to a global list that the build process will use. We adjust some AuthConfig properties for global settings. The user could similarly register more providers or even subclass a provider class if custom behavior is needed.

Using `pre_build.py` gives developers full Python power (e.g., conditional logic, reading from external sources, etc.) to configure auth. The framework can merge or override settings from the config file with those set in `pre_build.py` (with code taking precedence). This dual approach (config file for simplicity, code hook for flexibility) covers a wide range of use cases.

**Extensibility Hooks:**

* **Custom Provider Logic:** If an OAuth provider has some non-standard behavior, an advanced user might subclass an `OAuth2ProviderBase` class and override certain methods (for example, how to fetch user info, or how to construct the auth URL if extra params are needed). Our system should allow registering such custom provider classes in place of the simple config. The framework’s internal logic (likely in the code generation phase) will detect if a provider is just a config or a fully implemented class with custom handlers.

* **Event Hooks:** We can provide signals or hook functions for certain events, such as *post-login*. For instance, after a user authenticates and we have their info, we could call a user-defined hook (if provided) like `on_user_login(user_info)` which might, for example, create a local user record or log the login event. This could be configured via `pre_build.py` by assigning a function to a known hook in the AuthConfig.

* **Decorators for Authorization:** As mentioned, providing decorators like `@requires_auth` or `@requires_scope("X")` on tool functions will integrate with our auth system. Implementation-wise, these decorators can attach attributes to the function that the Golf build process reads and translates into route dependencies. For example, `@requires_auth` could mark that endpoint as needing authentication (which in our design is anyway global, but if we wanted to allow some public endpoints, such a decorator could mark which ones *specifically* need auth or not). More importantly, `@requires_scope("X")` can be recorded by Golf and enforced by adding a dependency on a `ScopeVerifier` for that route. This `ScopeVerifier` dependency would check `request.state.user` for scope “X” and raise an HTTP 403 if not present. Thus, Golf users can finely control authorization per endpoint by sprinkling these decorators, without manually writing the verification logic.

In summary, the extensibility goal is that users can **add new OAuth providers or tweak auth settings with minimal effort**. Most will use a simple config or one function call per provider. The design abstracts away the complex bits of OAuth (like constructing URLs, verifying tokens) into the framework or underlying libraries.

## Example: Adding a New OAuth Provider in `pre_build.py`

To illustrate how a developer would use this system, consider that we want to add GitHub login to our Golf app. We’ll use `pre_build.py` for this example:

```python
# pre_build.py

from golf.auth import ProviderConfig, register_provider

# Get OAuth app credentials from env or secure storage
import os
github_client_id = os.getenv("GITHUB_OAUTH_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")

# Define the GitHub OAuth2 provider configuration
github_provider = ProviderConfig(
    name="github",
    authorize_url="https://github.com/login/oauth/authorize",
    token_url="https://github.com/login/oauth/access_token",
    user_info_url="https://api.github.com/user",  # for fetching user profile
    client_id=github_client_id,
    client_secret=github_client_secret,
    scopes=["read:user"]  # Scope to request GitHub user profile access
)

# Register this provider with the Golf framework
register_provider(github_provider)

# Optionally, enforce that tokens must have a specific scope (if desired)
from golf.auth import AuthConfig
AuthConfig.required_scopes = ["mcp"]  # ensure the custom "mcp" scope is in all tokens
AuthConfig.token_expiration = 3600    # 1 hour expiry for issued JWTs
```

What happens here: we construct a `ProviderConfig` for GitHub, specifying the endpoints and our app credentials. We then call `register_provider`, which the Golf build system will use to incorporate GitHub into the auth flow. We also adjust a global setting to require the `"mcp"` scope in tokens (meaning our server will insert an `"mcp"` scope claim when issuing the JWT, and reject any token missing it). The `pre_build.py` script runs as part of `golf build`, so by the time `build/app.py` is generated, the framework knows about the GitHub provider.

**Using Multiple Providers:** If we also registered a Google provider (similar to the example earlier with `google_provider`), the system would handle both. Typically, the login UI (or client) might allow the user to choose a provider. Our design could include a generic endpoint (`/login`) that lists available providers or an HTML page with “Sign in with Google or GitHub” buttons (if a web UI is in scope). For programmatic clients, they would direct the user to the appropriate `/login/provider` URL based on desired identity source.

## Integration into the Build Process and Generated App

Once configured, the Golf framework will integrate the authentication into the final FastAPI app (often defined in `build/app.py`). The integration works as follows:

* **Session Middleware:** The build process will add `starlette.middleware.sessions.SessionMiddleware` to the FastAPI app. This is required to store OAuth state (Authlib uses the session to keep track of the `state` and PKCE verifier between the login redirect and callback). A secret key for session signing must be provided (likely derived from the Golf auth config or auto-generated). For example: `app.add_middleware(SessionMiddleware, secret_key=AuthConfig.session_secret)`.

* **Mounting FastMCP and Routing:** The FastMCP server can either be mounted onto the FastAPI app or integrated as needed. FastMCP provides an ASGI app of its own. We have two possible architectures:

  1. *FastAPI as main app:* We create a FastAPI instance as the main app, add our auth routes and middleware to it, then mount the FastMCP app under a certain path (e.g. at `/mcp` or `/` root). In this case, the auth middleware would ideally wrap the *mounted* MCP app as well. We can ensure this by adding the middleware to the main app **before** mounting the MCP router.
  2. *FastMCP as main app:* Alternatively, FastMCP may itself produce a FastAPI app internally. In that scenario, we would need to attach our routes and middleware into that. Since FastMCP 2.x allows integration with FastAPI, we can likely get the FastAPI `app` object from the `FastMCP` instance (or create FastMCP with `asgi_app=app`). A possible approach: initialize `mcp = FastMCP(...)` without running it, then do `app = mcp.build_app()` (if such a method exists) or directly manipulate `mcp.router` as a Starlette router. For our design, we can treat it similar to mounting: protect all routes either by wrapping the whole ASGI app or by making use of FastMCP’s `auth_server_provider` hook.

  In either case, **all MCP endpoints are protected**. If a request hits a mounted MCP route, the auth middleware will check the token first. If invalid, the request won’t proceed to the MCP handler.

* **Adding OAuth Routes:** The build process will iterate through the registered providers and create the `/login/{name}` and `/auth/{name}` routes on the FastAPI app. It will use the provider configs to know what to do. For example, pseudo-code in `build/app.py` might look like:

  ```python
  for provider in AuthConfig.providers:
      @app.get(f"/login/{provider.name}")
      async def oauth_login(request: Request, prov=provider):
          redirect_uri = request.url_for(f"auth_{prov.name}")  # URL for the callback
          return await oauth_client.authorize_redirect(request, redirect_uri, oauth_provider=prov)

      @app.get(f"/auth/{provider.name}", name=f"auth_{provider.name}")
      async def oauth_callback(request: Request, prov=provider):
          # Exchange code for token
          token_data = await oauth_client.authorize_access_token(request, oauth_provider=prov)
          # token_data now contains access_token (and maybe ID token or user info)
          user_info = None
          if prov.user_info_url:
              user_info = await oauth_client.fetch_user_info(token_data, prov)
          # Issue our token
          session_token = create_jwt_for_user(token_data, user_info, provider=prov)
          # Option 1: Set cookie and redirect to app
          response = RedirectResponse(url="/") 
          response.set_cookie("session", session_token, httponly=True, secure=True)
          return response
          # Option 2: (for API clients) return the token in the response or as code
  ```

  Here, `oauth_client` could be an Authlib `OAuth` instance configured with all providers. Authlib allows registering providers by name (e.g. `oauth.register(name="google", client_id=..., client_secret=..., server_metadata_url=...)`). Then `oauth_client.authorize_redirect(request, redirect_uri, oauth_provider=prov)` is pseudo-code representing that we use the correct provider’s client. In Authlib, typically you’d do `await oauth.google.authorize_redirect(request, redirect_uri)` if the provider was registered as `"google"`. In our abstraction, we might manage multiple Authlib client instances or one OAuth instance with multiple providers.

  After getting the `token_data`, we retrieve user info if needed (Authlib can automatically handle OpenID Connect userinfo if the provider is OIDC-compliant, populating `token_data['userinfo']` as in the Google example). For providers like GitHub, we might manually call the user API with the token (Authlib’s `OAuth2Session` can be used for that). Then we call a helper to create our JWT (`create_jwt_for_user`). This will include any `AuthConfig.required_scopes` (e.g. `"mcp"` scope) and maybe the provider or user ID as claims.

  Finally, we decide how to return it. In a web context, setting a cookie and redirecting is user-friendly. For pure JSON API usage, we might instead respond with JSON containing the token or a short HTML page instructing the user to copy the token. The *cleanest approach for clients* is the two-step code exchange: instead of issuing the token immediately, redirect to an intermediate page that sends an auth code to the client. We can generate a random code, map it to the JWT in a server-side store, and pass that code in the redirect URL (e.g. `https://client-app/callback?code=XYZ`). The client (if it’s an MCP CLI or agent) receives the code and then calls our `/token` endpoint to trade it for the JWT. We won’t detail that code here, but the design accounts for adding it (the Cloudflare diagram shows this sequence).

* **Token Verification:** The build script will also include our **AuthMiddleware** in the app. For example:

  ```python
  app.add_middleware(AuthMiddleware, 
      secret_key=AuthConfig.jwt_secret, 
      required_scopes=AuthConfig.required_scopes)
  ```

  The `AuthMiddleware` class (provided by Golf) would on each request do something like:

  ```python
  auth_header = request.headers.get("authorization")
  token = None
  if auth_header and auth_header.lower().startswith("bearer "):
      token = auth_header[len("bearer "):]
  # (Alternatively, check cookie if present.)
  if token is None:
      return Unauthorized(response="Authentication required")
  try:
      payload = jwt_decode(token, secret_key=..., algorithms=["HS256"])  # decode JWT
  except InvalidSignature:
      return Unauthorized(response="Invalid token")
  # Check expiration, etc.
  scopes = payload.get("scp", [])
  if isinstance(required_scopes, list) and not set(required_scopes).issubset(scopes):
      return Forbidden(response="Insufficient scope")
  request.state.user = payload  # or build a user object
  ```

  This is a simplified sketch. In practice, `AuthMiddleware` would handle more (like errors, and possibly support token revocation lists). It might also support accepting *either* our JWT **or** an external token in cases where the Golf server might honor an IdP’s JWT directly. However, since our approach is to use our own tokens, we expect the client to send those.

* **FastMCP Tool Enforcement:** With the middleware attaching `request.state.user`, any MCP tool function could access it if needed via the FastAPI dependency injection (e.g. declare a parameter of type `Request` in the tool function to get the request and then the user). If we provided decorators for scopes, the build process would incorporate them as dependencies. For example, if a tool is marked `@requires_scope("admin")`, we add a `SecurityScopes` dependency that checks for “admin” in the token scopes. This could reuse FastAPI’s `OAuth2PasswordBearer` and `security.Scopes` mechanism for convenience, or a custom function.

* **OpenAPI and Documentation:** FastAPI will automatically include our auth endpoints in the generated OpenAPI schema. We should also document the security scheme for the protected endpoints. We can add an OAuth2 security scheme in the OpenAPI (e.g. type: http, scheme: bearer). If we want, we can add an authorizationUrl to the OpenAPI docs pointing to our `/login` URL (though typically OAuth2 auth flows in docs assume the API is the provider, but here we mostly have interactive flow outside Swagger). Nonetheless, marking all MCP routes with a bearer auth requirement in OpenAPI would be good (FastMCP might do this if auth\_server\_provider is set).

* **FastMCP Authorization Integration:** By aligning with FastMCP, we ensure that from the client’s perspective, this is a standard OAuth2-protected MCP server. The **Model Context Protocol spec** encourages servers to implement OAuth2.1 flows, including support for well-known endpoints and dynamic client registration. In our design, implementing the discovery document (`/.well-known/oauth-authorization-server`) is a nice-to-have: we could auto-generate a JSON listing our auth endpoints (authorize, token, scopes, issuer, etc.). This allows MCP clients to discover how to authorize with our server in a standardized way. Dynamic client registration (RFC 7591) is more advanced and usually not needed unless we expect arbitrary clients to register; since in MCP, the “client” is often an AI agent or SDK that the user is running, we might not need dynamic registration for now – the client (user’s app) can be pre-registered or treated as a public client in the flow.