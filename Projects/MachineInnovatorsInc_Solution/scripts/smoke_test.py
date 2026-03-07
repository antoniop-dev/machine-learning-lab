#!/usr/bin/env python
"""
Smoke test to verify the running FastAPI backend.

This script makes HTTP requests to localhost:8000 to ensure that
the real model inference executes successfully.

Usage:
    Ensure the server is running: `python scripts/serve.py`
    Then run: `python scripts/smoke_test.py`
"""

import sys
import time

try:
    import httpx
except ImportError:
    print("Error: httpx is not installed. Run `pip install httpx` first.")
    sys.exit(1)

API_URL = "http://localhost:8000/api/v1"


def main():
    print("🚬 Starting API Smoke Tests...")
    
    client = httpx.Client(timeout=10.0)
    
    # 1. Test Health Check
    print(f"Checking health at {API_URL}/health ...")
    try:
        r = client.get(f"{API_URL}/health")
        if r.status_code == 200:
            print(f"✅ Health OK. Status: {r.json()['status']}, Model: {r.json()['model']}")
        else:
            print(f"❌ Health check failed with status {r.status_code}: {r.text}")
            sys.exit(1)
    except httpx.RequestError as e:
        print(f"❌ Connection failed: {e}. Is the server running on port 8000?")
        sys.exit(1)

    # 2. Test Prediction Forward Pass
    test_texts = [
        "I absolutely love this new feature, amazing work!",
        "The application crashed immediately upon opening. Terrible.",
        "The button is located on the top left of the screen.",
    ]

    for text in test_texts:
        print(f"\nSending prediction request for: '{text}' ...")
        t0 = time.time()
        
        r = client.post(f"{API_URL}/predict", json={"text": text})
        
        elapsed = time.time() - t0
        
        if r.status_code == 200:
            data = r.json()
            label = data["label"]
            score = data["scores"][label]
            print(f"✅ Success! ({elapsed:.2f}s) -> Predicted: {label.upper()} ({score*100:.1f}%)")
        else:
            print(f"❌ Prediction failed with status {r.status_code}: {r.text}")
            sys.exit(1)

    print("\n🎉 All smoke tests passed! The inference API is rock solid.")

if __name__ == "__main__":
    main()
