from fastapi import FastAPI,HTTPException
app = FastAPI()

import pymongo
from pymongo.server_api import ServerApi
import sys

uri = "mongodb+srv://admin:1234@thai-slang-dict.10ixf.mongodb.net/?retryWrites=true&w=majority&appName=thai-slang-dict"
# Create a new client and connect to the server
try:
    client = pymongo.MongoClient(uri, server_api=ServerApi('1'))
except pymongo.errors.ConfigurationError:
    print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
    sys.exit(1)
    
db = client["thai-slang-dict"]
slang_collection=db["slangs"]

items = []
@app.get("/")
def root():
    return {"Hello":"World"}

@app.get("/find")
def find_slang(slang: str) -> str: #func_name(param_name: param_data_type ) -> return_data_type
    result = slang_collection.find_one({"key": slang})
    if result is None:
        raise HTTPException(status_code=404, detail="Slang not found")
    return result["value"]

@app.post("/save")
def save_slang(slang,meaning: str):
    slang_collection.insert_one({"key": slang, "value": meaning})
    return "saving complete"

@app.delete("/delete")
def delete_slang(slang: str):
    result = slang_collection.delete_one({"key": slang})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Slang not found")
    return "Slang deleted successfully"
