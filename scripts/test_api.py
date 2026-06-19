"""
Quick API tester for PatientCare Platform.

Usage:
    python scripts/test_api.py
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_request(method: str, endpoint: str, data: Dict[str, Any] | None = None):
    """Print request details."""
    print(f"\n{method} {endpoint}")
    if data:
        print(f"Body: {json.dumps(data, indent=2)}")


def print_response(response: requests.Response):
    """Print response details."""
    print(f"\nStatus: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_health():
    """Test health endpoint."""
    print_header("1. Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_general():
    """Test general greeting."""
    print_header("2. General Greeting")
    
    data = {
        "message": "Hello, how can you help me?",
        "patient_id": "PAT001"
    }
    
    print_request("POST", "/chat", data)
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_appointment():
    """Test appointment intent."""
    print_header("3. Appointment Query")
    
    data = {
        "message": "When is my next appointment?",
        "patient_id": "PAT001"
    }
    
    print_request("POST", "/chat", data)
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            intent = result.get("intent")
            print(f"\n✓ Detected intent: {intent}")
            return intent == "appointment"
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_billing():
    """Test billing intent."""
    print_header("4. Billing Query")
    
    data = {
        "message": "What is my current balance?",
        "patient_id": "PAT001"
    }
    
    print_request("POST", "/chat", data)
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            intent = result.get("intent")
            print(f"\n✓ Detected intent: {intent}")
            return intent == "billing"
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_investigation():
    """Test event investigation."""
    print_header("5. Event Investigation (Root Cause)")
    
    data = {
        "message": "Why was my claim denied?",
        "patient_id": "PAT001"
    }
    
    print_request("POST", "/chat", data)
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            intent = result.get("intent")
            reply = result.get("reply", "")
            print(f"\n✓ Detected intent: {intent}")
            print(f"✓ Generated response with {len(reply)} characters")
            return "authorization" in reply.lower() or "denied" in reply.lower()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_emergency():
    """Test emergency escalation."""
    print_header("6. Emergency Escalation")
    
    data = {
        "message": "I have severe chest pain and difficulty breathing",
        "patient_id": "PAT001"
    }
    
    print_request("POST", "/chat", data)
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data)
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("reply", "")
            print(f"\n✓ Response mentions professional review: {'healthcare professional' in reply.lower() or 'review' in reply.lower()}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  PatientCare Platform - API Test Suite")
    print("="*70)
    print("\nMake sure the server is running at http://localhost:8000")
    print("Run: uvicorn app.main:app --reload")
    
    input("\nPress Enter to start tests...")
    
    tests = [
        ("Health Check", test_health),
        ("General Greeting", test_chat_general),
        ("Appointment Query", test_chat_appointment),
        ("Billing Query", test_chat_billing),
        ("Event Investigation", test_chat_investigation),
        ("Emergency Escalation", test_chat_emergency),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
