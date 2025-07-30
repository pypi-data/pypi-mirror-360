#!/usr/bin/env python3
"""
Test script for bearer token authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "default_user@example.com"
PASSWORD = "default_password"


def test_bearer_auth():
    print("Testing Bearer Token Authentication...")

    # Step 1: Get bearer token
    print("\n1. Getting bearer token...")
    token_url = f"{BASE_URL}/api/v1/auth/token"

    token_data = {"username": USERNAME, "password": PASSWORD}

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()

        token_info = response.json()
        access_token = token_info["access_token"]
        token_type = token_info["token_type"]

        print(f"✓ Token obtained successfully")
        print(f"  Token type: {token_type}")
        print(f"  Token: {access_token[:50]}...")

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get token: {e}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")
        return

    # Step 2: Test protected endpoint with bearer token
    print("\n2. Testing protected endpoint with bearer token...")
    search_url = f"{BASE_URL}/api/v1/search"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        print("✓ Successfully accessed protected endpoint with bearer token")
        print(f"  Response status: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access protected endpoint: {e}")
        if hasattr(e, "response") and e.response:
            print(f"  Response: {e.response.text}")

    # Step 3: Test without token (should fail)
    print("\n3. Testing protected endpoint without token...")
    try:
        response = requests.get(search_url)
        print(f"✗ Unexpected success without token (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        if hasattr(e, "response") and e.response and e.response.status_code == 401:
            print("✓ Correctly rejected request without token")
        else:
            print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    test_bearer_auth()
