"""
Production Q&A endpoint test script.
Tests the deployed backend directly to verify doc-saas-v42 indexing and Q&A functionality.
"""

import requests
import json
import sys

BACKEND_URL = "https://lexguard-backend-7yxz.onrender.com"

def test_health():
    """Test backend health endpoint."""
    print("=" * 80)
    print("TESTING BACKEND HEALTH")
    print("=" * 80)
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_qa_endpoint():
    """Test Q&A endpoint with doc-saas-v42."""
    print("\n" + "=" * 80)
    print("TESTING Q&A ENDPOINT")
    print("=" * 80)
    
    payload = {
        "document_id": "doc-saas-v42",
        "question": "What is the maximum aggregate liability cap and what are the carve-outs?",
        "top_k": 5,
        "session_id": "test-session-12345"
    }
    
    print(f"Request URL: {BACKEND_URL}/api/v1/documents/ask")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/documents/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"Answer: {data.get('answer', 'N/A')[:200]}...")
            print(f"Grounded: {data.get('grounded')}")
            print(f"Confidence: {data.get('confidence')}")
            print(f"Citations: {len(data.get('citations', []))}")
            print(f"Telemetry: {data.get('telemetry')}")
            return True
        else:
            print(f"\n❌ FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except requests.Timeout:
        print(f"❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_retrieval_endpoint():
    """Test retrieval endpoint to check if doc-saas-v42 is indexed."""
    print("\n" + "=" * 80)
    print("TESTING RETRIEVAL ENDPOINT (Vector Store Check)")
    print("=" * 80)
    
    payload = {
        "document_id": "doc-saas-v42",
        "query": "liability cap",
        "top_k": 3
    }
    
    print(f"Request URL: {BACKEND_URL}/api/v1/retrieval/search")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/retrieval/search",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Document is indexed!")
            print(f"Grounding status: {data.get('grounding_status')}")
            print(f"Results found: {len(data.get('results', []))}")
            if data.get('results'):
                first_result = data['results'][0]
                print(f"First result similarity: {first_result.get('similarity_score')}")
                print(f"First result text: {first_result.get('text', '')[:150]}...")
            return True
        else:
            print(f"\n❌ Document not indexed or retrieval failed")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"\n{'#' * 80}")
    print("LEXGUARD PRODUCTION BACKEND DIAGNOSTIC TEST")
    print(f"Backend: {BACKEND_URL}")
    print(f"{'#' * 80}\n")
    
    results = {
        "health": test_health(),
        "retrieval": test_retrieval_endpoint(),
        "qa": test_qa_endpoint()
    }
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.ljust(20)}: {status}")
    
    print("\n" + "=" * 80)
    if all(results.values()):
        print("✅ ALL TESTS PASSED - Production backend is functional")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        sys.exit(1)
