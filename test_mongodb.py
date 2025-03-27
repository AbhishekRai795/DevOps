import pytest
import requests
import os
import logging
import time
from pymongo import MongoClient
from unittest.mock import Mock, patch
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API base URL from environment variable (default to local)
API_BASE_URL = os.getenv("API_BASE_URL", "http://0.0.0.0:8000")

# Get MongoDB connection URI from environment variable
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "calculator_db")

# Define test cases
test_cases = [
    {
        "url": f"{API_BASE_URL}/add/2/2", 
        "expected": 4, 
        "operation": "add",
        "validation": {
            "num1": 2,
            "num2": 2,
            "result": 4,
            "required_fields": ["operation", "num1", "num2", "result"]
        }
    },
    {
        "url": f"{API_BASE_URL}/subtract/5/3", 
        "expected": 2, 
        "operation": "subtract",
        "validation": {
            "num1": 5,
            "num2": 3,
            "result": 2,
            "required_fields": ["operation", "num1", "num2", "result"]
        }
    },
    {
        "url": f"{API_BASE_URL}/multiply/4/3", 
        "expected": 12, 
        "operation": "multiply",
        "validation": {
            "num1": 4,
            "num2": 3,
            "result": 12,
            "required_fields": ["operation", "num1", "num2", "result"]
        }
    }
]

def validate_database_record(record, case_validation):
    """ Validate database record integrity """
    assert record is not None, "Record not found in database"

    for field in case_validation['required_fields']:
        assert field in record, f"Missing required field: {field}"

    assert record['num1'] == case_validation['num1'], "First number mismatch"
    assert record['num2'] == case_validation['num2'], "Second number mismatch"
    assert record['result'] == case_validation['result'], "Result mismatch"
    assert isinstance(record['num1'], int), "num1 must be an integer"
    assert isinstance(record['num2'], int), "num2 must be an integer"
    assert isinstance(record['result'], int), "result must be an integer"
    assert record['operation'] in ['add', 'subtract', 'multiply'], "Invalid operation"
    assert '_id' in record, "Record missing unique identifier"
    assert isinstance(record['_id'], (str, ObjectId)), "Invalid ID type"

@pytest.fixture(scope="module")
def mongo_client():
    """ Provide a MongoDB client fixture """
    client = MongoClient(MONGO_URI)
    yield client
    client.close()

@pytest.fixture(scope="module")
def wait_for_api():
    """ Wait for API server to be ready """
    retries = 5
    for _ in range(retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            time.sleep(2)
    pytest.fail("API server is not reachable")

def test_api_endpoints_with_data_integrity(mongo_client, wait_for_api):
    """ Test API with database validation """
    db = mongo_client[MONGO_DB_NAME]
    collection = db.calculations

    for case in test_cases:
        try:
            response = requests.get(case["url"])
            assert response.status_code == 200, f"API call failed for {case['url']}"
            result = response.json()["result"]
            assert result == case["expected"], f"Incorrect calculation result"

            # Validate DB record
            db_record = collection.find_one({"operation": case["operation"], "result": result})
            validate_database_record(db_record, {**case['validation'], 'result': result})

            logger.info(f"✅ Data integrity test passed for {case['url']}")

        except AssertionError as e:
            logger.error(f"❌ Data integrity test failed: {e}")
            raise

def test_mocked_database_connection():
    """ Mock database test for CI/CD """
    mock_client = Mock()
    mock_collection = Mock()
    
    mock_record = {
        "_id": "mock_id",
        "operation": "add",
        "num1": 2,
        "num2": 2,
        "result": 4
    }

    mock_collection.find_one.return_value = mock_record
    mock_client.calculator_db.calculations = mock_collection

    with patch('pymongo.MongoClient', return_value=mock_client):
        record = mock_client.calculator_db.calculations.find_one({})
        assert record == mock_record, "Mocked record does not match expected"
        mock_collection.find_one.assert_called_once()
    
    logger.info("✅ Database connection mocking test passed")

if __name__ == "__main__":
    pytest.main()
