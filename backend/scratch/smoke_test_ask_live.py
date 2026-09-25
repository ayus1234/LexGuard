import urllib.request
import json

def test_live_ask():
    url = "http://127.0.0.1:8000/api/v1/documents/ask"
    payload = {
        "document_id": "doc-saas-v42",
        "question": "What is the maximum aggregate liability cap and carve-outs?",
        "top_k": 5
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    print("Sending live POST request to /api/v1/documents/ask...")
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        print(f"HTTP Status: {resp.status}")
        print(f"Document ID: {body['document_id']}")
        print(f"Grounded: {body['grounded']}")
        print(f"Confidence: {body['confidence']}")
        print(f"Answer: {body['answer']}")
        print(f"Retrieved Sources: {len(body.get('retrieved_sources', []))}")
        print(f"Citations Count: {len(body.get('citations', []))}")
        for c in body.get("citations", []):
            print(f"  - Page {c.get('page')}, Section {c.get('section')}, Verified={c.get('verified')}")
            print(f"    Quote: {c.get('quoted_text')[:80]}...")
        print(f"Telemetry: {body.get('telemetry')}")

if __name__ == "__main__":
    test_live_ask()
