import pytest
import requests
from pymongo import MongoClient
from unittest.mock import Mock, patch
import os
import logging
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB Connection Parameters
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'calculator_db'
COLLECTION_NAME = 'calculations'

# Test cases with expanded validation
test_cases = [
    {
        "url": "http://localhost:8000/add/2/2", 
        "expected": 4, 
        "operation": "add",
        "validation": {
            "num1": 2,
            "num2": 2,
            "result": 4,
            "required_fields": ["operation", "num1", "num2", "result"]
        }
    }
]

def get_db_connection():
    """
    Establish a MongoDB connection with error handling
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        return db[COLLECTION_NAME]
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {e}")
        raise

def validate_database_record(record, case_validation):
    """
    Comprehensive data integrity validation
    """
    # Check record exists
    assert record is not None, "Record not found in database"
    
    # Validate required fields
    for field in case_validation['required_fields']:
        assert field in record, f"Missing required field: {field}"
    
    # Validate specific field values
    assert record['num1'] == case_validation['num1'], "First number mismatch"
    assert record['num2'] == case_validation['num2'], "Second number mismatch"
    assert record['result'] == case_validation['result'], "Result mismatch"
    
    # Check data types
    assert isinstance(record['num1'], int), "num1 must be an integer"
    assert isinstance(record['num2'], int), "num2 must be an integer"
    assert isinstance(record['result'], int), "result must be an integer"
    
    # Validate operation
    assert record['operation'] in ['add', 'subtract', 'multiply'], "Invalid operation"
    
    # Optional: Check timestamp or other metadata
    assert '_id' in record, "Record missing unique identifier"
    assert isinstance(record['_id'], str) or isinstance(record['_id'], ObjectId), "Invalid ID type"

def test_api_endpoints_with_data_integrity():
    """
    Test API endpoints with comprehensive data integrity checks
    """
    # Get database collection
    calculations_collection = get_db_connection()
    
    for case in test_cases:
        try:
            logger.debug(f"Testing URL: {case['url']}")
            
            # Make API request with timeout
            try:
                response = requests.get(case["url"], timeout=5)
            except requests.ConnectionError:
                logger.error("Could not connect to the API. Is the server running?")
                raise
            except requests.Timeout:
                logger.error("API request timed out")
                raise
            
            # Log full response for debugging
            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Content: {response.text}")
            
            # Verify API response
            assert response.status_code == 200, f"API call failed for {case['url']}"
            
            # Parse result
            result = response.json()["result"]
            assert result == case["expected"], f"Incorrect calculation result"
            
            # Validate database record
            db_record = calculations_collection.find_one({
                "operation": case["operation"],
                "result": result
            })
            
            # Comprehensive data integrity validation
            validate_database_record(db_record, {
                **case['validation'],
                'result': result
            })
            
            logger.info(f"Data integrity test passed for {case['url']}")
        
        except Exception as e:
            logger.error(f"Data integrity test failed: {e}")
            raise

if __name__ == "__main__":
    pytest.main()
