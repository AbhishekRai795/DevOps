from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = 'calculator_db'
COLLECTION_NAME = 'calculations'

try:
    # Initialize MongoDB Client
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    calculations_collection = db[COLLECTION_NAME]
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

# Initialize the FastAPI app
app = FastAPI()

# Pydantic Model for Calculation
class Calculation(BaseModel):
    operation: str
    num1: int
    num2: int
    result: int
    
    class Config:
        # Allow conversion of MongoDB's ObjectId
        json_encoders = {
            ObjectId: str
        }

# Root endpoint
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Addition endpoint with database logging
@app.get("/add/{num1}/{num2}")
def add(num1: int, num2: int):
    """
    Adds two numbers and logs the calculation in MongoDB.
    """
    try:
        result = num1 + num2
        
        # Create calculation document
        calculation = {
            "operation": "add",
            "num1": num1,
            "num2": num2,
            "result": result
        }
        
        # Insert calculation into MongoDB
        calculations_collection.insert_one(calculation)
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in add endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Subtraction endpoint with database logging
@app.get("/subtract/{num1}/{num2}")
def subtract(num1: int, num2: int):
    """
    Subtracts the second number from the first and logs the calculation.
    """
    try:
        result = num1 - num2
        
        calculation = {
            "operation": "subtract",
            "num1": num1,
            "num2": num2,
            "result": result
        }
        
        calculations_collection.insert_one(calculation)
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in subtract endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Multiplication endpoint with database logging
@app.get("/multiply/{num1}/{num2}")
def multiply(num1: int, num2: int):
    """
    Multiplies two numbers and logs the calculation.
    """
    try:
        result = num1 * num2
        
        calculation = {
            "operation": "multiply",
            "num1": num1,
            "num2": num2,
            "result": result
        }
        
        calculations_collection.insert_one(calculation)
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Error in multiply endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint to retrieve calculation history
@app.get("/history")
def get_calculation_history():
    """
    Retrieves the last 10 calculations from MongoDB.
    """
    try:
        # Retrieve last 10 calculations, sorted by most recent first
        history = list(calculations_collection.find().sort('_id', -1).limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for item in history:
            item['_id'] = str(item['_id'])
        
        return {"history": history}
    except Exception as e:
        logger.error(f"Error in history endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apiserver:app", host="0.0.0.0", port=8000, reload=True)
