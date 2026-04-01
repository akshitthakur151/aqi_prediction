"""
test_api.py
Test the AQI prediction API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_single_prediction():
    """Test single prediction"""
    data = {
        "pm25": 50.0,
        "pm10": 100.0,
        "no2": 30.0,
        "so2": 15.0,
        "co": 1.5,
        "ozone": 40.0,
        "city": "Delhi",
        "state": "Delhi"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=data
        )

        result = response.json()
        print("\nPrediction Result:")
        print(f"  AQI: {result['aqi']}")
        print(f"  Category: {result['category']}")
        print(f"  Message: {result['message']}")
        return True
    except Exception as e:
        print(f"Prediction test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing AQI Prediction API...")

    # Test health check
    if test_health_check():
        print("✓ Health check passed")
    else:
        print("✗ Health check failed")
        exit(1)

    # Test prediction
    if test_single_prediction():
        print("✓ Prediction test passed")
    else:
        print("✗ Prediction test failed")
        exit(1)

    print("\n🎉 All tests passed! API is working correctly.")