"""
Test OAuth2 PKCE Flow with Mock Server
Tests the complete authentication flow between the Time MCP Server and Mock OAuth Server
"""

import hashlib
import base64
import secrets
import requests
import json
from urllib.parse import urlencode, parse_qs, urlparse

# Configuration
MOCK_OAUTH_URL = "http://localhost:8000"
MCP_SERVER_URL = "http://localhost:3000"
CLIENT_ID = "time-mcp-client"
REDIRECT_URI = "http://localhost:3000/oauth/callback"
SCOPES = "time:read time:convert"


def generate_pkce_pair():
    """Generate PKCE code_verifier and code_challenge"""
    # Generate code_verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generate code_challenge (SHA256 hash of verifier)
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge


def test_oauth_flow():
    """Test the complete OAuth2 PKCE flow"""
    
    print("=" * 70)
    print("Testing OAuth2 PKCE Flow")
    print("=" * 70)
    
    # Step 1: Generate PKCE parameters
    print("\n[1/4] Generating PKCE parameters...")
    code_verifier, code_challenge = generate_pkce_pair()
    print(f"  ✅ Code Verifier: {code_verifier[:20]}...")
    print(f"  ✅ Code Challenge: {code_challenge[:20]}...")
    
    # Step 2: Request authorization
    print("\n[2/4] Requesting authorization...")
    state = secrets.token_urlsafe(16)
    
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    auth_url = f"{MOCK_OAUTH_URL}/oauth/authorize?{urlencode(auth_params)}"
    print(f"  📡 Authorization URL: {auth_url}")
    
    # Make the authorization request
    try:
        response = requests.get(auth_url, allow_redirects=False)
        
        if response.status_code == 200:
            # Parse code from HTML response
            import re
            # Look for the authorization code in the HTML
            code_match = re.search(r'<code[^>]*>([A-Za-z0-9_-]{40,})</code>', response.text)
            if not code_match:
                # Try alternative pattern
                code_match = re.search(r'code=([A-Za-z0-9_-]+)', response.text)
            
            if code_match:
                authorization_code = code_match.group(1).strip()
                print(f"  ✅ Authorization Code: {authorization_code[:20]}...")
            else:
                print("  ❌ Could not extract code from response")
                print("  Response preview:", response.text[:300])
                return False
        else:
            print(f"  ❌ Authorization failed: {response.status_code}")
            print(response.text[:200])
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Could not connect to OAuth server. Is it running on port 8000?")
        return False
    
    # Step 3: Exchange code for token
    print("\n[3/4] Exchanging code for access token...")
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'code_verifier': code_verifier
    }
    
    try:
        token_response = requests.post(
            f"{MOCK_OAUTH_URL}/oauth/token",
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if token_response.status_code == 200:
            token_info = token_response.json()
            access_token = token_info.get('access_token')
            refresh_token = token_info.get('refresh_token')
            expires_in = token_info.get('expires_in')
            
            print(f"  ✅ Access Token: {access_token[:20]}...")
            print(f"  ✅ Refresh Token: {refresh_token[:20]}...")
            print(f"  ✅ Expires In: {expires_in} seconds")
            print(f"  ✅ Scopes: {token_info.get('scope')}")
        else:
            print(f"  ❌ Token exchange failed: {token_response.status_code}")
            print(token_response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Could not connect to OAuth server")
        return False
    
    # Step 4: Test token refresh
    print("\n[4/4] Testing token refresh...")
    
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID
    }
    
    try:
        refresh_response = requests.post(
            f"{MOCK_OAUTH_URL}/oauth/token",
            data=refresh_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if refresh_response.status_code == 200:
            new_token_info = refresh_response.json()
            new_access_token = new_token_info.get('access_token')
            new_refresh_token = new_token_info.get('refresh_token')
            
            print(f"  ✅ New Access Token: {new_access_token[:20]}...")
            print(f"  ✅ New Refresh Token: {new_refresh_token[:20]}...")
        else:
            print(f"  ❌ Token refresh failed: {refresh_response.status_code}")
            print(refresh_response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Could not connect to OAuth server")
        return False
    
    print("\n" + "=" * 70)
    print("✅ OAuth2 PKCE Flow Test PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print(f"  • PKCE generation: ✅")
    print(f"  • Authorization request: ✅")
    print(f"  • Token exchange: ✅")
    print(f"  • Token refresh: ✅")
    print("\nThe OAuth flow is working correctly!")
    
    return True


if __name__ == "__main__":
    success = test_oauth_flow()
    exit(0 if success else 1)
