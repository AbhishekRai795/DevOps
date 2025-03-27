import pytest
import asyncio
import motor.motor_asyncio
from apiserver import app
from fastapi.testclient import TestClient

# Setup Test Client
client = TestClient(app)

# MongoDB Test Database
MONGO_URI = "mongodb://localhost:27017/"
TEST_DB_NAME = "test_db"

@pytest.fixture(scope="module")
def mongo_client():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[TEST_DB_NAME]
    yield db
    client.drop_database(TEST_DB_NAME)  # Cleanup after tests

@pytest.mark.asyncio
async def test_add_numbers(mongo_client):
    response = client.post("/add/", json={"num1": 10, "num2": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 15

    # Verify Data in MongoDB
    result = await mongo_client["numbers"].find_one({"num1": 10, "num2": 5})
    assert result["result"] == 15

@pytest.mark.asyncio
async def test_get_results(mongo_client):
    response = client.get("/get_results/")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0  # Ensure data is fetched
