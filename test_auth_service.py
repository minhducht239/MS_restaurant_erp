#!/usr/bin/env python3
"""
Test Auth Service Endpoints
Test authentication endpoints for restaurant ERP auth service
"""
import requests
import json
import sys
from datetime import datetime

# Auth service URL - Using DigitalOcean App Platform default URL
BASE_URL = "https://restaurant-erp-b24no.ondigitalocean.app"
# BASE_URL = "http://minhducht239.servebeer.com"  # Custom domain has DNS issues
TEST_USER = {
    "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%H%M%S')}@restaurant.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
}

def print_test_result(test_name, success, message, response=None):
    """Print formatted test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}: {message}")
    if response and hasattr(response, 'status_code'):
        print(f"   Status Code: {response.status_code}")
    if response and hasattr(response, 'text'):
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        except:
            print(f"   Response: {response.text[:200]}...")
    print("-" * 60)

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        print(f"   Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            print_test_result("Health Check", True, "Service is healthy", response)
            return True
        else:
            print_test_result("Health Check", False, f"Status: {response.status_code}", response)
            return False
    except Exception as e:
        print_test_result("Health Check", False, f"Connection error: {str(e)}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/docs/", timeout=10)
        if response.status_code == 200:
            print_test_result("API Docs", True, "API documentation accessible", response)
            return True
        else:
            print_test_result("API Docs", False, f"Unexpected status code", response)
            return False
    except Exception as e:
        print_test_result("API Docs", False, f"Connection error: {str(e)}")
        return False

def test_registration():
    """Test user registration"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json=TEST_USER,
            timeout=10
        )
        if response.status_code == 201:
            print_test_result("User Registration", True, "User created successfully", response)
            return True, response.json()
        else:
            print_test_result("User Registration", False, f"Registration failed", response)
            return False, None
    except Exception as e:
        print_test_result("User Registration", False, f"Connection error: {str(e)}")
        return False, None

def test_login():
    """Test user login"""
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=login_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if 'access' in data and 'refresh' in data:
                print_test_result("User Login", True, "Login successful, tokens received", response)
                return True, data
            else:
                print_test_result("User Login", False, "No tokens in response", response)
                return False, None
        else:
            print_test_result("User Login", False, f"Login failed", response)
            return False, None
    except Exception as e:
        print_test_result("User Login", False, f"Connection error: {str(e)}")
        return False, None

def test_protected_endpoint(access_token):
    """Test protected endpoint with JWT token"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(
            f"{BASE_URL}/api/auth/user/",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print_test_result("Protected Endpoint", True, "JWT authentication working", response)
            return True
        else:
            print_test_result("Protected Endpoint", False, f"Protected endpoint failed", response)
            return False
    except Exception as e:
        print_test_result("Protected Endpoint", False, f"Connection error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Auth Service Endpoints")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"👤 Test User: {TEST_USER['username']}")
    print("=" * 60)
    
    # Test 1: Health Check
    if not test_health():
        print("❌ Service not healthy, stopping tests")
        return False
    
    # Test 2: API Documentation
    test_api_docs()
    
    # Test 3: User Registration
    reg_success, user_data = test_registration()
    if not reg_success:
        print("❌ Registration failed, skipping login tests")
        return False
    
    # Test 4: User Login
    login_success, tokens = test_login()
    if not login_success:
        print("❌ Login failed, skipping protected endpoint test")
        return False
    
    # Test 5: Protected Endpoint
    if tokens and 'access' in tokens:
        test_protected_endpoint(tokens['access'])
    
    print("\n🎉 All tests completed!")
    return True

if __name__ == "__main__":
    main()