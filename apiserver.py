from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
import motor.motor_asyncio
from config import collection
from fastapi_jwt_auth import AuthJWT
from fastapi import Depends

app = FastAPI()
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

@AuthJWT.load_config
def get_config():
    return Settings()

@app.post("/login")
async def login(username: str, password: str, Authorize: AuthJWT = Depends()):
    if username == "admin" and password == "password":
        access_token = Authorize.create_access_token(subject=username)
        return {"access_token": access_token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/protected")
async def protected_route(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"message": "You are authorized"}
class Calculation(BaseModel):
    num1: int
    num2: int

@app.post("/add/")
async def add_numbers(data: Calculation):
    result = {"num1": data.num1, "num2": data.num2, "sum": data.num1 + data.num2}
    insert_result = await collection.insert_one(result)
    return {"id": str(insert_result.inserted_id), **result}

@app.get("/get_results/")
async def get_results():
    results = []
    async for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results
