"""
Mock OAuth2 PKCE Server for Testing
Simulates an OAuth gateway for local development and testing

Run this alongside your Time MCP Server to test the complete OAuth flow.
This is for TESTING ONLY - not production-ready!

Usage:
    python mock_oauth_server.py

Then configure your Time MCP Server to use:
    auth_url: http://localhost:8000/oauth/authorize
    token_url: http://localhost:8000/oauth/token
"""

import hashlib
import base64
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlencode, parse_qs

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


# In-memory storage (for testing only!)
authorization_codes: Dict[str, Dict] = {}
access_tokens: Dict[str, Dict] = {}
refresh_tokens: Dict[str, str] = {}

# Configuration
VALID_CLIENT_IDS = ['time-mcp-client']
VALID_REDIRECT_URIS = [
    'http://localhost:3000/callback',
    'http://localhost:3000/oauth/callback'
]
VALID_SCOPES = ['time:read', 'time:convert']
ACCESS_TOKEN_LIFETIME = 3600  # 1 hour
AUTHORIZATION_CODE_LIFETIME = 600  # 10 minutes


def generate_token(length: int = 32) -> str:
    """Generate a random token"""
    return secrets.token_urlsafe(length)


def verify_code_challenge(verifier: str, challenge: str) -> bool:
    """Verify PKCE code challenge"""
    # Calculate SHA256 hash
    sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
    # Encode to base64url
    calculated_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
    return calculated_challenge == challenge


class OAuthHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Custom logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def send_json_response(self, status_code: int, data: dict):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_html_response(self, status_code: int, html: str):
        """Send HTML response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        params = parse_qs(parsed_url.query)
        
        # Convert single-item lists to strings
        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        
        if path == '/':
            self.handle_root()
        elif path == '/oauth/authorize':
            self.handle_authorize(params)
        elif path == '/.well-known/oauth-authorization-server':
            self.handle_oauth_metadata()
        elif path == '/.well-known/openid-configuration':
            self.handle_openid_configuration()
        else:
            self.send_json_response(404, {'error': 'not_found'})
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(body)
        
        # Convert single-item lists to strings
        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        
        if path == '/oauth/token':
            self.handle_token(params)
        else:
            self.send_json_response(404, {'error': 'not_found'})
    
    def handle_root(self):
        """Root endpoint with server info"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mock OAuth2 PKCE Server</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 50px auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                .endpoint { 
                    background: #f0f0f0; 
                    padding: 10px; 
                    margin: 10px 0;
                    border-radius: 4px;
                    font-family: monospace;
                }
                .status { 
                    color: #28a745; 
                    font-weight: bold;
                }
                code {
                    background: #e8e8e8;
                    padding: 2px 6px;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Mock OAuth2 PKCE Server</h1>
                <p class="status">✅ Server is running</p>
                
                <h2>Available Endpoints</h2>
                <div class="endpoint">
                    <strong>GET /oauth/authorize</strong><br>
                    Authorization endpoint (user login)
                </div>
                <div class="endpoint">
                    <strong>POST /oauth/token</strong><br>
                    Token endpoint (exchange code for token)
                </div>
                <div class="endpoint">
                    <strong>GET /.well-known/oauth-authorization-server</strong><br>
                    OAuth 2.0 Authorization Server Metadata (RFC 8414)
                </div>
                <div class="endpoint">
                    <strong>GET /.well-known/openid-configuration</strong><br>
                    OpenID Connect Discovery endpoint
                </div>
                
                <h2>Configuration</h2>
                <ul>
                    <li><strong>Valid Client IDs:</strong> <code>time-mcp-client</code></li>
                    <li><strong>Valid Scopes:</strong> <code>time:read time:convert</code></li>
                    <li><strong>Code Challenge Method:</strong> <code>S256</code> (SHA256)</li>
                    <li><strong>Access Token Lifetime:</strong> 1 hour</li>
                    <li><strong>Authorization Code Lifetime:</strong> 10 minutes</li>
                </ul>
                
                <h2>Testing Instructions</h2>
                <ol>
                    <li>Configure your MCP server to use:
                        <ul>
                            <li><code>auth_url: http://localhost:8000/oauth/authorize</code></li>
                            <li><code>token_url: http://localhost:8000/oauth/token</code></li>
                        </ul>
                    </li>
                    <li>Use Postman collection to test the OAuth flow</li>
                    <li>All requests are automatically approved (no real login)</li>
                </ol>
                
                <h2>⚠️ Warning</h2>
                <p>This is a MOCK server for testing only. Do NOT use in production!</p>
                <ul>
                    <li>No real authentication</li>
                    <li>No persistent storage</li>
                    <li>Automatically approves all requests</li>
                    <li>Minimal security validation</li>
                </ul>
            </div>
        </body>
        </html>
        """
        self.send_html_response(200, html)
    
    def handle_oauth_metadata(self):
        """Handle OAuth 2.0 Authorization Server Metadata (RFC 8414)"""
        metadata = {
            "issuer": "http://localhost:8000",
            "authorization_endpoint": "http://localhost:8000/oauth/authorize",
            "token_endpoint": "http://localhost:8000/oauth/token",
            "token_endpoint_auth_methods_supported": ["none"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "response_types_supported": ["code"],
            "code_challenge_methods_supported": ["S256"],
            "scopes_supported": ["time:read", "time:convert"],
            "service_documentation": "http://localhost:8000/",
            "ui_locales_supported": ["en-US"],
            "revocation_endpoint": "http://localhost:8000/oauth/revoke",
            "introspection_endpoint": "http://localhost:8000/oauth/introspect",
            "response_modes_supported": ["query", "fragment"],
            "token_endpoint_auth_signing_alg_values_supported": ["none"]
        }
        self.send_json_response(200, metadata)
    
    def handle_openid_configuration(self):
        """Handle OpenID Connect Discovery (compatible format)"""
        config = {
            "issuer": "http://localhost:8000",
            "authorization_endpoint": "http://localhost:8000/oauth/authorize",
            "token_endpoint": "http://localhost:8000/oauth/token",
            "userinfo_endpoint": "http://localhost:8000/oauth/userinfo",
            "jwks_uri": "http://localhost:8000/.well-known/jwks.json",
            "registration_endpoint": "http://localhost:8000/oauth/register",
            "scopes_supported": ["openid", "time:read", "time:convert"],
            "response_types_supported": ["code"],
            "response_modes_supported": ["query", "fragment"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["none"],
            "token_endpoint_auth_methods_supported": ["none"],
            "code_challenge_methods_supported": ["S256"],
            "service_documentation": "http://localhost:8000/"
        }
        self.send_json_response(200, config)
    
    def handle_authorize(self, params: dict):
        """Handle authorization request"""
        # Validate required parameters
        required = ['response_type', 'client_id', 'redirect_uri', 'code_challenge', 'code_challenge_method']
        missing = [p for p in required if p not in params]
        
        if missing:
            error_html = f"""
            <html><body>
            <h1>Error: Missing Parameters</h1>
            <p>Missing: {', '.join(missing)}</p>
            <p><a href="/">Back to home</a></p>
            </body></html>
            """
            self.send_html_response(400, error_html)
            return
        
        # Validate parameters
        if params['response_type'] != 'code':
            self.send_html_response(400, '<html><body><h1>Error: Invalid response_type</h1></body></html>')
            return
        
        if params['client_id'] not in VALID_CLIENT_IDS:
            self.send_html_response(400, '<html><body><h1>Error: Invalid client_id</h1></body></html>')
            return
        
        if params['redirect_uri'] not in VALID_REDIRECT_URIS:
            self.send_html_response(400, '<html><body><h1>Error: Invalid redirect_uri</h1></body></html>')
            return
        
        if params['code_challenge_method'] != 'S256':
            self.send_html_response(400, '<html><body><h1>Error: Unsupported code_challenge_method</h1></body></html>')
            return
        
        # Generate authorization code
        auth_code = generate_token(32)
        
        # Store authorization code with metadata
        authorization_codes[auth_code] = {
            'client_id': params['client_id'],
            'redirect_uri': params['redirect_uri'],
            'scope': params.get('scope', ' '.join(VALID_SCOPES)),
            'code_challenge': params['code_challenge'],
            'code_challenge_method': params['code_challenge_method'],
            'created_at': datetime.now(),
            'used': False
        }
        
        print(f"✅ Generated authorization code: {auth_code[:10]}...")
        print(f"   Client ID: {params['client_id']}")
        print(f"   Code Challenge: {params['code_challenge'][:20]}...")
        
        # Redirect back with authorization code
        redirect_params = {
            'code': auth_code,
            'state': params.get('state', '')
        }
        redirect_url = f"{params['redirect_uri']}?{urlencode(redirect_params)}"
        
        # Show success page with auto-redirect
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Successful</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    text-align: center;
                }}
                .success {{
                    color: #28a745;
                    font-size: 48px;
                }}
                .code {{
                    background: #f0f0f0;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    font-family: monospace;
                    word-break: break-all;
                }}
                .instructions {{
                    background: #fff3cd;
                    padding: 15px;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
            </style>
            <meta http-equiv="refresh" content="3;url={redirect_url}">
        </head>
        <body>
            <div class="success">✅</div>
            <h1>Authorization Successful!</h1>
            <p>You will be redirected automatically...</p>
            
            <div class="code">
                <strong>Authorization Code:</strong><br>
                {auth_code}
            </div>
            
            <div class="instructions">
                <strong>📋 For Manual Testing:</strong><br>
                Copy the authorization code above and use it in your Postman collection.<br>
                Set the <code>authorization_code</code> variable to this value.
            </div>
            
            <p>Redirecting to: <code>{redirect_url}</code></p>
            <p><a href="{redirect_url}">Click here if not redirected</a></p>
        </body>
        </html>
        """
        
        self.send_html_response(200, html)
    
    def handle_token(self, params: dict):
        """Handle token request"""
        grant_type = params.get('grant_type')
        
        if grant_type == 'authorization_code':
            self.handle_authorization_code_grant(params)
        elif grant_type == 'refresh_token':
            self.handle_refresh_token_grant(params)
        else:
            self.send_json_response(400, {
                'error': 'unsupported_grant_type',
                'error_description': f'Grant type "{grant_type}" not supported'
            })
    
    def handle_authorization_code_grant(self, params: dict):
        """Handle authorization code grant"""
        # Validate required parameters
        required = ['code', 'client_id', 'code_verifier']
        missing = [p for p in required if p not in params]
        
        if missing:
            self.send_json_response(400, {
                'error': 'invalid_request',
                'error_description': f'Missing parameters: {", ".join(missing)}'
            })
            return
        
        code = params['code']
        client_id = params['client_id']
        code_verifier = params['code_verifier']
        
        # Validate authorization code
        if code not in authorization_codes:
            self.send_json_response(400, {
                'error': 'invalid_grant',
                'error_description': 'Invalid authorization code'
            })
            return
        
        auth_data = authorization_codes[code]
        
        # Check if code already used
        if auth_data['used']:
            self.send_json_response(400, {
                'error': 'invalid_grant',
                'error_description': 'Authorization code already used'
            })
            return
        
        # Check if code expired
        code_age = (datetime.now() - auth_data['created_at']).total_seconds()
        if code_age > AUTHORIZATION_CODE_LIFETIME:
            self.send_json_response(400, {
                'error': 'invalid_grant',
                'error_description': 'Authorization code expired'
            })
            return
        
        # Validate client_id
        if client_id != auth_data['client_id']:
            self.send_json_response(400, {
                'error': 'invalid_client',
                'error_description': 'Client ID mismatch'
            })
            return
        
        # Verify PKCE code_verifier
        if not verify_code_challenge(code_verifier, auth_data['code_challenge']):
            print(f"❌ PKCE verification failed!")
            print(f"   Code Verifier: {code_verifier[:20]}...")
            print(f"   Expected Challenge: {auth_data['code_challenge'][:20]}...")
            self.send_json_response(400, {
                'error': 'invalid_grant',
                'error_description': 'PKCE verification failed'
            })
            return
        
        print(f"✅ PKCE verification successful!")
        
        # Mark code as used
        auth_data['used'] = True
        
        # Generate tokens
        access_token = generate_token(32)
        refresh_token = generate_token(32)
        
        # Store tokens
        access_tokens[access_token] = {
            'client_id': client_id,
            'scope': auth_data['scope'],
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ACCESS_TOKEN_LIFETIME)
        }
        
        refresh_tokens[refresh_token] = access_token
        
        print(f"✅ Generated access token: {access_token[:10]}...")
        print(f"   Expires in: {ACCESS_TOKEN_LIFETIME} seconds")
        
        # Return token response
        self.send_json_response(200, {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_LIFETIME,
            'refresh_token': refresh_token,
            'scope': auth_data['scope']
        })
    
    def handle_refresh_token_grant(self, params: dict):
        """Handle refresh token grant"""
        refresh_token = params.get('refresh_token')
        
        if not refresh_token or refresh_token not in refresh_tokens:
            self.send_json_response(400, {
                'error': 'invalid_grant',
                'error_description': 'Invalid refresh token'
            })
            return
        
        # Get old access token data
        old_access_token = refresh_tokens[refresh_token]
        if old_access_token not in access_tokens:
            self.send_json_response(400, {
                'error': 'invalid_grant',
                'error_description': 'Refresh token invalid'
            })
            return
        
        old_token_data = access_tokens[old_access_token]
        
        # Generate new tokens
        new_access_token = generate_token(32)
        new_refresh_token = generate_token(32)
        
        # Store new tokens
        access_tokens[new_access_token] = {
            'client_id': old_token_data['client_id'],
            'scope': old_token_data['scope'],
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ACCESS_TOKEN_LIFETIME)
        }
        
        # Update refresh token mapping
        del refresh_tokens[refresh_token]
        refresh_tokens[new_refresh_token] = new_access_token
        
        # Optionally invalidate old access token
        del access_tokens[old_access_token]
        
        print(f"✅ Refreshed tokens")
        print(f"   New access token: {new_access_token[:10]}...")
        
        # Return new tokens
        self.send_json_response(200, {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_LIFETIME,
            'refresh_token': new_refresh_token,
            'scope': old_token_data['scope']
        })


def run_server(port: int = 8000):
    """Run the mock OAuth server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OAuthHandler)
    
    print("=" * 60)
    print("🔐 Mock OAuth2 PKCE Server")
    print("=" * 60)
    print(f"\n✅ Server running on http://localhost:{port}")
    print(f"\nEndpoints:")
    print(f"  - Authorization: http://localhost:{port}/oauth/authorize")
    print(f"  - Token:         http://localhost:{port}/oauth/token")
    print(f"  - Info:          http://localhost:{port}/")
    print(f"\nConfiguration:")
    print(f"  - Client IDs: {', '.join(VALID_CLIENT_IDS)}")
    print(f"  - Scopes: {', '.join(VALID_SCOPES)}")
    print(f"  - PKCE Method: S256 (SHA256)")
    print(f"\n⚠️  This is a TESTING server only!")
    print(f"    Do NOT use in production.\n")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.server_close()


if __name__ == "__main__":
    run_server(8000)
