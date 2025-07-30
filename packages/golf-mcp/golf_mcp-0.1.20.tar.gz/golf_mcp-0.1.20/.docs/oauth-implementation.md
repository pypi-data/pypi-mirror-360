Great. I’ll analyze how the current Python MCP SDK implements OAuth, including:

1. The internal OAuth flow handling (authorization, token exchange, JWT generation, etc.)
2. The interfaces like `OAuthAuthorizationServerProvider` that must be implemented
3. How FastMCP uses these interfaces to secure endpoints
4. Best practices for wrapping these in your own abstractions like `GolfOAuthProvider`, and how to hook them into the Golf build process cleanly

I’ll get back to you with a detailed specification and guidance for sustainable integration into Golf.


# OAuth 2.0 Implementation in the MCP Python SDK

## OAuth 2.0 Flow in the MCP SDK

**Authorization Endpoint (`/authorize`):** The SDK’s server module implements an OAuth 2.0 authorization endpoint handling the Authorization Code flow (the primary flow supported). An `AuthorizationHandler` processes incoming authorization requests by validating the query parameters (like `client_id`, `redirect_uri`, `response_type`, `scope`, `state`, and PKCE `code_challenge`). If the request is valid, it uses the provided `OAuthAuthorizationServerProvider` to fetch client details and handle user authorization. Specifically, it calls `provider.authorize(client, params)` to initiate the authorization step. This method returns a URL – often the URL of a login/consent page. In many cases, the MCP server will act as an **OAuth Authorization Server**, possibly delegating to an external IdP. For example, the provider’s `authorize` implementation might redirect the user agent to a third-party IdP and later handle the callback. The SDK’s handler will return an HTTP redirect to whatever URL the provider supplies (sending the user to either an internal or external auth page). After the user authenticates and approves, the provider (and possibly custom callback logic) is responsible for generating an authorization code and eventually ensuring the user is redirected back to the original client’s `redirect_uri` with that code.

<small>*Error handling:*</small> The authorization handler is designed to handle errors according to RFC 6749. If any validation fails (unknown client, invalid redirect URI, missing parameters, etc.), it will produce an OAuth error response. Notably, if a valid `redirect_uri` and client are known, the handler will redirect back to the client’s `redirect_uri` with error parameters in the query (e.g. `error=invalid_request`). If the client or redirect URI can’t be determined, it returns a JSON error response to the user agent (since it cannot safely redirect). This dual response mechanism ensures the client is informed of errors when possible, while not redirecting to unknown or untrusted URLs. The SDK defines Pydantic models for the authorization request and error response to facilitate validation and formatting.

**Token Endpoint (`/token`):** The SDK also provides a token endpoint to exchange authorization codes for tokens (and refresh tokens). This endpoint expects a POST (form-encoded) with parameters like `grant_type`, and then behaves as follows for each grant type:

* **Authorization Code Grant:** For `grant_type=authorization_code`, the handler will authenticate the client (e.g. by HTTP Basic auth or `client_id` + `client_secret` if applicable) and validate the request parameters (code, `redirect_uri`, and PKCE `code_verifier` if a code challenge was used). It calls `provider.load_authorization_code(client, code)` to retrieve the stored code object, then `provider.exchange_authorization_code(client, code_obj)` to perform the exchange. The provider is responsible for checking that the code is valid (not expired or already used, matches the client, etc.) and then generating an access token (and typically a refresh token). The result of this call is an `OAuthToken` object containing the new `access_token` (and optionally a `refresh_token`) along with its metadata. The SDK then returns a JSON response to the client including at least:

  * `access_token`: the token string (often a JWT or opaque token).
  * `token_type`: “bearer”.
  * `expires_in`: token lifetime in seconds (if provided).
  * `refresh_token`: a token to obtain a new access token (if the provider issued one).
    The SDK follows the OAuth 2.0 spec for error cases: e.g. if the code is invalid or expired, it raises a `TokenError` with `error="invalid_grant"`, which the handler returns as a JSON error response. Invalid client credentials yield `error="invalid_client"`, unsupported grant types yield `error="unsupported_grant_type"`, etc., matching the RFC definitions.

* **Refresh Token Grant:** For `grant_type=refresh_token`, the token endpoint will call `provider.load_refresh_token(client, refresh_token)` to validate and retrieve the stored refresh token model, then invoke `provider.exchange_refresh_token(client, refresh_token_obj, scopes)` to rotate it. The provider should verify that the refresh token is valid and not expired/revoked, and typically issue a new access token **and** a new refresh token. The design follows best practices by **rotating refresh tokens** – i.e. replacing the old refresh token with a new one on each use. The response JSON will contain the new `access_token` and `refresh_token` (and the old refresh token should be invalidated by the provider). If the client requested a reduced scope, the provider may issue a token with a subset of scopes. Error handling is similar (e.g. unknown or invalid refresh token -> `invalid_grant`).

* **Client Credentials (future):** The initial implementation (as of v1.7.x) focused on authorization code flow (for user-driven auth) and refresh tokens. Client Credentials grant was not yet supported in v1.7.0 (there is an open request to add it). In the future, we expect `grant_type=client_credentials` to be handled by calling a provider method to directly issue an access token for server-to-server clients.

All token responses and errors are returned as JSON. The SDK uses Pydantic models for token responses and errors to ensure compliance. For instance, an `OAuthToken` model (imported from `mcp.shared.auth`) encapsulates the issued tokens so that the SDK can easily serialize it to JSON for the HTTP response.

**JWT Creation & Validation:** The MCP SDK delegates JWT creation and validation largely to the **provider implementation**. In other words, the SDK doesn’t hard-code how tokens are generated or verified; it provides the interface and some helpers, while you supply the logic (this design gives flexibility to integrate with different auth backends). Typically, an OAuth provider will issue **JWTs** for access tokens (and possibly for refresh tokens, or refresh tokens could be opaque). The `AuthSettings` configuration includes an `issuer_url` which should be the URI identifying your server (this will be the `iss` claim in tokens you issue). The provider needs to sign JWTs (usually with an RSA or EC private key, or HS secret) such that they can be verified later. The SDK’s design anticipates this by supporting JWKS and issuer configuration:

* When **issuing** tokens in `exchange_authorization_code` or `exchange_refresh_token`, the provider will create a JWT (access token) containing appropriate claims (subject, issuer, audience, scopes, expiration, etc.). This JWT is signed with the server’s key. The provider returns the token string via the `OAuthToken` object.
* When **validating** tokens on incoming requests, the SDK will call `provider.load_access_token(token_str)` to check the token. If JWTs are used, `load_access_token` should decode and verify the JWT signature and claims (e.g. using PyJWT or python-jose). If the token is valid, it returns an `AccessToken` model (which at least contains the token string, client ID, scopes, and expiration). If invalid or expired, it returns `None` (causing an auth failure). This method abstracts the verification process – whether that means checking a signature, looking up a token in a database, or calling an external introspection endpoint, it’s up to the provider. In practice, JWTs will be verified against the server’s public key, using the JWKS info (more on JWKS below). The SDK does not itself perform JWT verification; it relies on the provider to implement it in `load_access_token`.
* The SDK supports **JWKS endpoint** exposure so that external clients or services can retrieve the public keys needed to verify the JWTs. When you configure the server, you likely provide a key pair or allow it to generate one. The public key(s) are published via a JWKS (JSON Web Key Set) endpoint. The MCP spec and ecosystem assume that an MCP server acting as an auth server will make its signing keys available at a known URL for token verification. In the current SDK, this is handled by the auth router (usually at something like `/keys` or `/.well-known/jwks.json`). Clients (or other resource servers) can fetch this JWKS to validate token signatures. **Example:** If you use an external service or library to verify tokens, you’d configure it with the MCP server’s JWKS URL, and it will confirm the JWT’s signature, `iss`, `aud`, and `exp` are all valid. The `issuer_url` in `AuthSettings` is used in the token’s issuer claim and also likely tied to the discovery metadata (if any). *Note:* the exact path of the JWKS endpoint in the SDK might be `/keys` or under an OAuth discovery document; but the support is explicitly mentioned as part of OAuth support.

**User Info Retrieval:** In a full OAuth2/OpenID Connect implementation, a **UserInfo endpoint** is provided to retrieve user profile information using an access token. The MCP SDK’s OAuth support is primarily focused on the authorization and token aspects; it does not define a concrete `get_userinfo` method in the provider interface. However, it’s designed such that a developer can easily add a `/userinfo` route if needed. Typically, if the MCP server itself is the Identity Provider, one could implement an endpoint that uses `provider.load_access_token` to authenticate the token and then returns user claims (for example, user ID, name, email) as JSON. The data for this would come from wherever the provider stored the user’s info (perhaps encoded in the token or looked up via a user ID). If the MCP server is delegating to an external IdP, the UserInfo endpoint could proxy to the external provider’s userinfo. In summary, **user info retrieval** is supported in principle (the server can expose it), but it’s not a built-in fixed part of the `OAuthAuthorizationServerProvider` interface. The expectation is that the provider knows the authenticated user’s identity (e.g. from the external IdP’s ID token or from the internal auth process) and can supply user claims as needed. Many implementations will simply include user claims in the JWT access token, obviating a round-trip to a userinfo endpoint. If a separate userinfo endpoint is desired, one can be added using the validated token data. (The FastMCP documentation hints that a higher-level abstraction or guide for authentication will cover details like user info once the interface matures.)

**Revocation & Client Registration:** Rounding out the OAuth 2.0 support, the SDK includes optional support for token revocation and dynamic client registration, as configured in `AuthSettings`. If `revocation_options.enabled=True`, the server will expose a standard OAuth revocation endpoint (typically `/revoke`) that allows clients to revoke an access or refresh token. The `OAuthAuthorizationServerProvider` provides a `revoke_token()` method which the endpoint handler will call to actually invalidate the token. The expectation is that the provider will revoke both the access token and its corresponding refresh token, regardless of which one is given (to prevent reuse). If `client_registration_options.enabled=True`, the server exposes a dynamic client registration endpoint (`/register`). The provider’s `register_client(client_info)` will be invoked to save new client metadata, and `get_client` must be able to retrieve clients (the SDK’s default flow uses `get_client` for lookup on each auth request). The provider can enforce validations here – for example, only allowing certain redirect URIs or requiring specific metadata – and can throw a `RegistrationError` if the client data is invalid. These features make the MCP server’s OAuth support more complete, aligning with RFC 7591 (Dynamic Client Registration) and RFC 7009 (Token Revocation) in an optional way.

## OAuth Provider Interfaces and Base Classes

To support pluggable OAuth logic, the MCP Python SDK defines a set of interfaces and data models in **`mcp.server.auth`**. The core interface is `OAuthAuthorizationServerProvider`, which is a generic Python protocol (PEP 544) that you implement to hook into the auth system. By providing an object that implements this protocol to the server, you supply the backing logic (whether it’s checking a database, calling an external IdP, etc.). Key components include:

* **`OAuthAuthorizationServerProvider` Interface:** This is defined as a `Protocol` with generics for custom token models. Your implementation can specify concrete types for `AuthorizationCodeT`, `RefreshTokenT`, and `AccessTokenT` (which by default are Pydantic models described below). You could use the defaults or subclasses thereof if you need to store extra fields (the SDK notes you may add fields like user info to your token models since they won’t be automatically exposed externally). The required methods in this interface are all `async` methods (the server is async, built on Starlette/FastAPI):

  * **`get_client(client_id: str) -> OAuthClientInformationFull | None`:** Retrieve the client application’s details by ID. The SDK will call this during authorization and token requests to look up the client. The return type `OAuthClientInformationFull` likely includes fields such as the client’s name, allowed redirect URIs, type (public/confidential), client secret (if any), allowed scopes, etc. If you have dynamic registration off, you can raise `NotImplementedError` or simply return `None` for unknown clients. The SDK uses this to validate `client_id` and to later check redirect URIs and client secrets. (If `None` is returned, the client is treated as not found and an auth error is raised.)
  * **`register_client(client_info: OAuthClientInformationFull) -> None`:** Save a new client’s information. This is invoked when a client dynamically registers via the `/register` endpoint. You should persist the client (e.g., in a database) so that `get_client` can later retrieve it. You can validate the incoming data and raise a `RegistrationError` with an error code like `"invalid_client_metadata"` if something is wrong. If your server doesn’t support dynamic registration, you may simply not implement this (raising `NotImplementedError` causes the registration route to return an error).
  * **`authorize(client: OAuthClientInformationFull, params: AuthorizationParams) -> str`:** Handle the authorization request. The SDK calls this during the `/authorize` flow *after* it has validated basic parameters and loaded the client. The `params` (an `AuthorizationParams` model) include details like the requested scopes, the redirect URI, whether the redirect URI was explicitly provided, the `state`, and the PKCE `code_challenge`. Your implementation of `authorize` should perform the next step in the auth flow. In many cases, this means **initiating user authentication/consent**. For example, you might redirect to a login page or to an external IdP’s authorize URL. The expectation is that you return a URL as a string – the SDK will issue an HTTP redirect to that URL for you.

    * If you are handling user login *within* the MCP server, you might return a URL for an internal route (maybe something like `/login?client_id=...`). That route would not be handled by the SDK automatically – you’d need to implement it (perhaps using a custom Starlette route) to show a form or otherwise authenticate the user. After authenticating, you would generate an auth code and redirect to `params.redirect_uri` with the code. The documentation suggests that many implementations will **perform a secondary OAuth exchange with a third-party provider** – meaning the MCP server itself relies on an upstream IdP. In that case, `authorize` likely returns the external provider’s authorization URL (including a callback back to the MCP server). The SDK’s docs include an ASCII diagram showing: *Client -> MCP Server -> 3rd Party OAuth Server -> (back to) MCP Server -> Client*. In such a setup, your MCP server is effectively an OAuth **broker**. You’ll need to set up a callback endpoint on the MCP server to catch the 3rd party IdP’s response. In that callback, you’d finish the login by generating an MCP auth code and redirecting the user to the original client app’s `redirect_uri` with that code. (The SDK leaves this part to the implementer – “Implementations will need to define another handler on the MCP server \[to] perform the second redirect and generate/store an authorization code”.)
    * However you do it, by the end of the `authorize` flow, an `AuthorizationCode` must be issued. The SDK expects that when the client later hits `/token` with that code, your provider can retrieve it and validate it. The SDK’s own recommendation is that auth codes have at least 128 bits of entropy (practically, a random URL-safe string \~22+ chars). The `AuthorizationCode` model provided has fields for the code, associated client, scopes, redirect URI, code challenge, etc., which you should populate when creating a code.
  * **`load_authorization_code(client, authorization_code: str) -> AuthorizationCodeT | None`:** Look up an authorization code that was previously issued. The SDK will call this during the token exchange to get the full details of the code. You should return an object (likely an instance of your `AuthorizationCodeT` model) if it’s found and still valid, or `None` if the code is not found (which will trigger an `invalid_grant` error). This is where you’d enforce one-time use and expiration: e.g. if the code was already used or is expired, return `None`. The `client` passed in is the *authenticated client* trying to exchange the code, which you can use to ensure the code was issued to that same client (if not, you should consider it invalid).
  * **`exchange_authorization_code(client, authorization_code: AuthorizationCodeT) -> OAuthToken`:** Exchange a valid authorization code for tokens. This is called after `load_authorization_code` succeeds. Here you should create the access token and refresh token (if using refresh tokens) for the given client & code. The `OAuthToken` return value is a model that typically contains: `access_token` (str), `refresh_token` (str or None), `expires_in` or expiration timestamp, and possibly scope or token type. In the SDK, `OAuthToken` is likely a Pydantic model that will be serialized to JSON for the response. Your implementation should **persist any generated tokens** as needed (e.g., store refresh token in DB, or record the access token if you need to track it server-side). If you issue JWTs, you might not store access tokens at all, relying on verification. But refresh tokens usually need to be stored (unless you embed everything in them and can invalidate via blacklists or short TTLs). If something is wrong (e.g. the code is invalid or the client is not allowed), you can raise a `TokenError` which will result in an error response.
  * **`load_refresh_token(client, refresh_token: str) -> RefreshTokenT | None`:** Look up a refresh token string and return the corresponding model if valid. This is similar to `load_authorization_code` but for refresh tokens. You should verify the token exists, was issued to the given client, and isn’t expired or revoked. If valid, return the `RefreshToken` object; if not, return `None` (leading to an `invalid_grant` error).
  * **`exchange_refresh_token(client, refresh_token: RefreshTokenT, scopes: list[str]) -> OAuthToken`:** Exchange a refresh token for a new token pair. The SDK calls this when a client hits the token endpoint with `grant_type=refresh_token`. Your implementation should verify that the refresh token is still good (though presumably it was loaded via `load_refresh_token` already) and then generate a new `access_token` (and often a new `refresh_token`). According to the documentation, implementations **SHOULD rotate** both tokens, issuing a fresh refresh token and **invalidating the old one** to prevent reuse. You can also optionally narrow or adjust scopes: the `scopes` parameter is provided in case the client wants to reduce the scope for the new token (OAuth 2.0 allows a refresh token to request a subset of the original scope). Typically, you should ensure the new scope is not broader than the original token’s scope. The result is again an `OAuthToken` model with the new tokens.
  * **`load_access_token(token: str) -> AccessTokenT | None`:** Validate an access token presented to the resource server (which in this case is the MCP server itself). This is called whenever an incoming MCP request (for a protected tool/resource) includes an `Authorization: Bearer ...` token. Your job is to verify the token and, if valid, return an `AccessToken` model (or subclass) containing at least the token’s identity (e.g. the client or user info, scopes, expiration). If the token is invalid, expired, or revoked, return `None`. For JWTs, this is where you’d decode and verify the JWT signature, check claims like expiration and issuer, etc. The docstring refers to returning an "AuthInfo" – essentially the `AccessToken` object serves as the auth context. The SDK doesn’t send this object to the client; it’s used internally (e.g. it might be attached to the request state or context for use in the server’s logic). By implementing this, you can integrate with external verification as well (for instance, if the MCP server trusts an external issuer, it could call that issuer’s introspection endpoint or verify using that issuer’s JWKS).
  * **`revoke_token(token: AccessTokenT | RefreshTokenT) -> None`:** Revoke a token. The SDK will call this if a client hits the revocation endpoint. The `token` passed in could be either an access token or a refresh token (the spec allows either to be submitted for revocation). Your implementation should revoke **both** the access and refresh token associated with it. For example, if an access token string is given, you should find its corresponding refresh token (if any) and revoke that as well – since a refresh token could be used to get a new access token, it needs to be invalidated. Likewise, if a refresh token is provided, you’d revoke it and perhaps any cached access token. If the token is unknown or already revoked, you can simply no-op (the spec says revocation is idempotent and not revealing of token status). This might involve deleting records from your database or adding them to a revocation list.

In addition to the provider interface, the SDK defines **data models** for common OAuth objects:

* **`AuthorizationParams`:** encapsulates incoming authorize request parameters. It has fields for `state` (optional), `scopes` (requested scopes list), `code_challenge` (for PKCE, if used), `redirect_uri` (the callback URL), and a boolean `redirect_uri_provided_explicitly`. This model is used to pass sanitized data into `provider.authorize`.
* **`AuthorizationCode`:** a Pydantic model for authorization codes. Fields include the `code` (string), `client_id`, `scopes` (list), `expires_at` (timestamp), `redirect_uri`, `redirect_uri_provided_explicitly`, and the PKCE `code_challenge`. You might extend this model (via the generic type param) to include a user identifier if your auth codes are tied to user accounts. The SDK does not inherently include a user field, but you can subclass it (e.g. add `user_id`) in your own `AuthorizationCodeT`.
* **`AccessToken` and `RefreshToken`:** Pydantic models for tokens. Each has a `token` (string value), `client_id`, `scopes`, and `expires_at`. They do not by default include a `user` or `subject` field or an `issued_at`, but again you can subclass. The idea is that these represent the token as a persistent object. For JWT, you might not store the AccessToken at all – but you could still use the model to represent the decoded claims (e.g. populate it after verifying the JWT, to pass around internally). The `expires_at` is typically a UNIX timestamp or None if non-expiring.
* **`OAuthClientInformationFull`:** represents client metadata. While we don’t see the fields in the snippet, typically this would include at least `client_id`, `client_name`, `redirect_uris` (list), `grant_types` allowed, `response_types` allowed, `scopes` allowed, `client_secret` (perhaps hashed), `token_endpoint_auth_method` (like “none” for public or “client\_secret\_basic”), etc. The provider’s `get_client` and `register_client` deal in this object. The naming “Full” suggests there might be a subset (like registration input vs full stored info), but the SDK likely uses one model for simplicity. It’s reasonable to assume the SDK provides validation on redirect URIs (possibly via a method on this model, e.g. `client.validate_redirect_uri(uri)` as hinted in the commit).
* **Error types:** The SDK defines typed exceptions for OAuth errors:

  * `AuthorizeError` (with an `error` code of type `AuthorizationErrorCode` and optional description). `AuthorizationErrorCode` is a literal type of strings like `"invalid_request"`, `"unauthorized_client"`, `"access_denied"`, `"unsupported_response_type"`, etc., covering the standard error codes for the auth endpoint. If your provider raises `AuthorizeError`, the SDK’s handler will catch it and produce the appropriate error response (redirect or JSON).
  * `TokenError` (with `error` of type `TokenErrorCode`). `TokenErrorCode` covers errors like `"invalid_request"`, `"invalid_client"`, `"invalid_grant"`, `"unauthorized_client"`, `"unsupported_grant_type"`, `"invalid_scope"`. Raising this in your provider’s token handling will result in an OAuth-compliant error JSON (with HTTP 400 or 401 as appropriate).
  * `RegistrationError` for client registration issues, with codes like `"invalid_redirect_uri"`, `"invalid_client_metadata"`, etc. If `register_client` raises this, the dynamic registration endpoint will return an error response to the client.

All of these classes live in the `mcp.server.auth` package of the SDK. The **AuthSettings** class (in `mcp.server.auth.settings`) is also important – it’s not an interface but a configuration dataclass that you pass into FastMCP. It includes:

* `issuer_url` (str): the issuer URI for your server (used in tokens and metadata).
* `required_scopes` (List\[str]): a list of scopes that are required on incoming tokens to consider them authorized. (For example, you might require that every access token has a scope like “myscope” to use your API; the SDK will enforce this on requests.)
* `revocation_options` (RevocationOptions): with at least an `enabled` flag (and possibly other settings like whether to revoke on logout, etc.).
* `client_registration_options` (ClientRegistrationOptions): with an `enabled` flag and potentially `valid_scopes`, `default_scopes` lists. In the example, `valid_scopes=["myscope","myotherscope"]` and `default_scopes=["myscope"]` were set, meaning new clients can only request those scopes and will get “myscope” by default if none specified.
* Possibly other fields like token expiration times, JWKS key configuration (the SDK might generate a key pair if not provided, or there could be a field for a JWKS or PEM file – this wasn’t explicitly shown, but since JWKS is supported, AuthSettings likely knows about keys).

In summary, the SDK exposes a *protocol* (`OAuthServerProvider` a.k.a. `OAuthAuthorizationServerProvider`) that you implement, along with a suite of data models to use for OAuth entities. The methods you implement cover the full lifecycle: client lookup/registration, user authorization step, code and token issuance, token lookup/verification, and revocation. This clean separation means the SDK itself remains agnostic to how you manage users or clients – you can integrate with databases or external services by writing an appropriate provider class.

## FastMCP Integration with OAuth Interfaces

FastMCP (the high-level server class in the MCP SDK) is responsible for tying the OAuth implementation into the running web server. When you create a `FastMCP` instance, you can pass in the `auth_provider` and `auth` settings to enable OAuth. For example:

```python
mcp = FastMCP(
    "SecureApp",
    auth_provider=MyOAuthServerProvider(),
    auth=AuthSettings(
        issuer_url="https://myapp.com",
        required_scopes=["myscope"],
        revocation_options=RevocationOptions(enabled=True),
        client_registration_options=ClientRegistrationOptions(enabled=True, ...),
    ),
)
```

As shown in the documentation, providing an `auth_provider` and `AuthSettings` configures the server to use OAuth 2.0 authentication. Under the hood, FastMCP will register the necessary routes and hooks:

* It **registers the OAuth routes** (authorization, token, etc.) with the Starlette/FastAPI app that FastMCP manages. The SDK’s auth module likely includes a pre-built APIRouter or set of route handlers. When `auth_provider` is set, FastMCP includes these routes. This typically means endpoints like:

  * `GET /authorize` – handled by the AuthorizationHandler (which calls `provider.authorize` internally).
  * `POST /token` – handled by the Token handler (calls the relevant provider methods like `exchange_authorization_code`, `exchange_refresh_token`).
  * If enabled: `POST /revoke` for token revocation (calls `provider.revoke_token`), and `POST /register` for dynamic client registration (calls `provider.register_client`).
  * Possibly `GET /.well-known/jwks.json` or `/keys` for JWKS (serving keys from AuthSettings).
  * The **issuer URL** in AuthSettings might also be used to advertise metadata; e.g., the MCP server may include OAuth metadata in its MCP descriptor so that a client (like an AI agent) knows where the auth endpoints are. Indeed, current MCP clients discover the OAuth endpoints from the server’s manifest. This is why the MCP server effectively behaves as an OAuth Authorization Server in the ecosystem.
* FastMCP **passes the provider and settings** to the underlying server implementation so that the route handlers know what to call. For example, the authorization handler has access to `self.provider` (your `MyOAuthServerProvider` instance) and `self.settings` (AuthSettings) to apply things like scope requirements or issuer checks. The FastMCP docs note that at this stage the integration is somewhat low-level: FastMCP essentially plugs in your provider and does not provide a lot of abstraction on top of it yet. In other words, FastMCP’s job is mostly to **connect** the provider interface with incoming HTTP requests.

**Securing Protected Endpoints:** Once OAuth is enabled, all MCP **tools, resources, and other endpoints are protected** by default (unless explicitly marked public). The `required_scopes` setting comes into play here: FastMCP will enforce that any incoming request carrying an access token has at least these scopes. Concretely, the SDK likely uses a Starlette dependency or middleware to check auth on each request:

* For any invocation of a tool or resource (which might correspond to an HTTP endpoint or an SSE event initiation), the server looks for an `Authorization: Bearer <token>` header. If absent, it will reject the request (possibly with a 401 Unauthorized).
* If a token is provided, FastMCP calls `auth_provider.load_access_token(token)` to validate it. If this returns `None` (invalid or expired), the server responds with 401 (and possibly a JSON error or an OAuth WWW-Authenticate header indicating invalid token). If it returns an `AccessToken` object, the server then checks that the scopes in that token meet the `required_scopes` policy. If the token lacks a required scope, the server denies access (likely a 403 Forbidden, `invalid_scope` error).
* Only if the token is valid and authorized will the server allow the request to proceed to the actual tool/resource logic. In effect, every tool/resource function call is wrapped by an auth check. This is analogous to adding a `@requires_auth` decorator or FastAPI dependency globally when auth is configured.

**Attaching Auth Context:** When a request is authorized, the server may attach the auth info to the request context. FastMCP’s `Context` object (which can be injected into tool functions) could contain attributes for authentication, such as `Context.user` or `Context.scopes`. Although the SDK’s documentation hasn’t detailed this, it’s common in frameworks to store the authenticated principal in the request state. Since the `AccessTokenT` model is returned by `load_access_token`, it could carry a user identifier if you extended it. For example, if your `AccessToken` subclass has a `user_id`, you could modify the FastMCP context to include that. The SDK had a test (mentioned in the commit notes) for an "auth context", implying that the context or request state will have information about the authenticated user/token for use inside your endpoints. This would let your tool implementations know *who* is calling or with what scopes, enabling application-level authorization decisions on top of just authentication.

**Integration Points in Code:** FastMCP is built on Starlette (as indicated by imports of Starlette’s Request, Response, RedirectResponse in the auth code). It likely uses an internal FastAPI or Starlette app. When you run `mcp.run()` or similar, it serves this app. The auth integration happens during FastMCP initialization:

* If `auth_provider` is provided, FastMCP calls something like `auth_router = create_auth_router(auth_provider, auth_settings)` and includes it. This router defines the paths mentioned above and ties them to handlers which call your provider.
* FastMCP might also configure a middleware that checks auth on all requests to the MCP API endpoints. Alternatively, each route (tool/resource) might include a dependency to check auth. The exact implementation could vary, but either way the effect is that before a tool function executes, the token is verified.
* The server metadata (the JSON that describes the MCP server’s capabilities to clients) will include an `"auth_type": "oauth2"` and likely the `issuer_url` and endpoints. For example, an MCP client (like an AI assistant) when connecting to an MCP server will see in the handshake that the server requires OAuth2. It can then use the provided `issuer_url` or auth metadata to begin the OAuth flow. Some implementations treat the MCP server as both the auth *and* resource server (which is the current design), meaning the client interacts directly with the MCP server for auth. The community has discussed treating MCP servers as resource servers with third-party authorization servers instead – the current SDK leans toward the simpler combined approach.

**Example Flow in Practice:** To illustrate how FastMCP, the SDK, and your provider come together, consider an AI client (e.g. Claude or ChatGPT plugin system) connecting to your FastMCP server:

1. The client discovers your server’s auth requirements (issuer or auth endpoints) from the MCP handshake. It directs the user to your server’s `/authorize` URL (perhaps opening a browser).
2. The request hits FastMCP’s `/authorize`. FastMCP uses the `AuthorizationHandler` which calls your `provider.authorize`. Suppose your implementation returns a URL to an external IdP’s authorize page. FastMCP then sends a redirect to that URL back to the user’s browser.
3. The user authenticates with the external IdP, which redirects back to your MCP server’s predefined callback endpoint (which you have set up separately, since the SDK doesn’t do it automatically). In that callback view, you use the provider or your own logic to verify the IdP response (e.g., exchange an IdP code for tokens) and then generate an `AuthorizationCode` for the MCP client. Finally, you redirect the user’s browser to the original client’s `redirect_uri` with `code=<auth_code>&state=<state>`.
4. The AI client receives the code and calls the MCP server’s `/token` endpoint. FastMCP’s token handler authenticates the client (if needed) and calls `provider.load_authorization_code` and `provider.exchange_authorization_code`. Your provider returns an `OAuthToken` containing (for example) a signed JWT access token and a refresh token. FastMCP packages this into JSON and returns it to the client.
5. Now the AI client has an access token. When it subsequently calls any tool or resource on your MCP server, it includes `Authorization: Bearer <token>`. FastMCP receives the request, the auth middleware calls `provider.load_access_token`. You verify the JWT (e.g., check signature against your public key, etc.) and return an AccessToken model (say it contains `user_id` and scopes). The SDK sees this is valid and allows the request to proceed. The tool function executes, possibly using `Context` to get info like `ctx.user_id` if you wired that in.
6. If at any point the token is invalid (expired or tampered), `load_access_token` returns None and FastMCP will deny the request with an error. The client may then try to use its refresh token: it calls `/token` with the refresh token. FastMCP calls `provider.load_refresh_token` and `exchange_refresh_token`, you issue a new JWT and new refresh, and the client gets a new token set. This continues until token expiry or revocation.
7. If the client logs out or similar, it can hit the revocation endpoint. FastMCP will call `provider.revoke_token` and you mark that token (and its partner) as revoked. Future uses of that token will then fail in `load_access_token` or `load_refresh_token`.

Throughout this integration, FastMCP itself is not making authorization decisions beyond what you configure (like required scopes). It defers to your provider for the heavy lifting (client validation, user auth, token issuance). FastMCP’s role is to route requests appropriately and enforce the presence of a valid token on protected operations.

It’s worth noting that the FastMCP project (by the author jlowin) has evolved quickly. As of version 2.x, some higher-level abstractions are being introduced (like possibly a simpler way to plug in common auth scenarios). But at the current state (v1.7 in the official SDK), using OAuth means implementing the interface and perhaps writing a fair bit of code – which leads into the idea of creating a reusable wrapper to simplify this.

## Designing a Reusable OAuth Provider Wrapper

Given the complexity of implementing `OAuthAuthorizationServerProvider` for each use case, one might want to create a **wrapper class** (e.g. `GolfOAuthProvider`) to abstract common patterns. This wrapper would implement the interface but allow a simpler configuration, so developers don’t have to write all the methods for every project. Here’s how we could approach it:

**Goals and Concept:** The `GolfOAuthProvider` (hypothetical name) would serve as an **adapter** between a high-level configuration (perhaps a JSON/YAML or object specifying how to do auth) and the MCP SDK’s low-level provider functions. For instance, if many MCP servers just want to use an external OpenID Connect provider (like Auth0, Azure AD, etc.), the wrapper could handle the standard steps: building the auth URL, exchanging codes with the external token endpoint, and so on. Alternatively, it could handle a simple internal username/password store. The key is to encode those options in a config and have the wrapper’s methods use that config.

**Configuration Model (`ProviderConfig`):** We’d define a dataclass or similar that holds all necessary settings. For example:

* `mode` (enum `"external_oidc"` or `"internal_simple"` or `"hybrid"` etc.) – determines which strategy to use.
* **For external OIDC mode:**

  * `auth_endpoint`, `token_endpoint`, `jwks_uri`, `userinfo_endpoint` (all URLs of the external IdP).
  * `client_id`, `client_secret` (credentials for *your MCP server* to use the external IdP – e.g., your server is a client of Auth0).
  * `scopes` to request on the external IdP (maybe configured to include `openid profile email` for user info).
  * Possibly `extra_params` or flags (e.g., use PKCE with external or not, prompt behavior, etc.).
* **For internal mode:**

  * `users` store or user validation callback – e.g., a dictionary of username->password hash, or a function to verify credentials.
  * `tokens_signing_key` (or certificate) to sign JWTs.
  * `token_lifetime` (access token TTL) and `refresh_lifetime`.
  * `allowed_scopes` and `default_scopes` (could derive from AuthSettings too).
  * Whether to issue refresh tokens or not.
* **Common:**

  * Reference to the MCP server’s own `issuer_url` (should match AuthSettings).
  * Keys for JWT signing: maybe an RSA private key (PEM string or filepath) or a JWK set. If not provided, the wrapper could generate a new key pair at startup.
  * Option to enable dynamic client registration (if so, maybe a storage for clients, or an upstream registration endpoint if using a SaaS that supports it).
  * Option to enable token revocation (and if so, storage for revoked token IDs or integration with external revocation if available).

**Internal Structure:** The `GolfOAuthProvider` would implement all methods of `OAuthAuthorizationServerProvider`, possibly by combining custom logic with calls to external services:

* *Client methods:* If `client_registration_options.enabled` is true, `register_client` could simply store the client in an internal dict/DB (with generated client\_secret if needed) or call an external registration API. `get_client` would look up the client in the store. If dynamic reg is off but we still expect only one or few known clients (e.g., the AI agent itself), the config might include a predefined client list that `get_client` checks. For an external IdP scenario, the MCP server might not manage clients at all – in that case, `get_client` could be implemented to return a dummy client object for a known client\_id (since the actual OAuth clients might be managed externally, but the MCP server still needs to recognize at least its own client integration).
* *Authorize:* This is where mode branching is significant:

  * In **external\_oidc mode**, `authorize` should construct the authorization URL for the external provider. For example, it might do: `auth_url = auth_endpoint + "?" + urlencode({ client_id, redirect_uri=<our_callback>, response_type="code", scope=<configured scopes>, state=<pass-through state>, code_challenge=<if using PKCE, from params>, ... })`. It would return this URL. The MCP SDK will redirect the user’s browser to it. Meanwhile, the wrapper needs to remember the context: we have an ongoing auth request for a given MCP client. Likely we can piggy-back on the `state` parameter – for instance, encode into the `state` a reference that the callback can use to find the original client and scopes (the `AuthorizationParams`). We might store a mapping from `state` to `AuthorizationParams` or store it in a signed token.
  * In **internal\_simple mode**, where the MCP server handles its own user auth, `authorize` might do something different: If the user is not yet authenticated (e.g., no session), it might return a URL for an internal login page. If we assume no interactive capability (since MCP is headless), another approach is possible: Some MCP servers running in trusted environments might skip user login entirely (if only one user or service-to-service). In that trivial case, `authorize` could immediately create an `AuthorizationCode` and return the final redirect URI (concatenating `?code=<code>&state=<state>` using the helper `construct_redirect_uri`). That would effectively auto-approve the request. But in general, for multi-user scenarios, an interactive login is needed. In a real web app, you’d integrate with Starlette sessions or an OAuth login page.
  * Regardless of mode, `authorize` must handle errors: e.g., if the requested redirect URI isn’t in the client’s allowed list, raise `AuthorizeError("invalid_request")` (the SDK will handle forming the error redirect).
* *Handling the callback (external mode):* We would implement a separate async function (not part of the interface, but part of the wrapper class) to serve as the callback endpoint for the external IdP. This function (say `async def handle_external_callback(request)`) would:

  1. Get the `code` and `state` from the request query.
  2. Look up the saved state to retrieve the original `AuthorizationParams` (and possibly client info).
  3. Use the external provider’s token endpoint to exchange the code for tokens (this requires `client_id`, `client_secret` of our MCP server’s registration with the IdP). For example, do an HTTP POST to `token_endpoint` with `grant_type=authorization_code`, the code, `redirect_uri` (must match what was used), and maybe a `code_verifier` if PKCE was used. Receive the IdP’s `access_token`, `id_token`, etc.
  4. Verify the IdP’s response (e.g., check the ID token’s signature using the IdP’s JWKS – the wrapper could cache the IdP JWKS on startup).
  5. Determine the user’s identity from the IdP tokens (perhaps the ID token’s `sub`, or call the `userinfo_endpoint` with the access token to get user info).
  6. Create a new **MCP authorization code** for the original client: instantiate an `AuthorizationCode` with a new random code value, the original scopes (maybe intersect with what IdP granted if needed), and link it to the user identity (could embed the user ID in a field if we extended AuthorizationCode). Store this code in an internal store (so that `load_authorization_code` can find it).
  7. Redirect the browser to the original client’s `redirect_uri` with `code=<new_code>&state=<orig_state>`. This completes the loop: the client that initiated now gets the code for the MCP server.

  * The FastMCP server would need to route this callback URL to the above logic. We can achieve that by either manually adding a route to the underlying FastAPI app in FastMCP (perhaps FastMCP lets us attach extra Starlette routes), or by running a side-by-side small web server for the callback. A cleaner way is if FastMCP has something like `mcp.add_route(path, func)` – not sure, but it likely can since it’s basically a FastAPI app under the hood. The wrapper can expose a method to register the callback route.
* *Exchange Authorization Code:* Now, when the client calls our `/token`:

  * `load_authorization_code`: our wrapper will look up the code in the internal store (the one we saved in step 6 above, or in internal mode, the one we possibly created after user login). It returns the `AuthorizationCode` object (which might include the user or external token reference).
  * `exchange_authorization_code`: In external mode, we already have the IdP’s tokens from earlier. We have two choices:

    1. We could **forward the external token** directly: for instance, use the IdP’s access token as our MCP access token. However, that might not be ideal because the MCP server would then need to trust an external token on each request (meaning `load_access_token` would have to validate an external token – doable by JWKS of the IdP). This essentially makes the MCP server a pure resource server using an external auth server.
    2. Or we **mint our own access token** for the MCP server, embedding some info from the external token (like the user’s ID from the IdP, and maybe an identifier of the IdP). This way, the MCP server’s resources can be protected by verifying tokens against *its own* keys (which it controls). The MCP server then acts as its own Authorization Server (with the external IdP as an upstream identity provider). This is a classic OAuth federation approach.

    * Minting our own token is often preferable for control. So the wrapper could create a JWT signed with the MCP server’s key. For claims, it might set `sub` to something like `<IdP>:<user_id>` or map to an internal user id, include `scope` claims, etc. The `issuer` would be our MCP server’s issuer\_url.
    * It would also generate a refresh token (could be a random UUID or JWT). We might *not* want to use the IdP’s refresh token directly with the client, because that would couple the client to the IdP. Instead, the wrapper can keep the IdP refresh token server-side (associated with the user’s session or in the refresh token object), and issue its own refresh token to the client. Then when `exchange_refresh_token` is called later, the wrapper will use the stored IdP refresh token to get a new IdP access token under the hood, and then mint a new MCP access token. This way, the client only ever deals with the MCP server’s tokens.
    * The `OAuthToken` returned would carry `access_token` (our JWT) and maybe a new `refresh_token` (random string or JWT). We include `token_type="bearer"` and `expires_in` as needed.
  * In internal mode, `exchange_authorization_code` would be simpler: it creates a JWT access token using the server’s key (with `sub` as the local user’s id) and a refresh token if configured. It could use scopes from the code. No external calls needed.
* *Refresh Token handling:*

  * `load_refresh_token`: the wrapper looks up the refresh token in its store. If we issued our own refresh token, we find it and also retrieve any context (like the external refresh token or user info) associated.
  * `exchange_refresh_token`:

    * External mode: Use the stored external refresh token (if still valid) to call the IdP’s token endpoint with `grant_type=refresh_token`. Get a new IdP access (and possibly new refresh) token. Update our stored external refresh token if it rotated (some IdPs do rotate refresh tokens). Then mint a new MCP access token (JWT) for the client, possibly also rotate the MCP refresh token. Return the new tokens to the client. If the external refresh token is expired or revoked, we should propagate an error (`invalid_grant`).
    * Internal mode: Simply create a new JWT (and new refresh token) and revoke the old one, similar to standard practice.
* *Token Validation (`load_access_token`):*

  * External-forwarding strategy: If we decided to use external access tokens as MCP access tokens directly (not recommended unless the external issuer == MCP issuer in a federation scenario), this method would need to verify the token against the external IdP’s JWKS. It would check that the token’s `iss` matches the external provider, etc. Since our AuthSettings.issuer\_url would not match the token’s issuer, this scenario complicates things. So likely we wouldn’t do this for user tokens.
  * Internal/minted token strategy: Here, `load_access_token` will verify the JWT with the MCP’s own public key (which our JWKS endpoint publishes). The wrapper can do this via a JWT library. It then returns an `AccessToken` model. If we included custom fields (like user id or external claims) in our `AccessTokenT` type, we’d populate them now. For example, if our AccessToken model has `user_id`, we get it from the JWT claims and include it. This object might be attached to the request context by FastMCP so that tools can access the user info if needed.
  * Additionally, the wrapper can enforce scope checking here (though FastMCP itself also checks required\_scopes). It could, for instance, filter out tokens that don’t have certain internal claims or are revoked (we could maintain a cache of revoked token IDs if needed).
* *Revocation (`revoke_token`):*

  * The wrapper should remove tokens from its stores. If an external IdP provides a revocation endpoint and if the token to revoke is actually an external token (in case of forward strategy), we might call that. However, since in our design we issue our own tokens, revocation means:

    * Mark the given refresh token (or access token) as revoked in our internal DB (so `load_refresh_token` or `load_access_token` will fail them in future).
    * If we still have a valid session or refresh token at the external IdP, we might call the external revocation too, to invalidate that side. This depends on whether the IdP requires explicit revocation or if we rely on short expiration.
    * For internal mode, simply mark the token pair as revoked in DB or memory. The provider interface suggests that providing either an access or refresh token should result in both being invalidated, so we ensure that (e.g., look up the family by token string and delete both).

**Wrapper Layout and Build vs Runtime:**

We can structure `GolfOAuthProvider` with helper methods to separate concerns, and perform heavy setup at initialization:

* In `__init__`, take the `ProviderConfig`. Based on config:

  * If no signing keys provided and we need one, generate a new RSA key pair (this is a one-time cost). We’d store the private key in the provider (to sign tokens) and the public in a JWKS structure for the JWKS endpoint. We might even save it to disk if we want it to persist across restarts (or accept an environment variable for the key).
  * If external mode, fetch the external provider’s JWKS and store it (for verifying ID tokens). Also, fetch their OAuth metadata if available (OpenID Connect discovery document) to confirm endpoints and capabilities. This could be done at “build time” (i.e., server startup) to avoid latency during requests. We might refresh the JWKS periodically (the config can include a TTL or we use cache headers).
  * Set up data stores: e.g., an in-memory dict or a database connection for clients, auth codes, tokens. If using a DB, ensure connections are ready. This is also initialization work.
  * If needed, register the external callback route with FastMCP. Possibly the wrapper could expose something like `provider.get_callback_route()` giving a Starlette `Route` object that the application should include.
  * Prepare any static response data: for example, the server’s OAuth2 **metadata document**. Although not explicitly mentioned, a well-formed auth server has a discovery endpoint (`.well-known/openid-configuration`). We might generate this JSON from our settings (issuer, auth URL, token URL, scopes, JWKS URL, etc.) at startup so it can be served quickly. This is especially helpful if clients auto-discover; the MCP spec might not require a full OIDC discovery, but having it doesn’t hurt. This generation is a build-time task.

At runtime, the wrapper’s methods handle per-request logic, using the info and resources prepared at init:

* The heavy cryptographic operations (JWT sign/verify) are performed as needed per request, but using keys that were loaded/generated at startup.
* Network calls to external IdP (token exchange, userinfo) happen during authorization and token exchange flows – these are runtime and unavoidable, but the wrapper can minimize them (e.g., do not call userinfo if ID token already has needed info).
* Data storage operations (lookups for codes/tokens) are runtime but should be optimized (perhaps using an in-memory cache for codes since they are short-lived, etc.).
* Logging and error handling are runtime: the wrapper can log events (token issued, user X authorized, token Y revoked) which is useful for auditing.

**Build-Time Code Generation:** The question hints at “what should be generated at build time vs runtime-configurable.” Aside from the above initialization, we can also consider if any **code** needs to be generated. Ideally, we keep code static and just supply data/config. But one idea: if we had a config describing the OAuth provider (like a template), we could **generate a subclass** of `GolfOAuthProvider` with some sections filled in. For instance, if someone writes a YAML with known clients and a static user list, one could codegen a provider that hardcodes those (for performance and security). However, this might be overkill – a well-written class can handle it via config without real codegen.

Instead, “build time” likely refers to *configuration time* (before deployment). So:

* **Build-time (configuration-time) tasks:**

  * Choosing the mode (e.g., compile the app for external Auth0 vs internal).
  * Provisioning credentials (register the MCP server as a client in the external IdP and put those in config).
  * Generating encryption keys or setting environment secrets for them.
  * Defining allowed scopes and clients (which might be baked into the app).
  * Essentially, anything that doesn’t need to change at runtime for each request should be set in config or done on startup. For example, if you know the valid scopes and default scopes, put them in AuthSettings (which is set at build/deploy time).
  * If using static clients (no dynamic reg), you might list them in a config file. The wrapper can load that once.

* **Runtime-configurable aspects:**

  * Dynamic client registration is inherently runtime (clients register and go).
  * Token revocation lists will be managed at runtime (as tokens come and go).
  * If using external IdP, new user authorizations happen at runtime (though the IdP config itself is static).
  * Perhaps the admin of the server might toggle something at runtime (like disabling a certain scope or blocking a user) – the wrapper could allow hooks for that (e.g., consult a dynamic policy in `load_access_token` to reject tokens for banned users).
  * In essence, anything to do with live tokens, sessions, and user interactions is runtime.

**Example Wrapper Usage:** If we had `GolfOAuthProvider` implemented, using it might look like:

```python
provider = GolfOAuthProvider(config=ProviderConfig(
    mode="external_oidc",
    issuer_url="https://myapp.com",
    auth_endpoint="https://auth.example.com/authorize",
    token_endpoint="https://auth.example.com/oauth/token",
    jwks_uri="https://auth.example.com/.well-known/jwks.json",
    client_id="mcp-server-123", client_secret="ABCDEF...",
    scopes=["openid", "profile", "email"],
))
mcp = FastMCP("My Secure App", auth_provider=provider, auth=AuthSettings(
    issuer_url="https://myapp.com",
    required_scopes=["myapi.read"],
    client_registration_options=ClientRegistrationOptions(enabled=False)
))
```

The above configures the MCP server to use an external OIDC provider (with given endpoints). The wrapper handles redirecting to the external auth, exchanging codes, and issuing its own tokens that include an `"myapi.read"` scope. On the other hand, for a simple internal auth:

```python
provider = GolfOAuthProvider(config=ProviderConfig(
    mode="internal_simple",
    users={"alice": "<hashed_pw>", "bob": "<hashed_pw>"},
    token_signing_key="path/to/private.pem",
    default_scopes=["myapi.read"],
    allowed_scopes=["myapi.read","myapi.write"],
    token_lifetime=3600, refresh_lifetime=86400
))
```

In this mode, the provider might present a basic HTTP auth or some out-of-band mechanism for user login (since MCP doesn’t natively handle user prompts, one might integrate an interactive CLI or pre-shared token for development). It would then directly issue codes and tokens for known users.

**Summary of Wrapper Advantages:** By encapsulating all this logic, `GolfOAuthProvider` would make it **reusable** across MCP servers. It abstracts:

* External vs internal auth differences.
* JWT handling (developers using it don’t have to manually call PyJWT; the wrapper would do it).
* Storage of tokens/codes.
* Integration of JWKS and user info.
* It could also handle **maintenance tasks** like cleaning up expired codes/tokens periodically.

The wrapper essentially becomes an OAuth “module” you can plug in with a config, instead of hand-writing the entire provider. This separation of config (what you want to use) and implementation (how it’s done under the hood) is key for maintainability.

When building such a wrapper, one must carefully decide what is fixed at build time: for example, the choice of external IdP and the associated endpoints is a build-time decision (you wouldn’t normally switch the IdP on the fly). The cryptographic keys are usually generated or set up ahead of time as well. Conversely, anything that needs flexibility (e.g., the actual client registrations or the active tokens) are handled at runtime.

In conclusion, the current MCP Python SDK provides a comprehensive but low-level OAuth 2.0 integration – covering authorization codes, tokens (with JWT support), refresh, revocation, and even client registration. It does so through the `OAuthAuthorizationServerProvider` interface, which gives developers full control over how authentication is done. FastMCP simply plugs this into the web server, enforcing the auth on incoming requests and routing the OAuth endpoints to the provider. A custom wrapper like `GolfOAuthProvider` can be created to simplify common patterns by mapping a high-level config to those interface methods. The wrapper would handle the heavy lifting (JWT creation/verification, external IdP calls, storage) internally, allowing server developers to enable OAuth by configuration rather than coding every detail. By deciding which parts of that process are static (build-time) and which are dynamic (runtime), we ensure the server is efficient, secure, and easy to configure for various authentication scenarios.

**Sources:**

* MCP SDK OAuth implementation and usage examples
* Definition of `OAuthAuthorizationServerProvider` interface and its methods
* FastMCP documentation on integrating auth providers
* OAuth2 error and flow handling as per RFC 6749 (from SDK code comments)
* JWKS and token verification in OAuth2 (Scalekit blog example)