#!/usr/bin/env python3
"""
Simple test script for the Document Query API
"""
import requests
import json
import time
import sys

API_URL = "http://localhost:8080"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_query():
    """Test the main query endpoint"""
    print("Testing query endpoint...")

    # The example from the requirements
    payload = {
        "query": "is the home roof age compliant with the underwriting guide rules set in the training guide PDF?",
        "document_urls": [
            "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/wind_inspection_report.pdf",
            "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/Training-Guide-ATG-03052019_PDF.pdf",
        ],
    }

    # Submit query
    response = requests.post(f"{API_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    if response.status_code == 200 and "job_id" in result:
        job_id = result["job_id"]
        print(f"\nJob ID: {job_id}")
        print("Polling for results...")

        # Poll for results
        max_attempts = 60  # 5 minutes max
        for i in range(max_attempts):
            time.sleep(5)  # Wait 5 seconds between polls

            status_response = requests.get(f"{API_URL}/jobs/{job_id}")
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(f"\nAttempt {i+1}: Status = {job_status['status']}")

                if job_status["status"] == "completed":
                    print("\nQuery completed successfully!")
                    print(f"Answer: {job_status['result']['answer']}")
                    if "confidence_note" in job_status["result"]:
                        print(
                            f"\nConfidence Note: {job_status['result']['confidence_note']}"
                        )
                    if "metadata" in job_status["result"]:
                        print(
                            f"\nMetadata: {json.dumps(job_status['result']['metadata'], indent=2)}"
                        )
                    break
                elif job_status["status"] == "failed":
                    print(f"\nQuery failed: {job_status.get('error', 'Unknown error')}")
                    break
            else:
                print(f"Error checking job status: {status_response.status_code}")
                break
        else:
            print("\nTimeout waiting for results")


def test_sync_query():
    """Test the synchronous query endpoint"""
    print("\nTesting synchronous query endpoint...")

    # Simple test with smaller query
    payload = {
        "query": "What year was the roof installed?",
        "document_urls": [
            "https://storage.googleapis.com/ff-interview/backend-engineer-take-home-project/wind_inspection_report.pdf"
        ],
    }

    response = requests.post(f"{API_URL}/query-sync", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result['answer']}")
        if "confidence_note" in result:
            print(f"Confidence Note: {result['confidence_note']}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("Document Query API Test Script")
    print("=" * 50)

    try:
        # Test health first
        test_health()

        # Test main query
        test_query()

        # Optionally test sync endpoint
        # test_sync_query()

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Is the server running?")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
