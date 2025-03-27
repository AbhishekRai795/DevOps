import pytest
import requests
from pymongo import MongoClient
from unittest.mock import Mock, patch
import os
import logging
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    },
    {
        "url": "http://localhost:8000/subtract/5/3", 
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
        "url": "http://localhost:8000/multiply/4/3", 
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
    for case in test_cases:
        try:
            # Make API request
            response = requests.get(case["url"])
            
            # Verify API response
            assert response.status_code == 200, f"API call failed for {case['url']}"
            
            result = response.json()["result"]
            assert result == case["expected"], f"Incorrect calculation result"
            
            # Validate database record
            db_record = MongoClient().calculator_db.calculations.find_one({
                "operation": case["operation"],
                "result": result
            })
            
            # Comprehensive data integrity validation
            validate_database_record(db_record, {
                **case['validation'],
                'result': result
            })
            
            logger.info(f"Data integrity test passed for {case['url']}")
        
        except AssertionError as e:
            logger.error(f"Data integrity test failed: {e}")
            raise

def test_mocked_database_connection():
    """
    Demonstrate mocking of database connection
    """
    # Mock MongoDB client and collection
    mock_client = Mock()
    mock_collection = Mock()
    
    # Simulate a database record
    mock_record = {
        "_id": "mock_id",
        "operation": "add",
        "num1": 2,
        "num2": 2,
        "result": 4
    }
    
    # Configure mock to return predefined record
    mock_collection.find_one.return_value = mock_record
    mock_client.calculator_db.calculations = mock_collection
    
    # Patch the MongoClient to use our mock
    with patch('pymongo.MongoClient', return_value=mock_client):
        # Simulate database interaction
        record = mock_client.calculator_db.calculations.find_one({})
        
        # Validate mocked record
        assert record == mock_record, "Mocked record does not match expected"
        mock_collection.find_one.assert_called_once()
    
    logger.info("Database connection mocking test passed")

if __name__ == "__main__":
    pytest.main()
