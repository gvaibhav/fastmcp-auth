# Well-Known OAuth Endpoints Implementation

## Summary

Added standard `.well-known` discovery endpoints for OAuth 2.0 compliance:

### Authorization Server (Mock OAuth Server - port 8000)

1. **`/.well-known/oauth-authorization-server`** (RFC 8414)
   - OAuth 2.0 Authorization Server Metadata
   - Provides server capabilities and endpoint URLs
   - Fields: issuer, authorization_endpoint, token_endpoint, grant_types_supported, etc.

2. **`/.well-known/openid-configuration`**
   - OpenID Connect Discovery endpoint
   - Compatible format for OIDC clients
   - Additional fields: userinfo_endpoint, jwks_uri, etc.

### Protected Resource (Time MCP Server - port 3000)

1. **`/.well-known/oauth-protected-resource`** (RFC 9728)
   - OAuth 2.0 Protected Resource Metadata
   - Describes the protected resource server
   - Fields: resource, authorization_servers, scopes_supported, bearer_methods_supported, etc.

## Implementation Details

### Authorization Server Metadata (RFC 8414)

```json
{
  "issuer": "http://localhost:8000",
  "authorization_endpoint": "http://localhost:8000/oauth/authorize",
  "token_endpoint": "http://localhost:8000/oauth/token",
  "token_endpoint_auth_methods_supported": ["none"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "response_types_supported": ["code"],
  "code_challenge_methods_supported": ["S256"],
  "scopes_supported": ["time:read", "time:convert"],
  "service_documentation": "http://localhost:8000/",
  "revocation_endpoint": "http://localhost:8000/oauth/revoke",
  "introspection_endpoint": "http://localhost:8000/oauth/introspect"
}
```

### Protected Resource Metadata (RFC 9728)

```json
{
  "resource": "http://localhost:3000",
  "authorization_servers": ["http://localhost:8000"],
  "bearer_methods_supported": ["header"],
  "scopes_supported": ["time:read", "time:convert"],
  "resource_documentation": "http://localhost:3000/",
  "token_endpoint": "http://localhost:8000/oauth/token",
  "introspection_endpoint": "http://localhost:8000/oauth/introspect",
  "revocation_endpoint": "http://localhost:8000/oauth/revoke"
}
```

## Testing

Run the test script:

```powershell
# Start both servers first
python mock_oauth_server.py     # Terminal 1
python time_mcp_server.py        # Terminal 2

# Run tests
python test_wellknown_endpoints.py
```

Or test manually:

```powershell
# Authorization Server metadata
curl http://localhost:8000/.well-known/oauth-authorization-server

# OpenID configuration
curl http://localhost:8000/.well-known/openid-configuration

# Protected Resource metadata
curl http://localhost:3000/.well-known/oauth-protected-resource
```

## Benefits

1. **Standards Compliance**: Implements RFC 8414 and RFC 9728
2. **Auto-Discovery**: Clients can automatically discover server capabilities
3. **Interoperability**: Works with standard OAuth 2.0 clients
4. **Documentation**: Self-documenting API endpoints
5. **Future-Proof**: Easy to extend with additional metadata

## Files Modified

- `mock_oauth_server.py` - Added AS metadata endpoints
- `time_mcp_server.py` - Added protected resource metadata endpoint
- `test_wellknown_endpoints.py` - New test file
- `README.md` - Updated documentation

## References

- [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414.html) - OAuth 2.0 Authorization Server Metadata
- [RFC 9728](https://www.rfc-editor.org/rfc/rfc9728.html) - OAuth 2.0 Protected Resource Metadata
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)
