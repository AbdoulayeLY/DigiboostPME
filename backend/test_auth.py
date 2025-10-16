"""
Script de test pour l'authentification JWT.
"""
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "http://localhost:8000/api/v1"


def test_login():
    """Test de l'endpoint de login."""
    print("\n=== TEST LOGIN ===")

    url = f"{BASE_URL}/auth/login"
    data = json.dumps({
        "email": "admin@digiboost.sn",
        "password": "password123"
    }).encode('utf-8')

    req = Request(url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Status: {response.status}")
            print(f"✓ Access Token: {result['access_token'][:50]}...")
            print(f"✓ Refresh Token: {result['refresh_token'][:50]}...")
            print(f"✓ Token Type: {result['token_type']}")
            return result
    except HTTPError as e:
        print(f"✗ Error {e.code}: {e.read().decode('utf-8')}")
        return None


def test_me(access_token):
    """Test de l'endpoint /me (utilisateur courant)."""
    print("\n=== TEST GET CURRENT USER ===")

    url = f"{BASE_URL}/auth/me"
    req = Request(url, headers={
        'Authorization': f'Bearer {access_token}'
    })

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Status: {response.status}")
            print(f"✓ User ID: {result['id']}")
            print(f"✓ Email: {result['email']}")
            print(f"✓ Full Name: {result['full_name']}")
            print(f"✓ Role: {result['role']}")
            print(f"✓ Tenant ID: {result['tenant_id']}")
            return result
    except HTTPError as e:
        print(f"✗ Error {e.code}: {e.read().decode('utf-8')}")
        return None


def test_refresh(refresh_token):
    """Test de l'endpoint de refresh token."""
    print("\n=== TEST REFRESH TOKEN ===")

    url = f"{BASE_URL}/auth/refresh"
    data = json.dumps({
        "refresh_token": refresh_token
    }).encode('utf-8')

    req = Request(url, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Status: {response.status}")
            print(f"✓ New Access Token: {result['access_token'][:50]}...")
            print(f"✓ New Refresh Token: {result['refresh_token'][:50]}...")
            return result
    except HTTPError as e:
        print(f"✗ Error {e.code}: {e.read().decode('utf-8')}")
        return None


def test_invalid_token():
    """Test avec un token invalide."""
    print("\n=== TEST INVALID TOKEN ===")

    url = f"{BASE_URL}/auth/me"
    req = Request(url, headers={
        'Authorization': 'Bearer invalid_token_here'
    })

    try:
        with urlopen(req) as response:
            print(f"✗ Should have failed but got: {response.status}")
    except HTTPError as e:
        if e.code == 401:
            print(f"✓ Correctly rejected invalid token with 401")
        else:
            print(f"✗ Unexpected error {e.code}: {e.read().decode('utf-8')}")


if __name__ == "__main__":
    print("="*60)
    print("TEST AUTHENTIFICATION JWT - Digiboost PME")
    print("="*60)

    # Test 1: Login
    tokens = test_login()
    if not tokens:
        print("\n✗ Login failed, stopping tests")
        sys.exit(1)

    # Test 2: Get current user
    user = test_me(tokens['access_token'])
    if not user:
        print("\n✗ Get current user failed")

    # Test 3: Refresh token
    new_tokens = test_refresh(tokens['refresh_token'])
    if not new_tokens:
        print("\n✗ Refresh token failed")

    # Test 4: Invalid token
    test_invalid_token()

    print("\n" + "="*60)
    print("TESTS TERMINES")
    print("="*60)
