#!/usr/bin/env python3
"""
Simple test script for AutoRescue API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("+ Health check passed")
            return True
        else:
            print(f"- Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"- Health check error: {e}")
        return False

def test_login():
    """Test admin login"""
    print("Testing admin login...")
    try:
        data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/login", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("+ Admin login successful")
                return True
            else:
                print(f"- Admin login failed: {result.get('message')}")
                return False
        else:
            print(f"- Login request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"- Login error: {e}")
        return False

def test_create_alert():
    """Test creating a test alert"""
    print("Testing alert creation...")
    try:
        # First login to get session
        session = requests.Session()
        login_data = {"username": "admin", "password": "admin123"}
        login_response = session.post(f"{BASE_URL}/login", json=login_data)
        
        if login_response.status_code != 200:
            print("- Login failed for alert test")
            return False
        
        # Create test alert
        alert_data = {
            "alert_type": "Test Alert",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "details": "Test alert from API test script",
            "impact_magnitude": 30.5
        }
        
        response = session.post(f"{BASE_URL}/api/alerts", json=alert_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("+ Alert creation successful")
                return True
            else:
                print(f"- Alert creation failed: {result.get('message')}")
                return False
        else:
            print(f"- Alert creation request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"- Alert creation error: {e}")
        return False

def test_get_alerts():
    """Test retrieving alerts"""
    print("Testing alert retrieval...")
    try:
        session = requests.Session()
        login_data = {"username": "admin", "password": "admin123"}
        session.post(f"{BASE_URL}/login", json=login_data)
        
        response = session.get(f"{BASE_URL}/api/alerts")
        if response.status_code == 200:
            alerts = response.json()
            print(f"+ Retrieved {len(alerts)} alerts")
            return True
        else:
            print(f"- Alert retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"- Alert retrieval error: {e}")
        return False

def main():
    """Run all tests"""
    print("AutoRescue API Test Suite")
    print("=" * 30)
    
    tests = [
        test_health_check,
        test_login,
        test_create_alert,
        test_get_alerts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 30)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("*** All tests passed! ***")
    else:
        print("*** Some tests failed ***")

if __name__ == "__main__":
    main()
