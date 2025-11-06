"""
Test .well-known endpoints for OAuth servers
Tests both Authorization Server and Protected Resource metadata endpoints
"""

import requests
import json


def test_authorization_server_metadata():
    """Test OAuth 2.0 Authorization Server Metadata endpoint (RFC 8414)"""
    print("\n" + "=" * 60)
    print("Testing Authorization Server Metadata")
    print("=" * 60)
    
    url = "http://localhost:8000/.well-known/oauth-authorization-server"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\nEndpoint: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            metadata = response.json()
            print("\n✅ Authorization Server Metadata Retrieved:")
            print(json.dumps(metadata, indent=2))
            
            # Verify required fields
            required_fields = [
                'issuer',
                'authorization_endpoint',
                'token_endpoint',
                'response_types_supported'
            ]
            
            missing = [f for f in required_fields if f not in metadata]
            if missing:
                print(f"\n⚠️  Missing required fields: {missing}")
            else:
                print("\n✅ All required fields present")
                
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: OAuth server not running?")
        print("   Start it with: python mock_oauth_server.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_openid_configuration():
    """Test OpenID Connect Discovery endpoint"""
    print("\n" + "=" * 60)
    print("Testing OpenID Connect Configuration")
    print("=" * 60)
    
    url = "http://localhost:8000/.well-known/openid-configuration"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\nEndpoint: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("\n✅ OpenID Configuration Retrieved:")
            print(json.dumps(config, indent=2))
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: OAuth server not running?")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_protected_resource_metadata():
    """Test OAuth 2.0 Protected Resource Metadata endpoint (RFC 9728)"""
    print("\n" + "=" * 60)
    print("Testing Protected Resource Metadata")
    print("=" * 60)
    
    url = "http://localhost:3000/.well-known/oauth-protected-resource"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"\nEndpoint: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            metadata = response.json()
            print("\n✅ Protected Resource Metadata Retrieved:")
            print(json.dumps(metadata, indent=2))
            
            # Verify important fields
            important_fields = [
                'resource',
                'authorization_servers',
                'scopes_supported'
            ]
            
            missing = [f for f in important_fields if f not in metadata]
            if missing:
                print(f"\n⚠️  Missing important fields: {missing}")
            else:
                print("\n✅ All important fields present")
                
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: MCP server not running?")
        print("   Start it with: python time_mcp_server.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🔍 Testing OAuth .well-known Endpoints")
    print("=" * 60)
    
    results = {
        "Authorization Server Metadata": False,
        "OpenID Configuration": False,
        "Protected Resource Metadata": False
    }
    
    # Test Authorization Server endpoints
    print("\n📋 Authorization Server Tests (port 8000)")
    results["Authorization Server Metadata"] = (
        test_authorization_server_metadata()
    )
    results["OpenID Configuration"] = test_openid_configuration()
    
    # Test Protected Resource endpoint
    print("\n📋 Protected Resource Tests (port 3000)")
    results["Protected Resource Metadata"] = (
        test_protected_resource_metadata()
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests PASSED!")
    else:
        print("⚠️  Some tests FAILED")
        print("\nMake sure both servers are running:")
        print("  Terminal 1: python mock_oauth_server.py")
        print("  Terminal 2: python time_mcp_server.py")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
