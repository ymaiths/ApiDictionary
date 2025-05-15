import sys
from pymongo.server_api import ServerApi
import pymongo
from fastapi import FastAPI, HTTPException
from main import get_slang_meaning

app = FastAPI()


uri = "mongodb+srv://admin:1234@thai-slang-dict.10ixf.mongodb.net/?retryWrites=true&w=majority&appName=thai-slang-dict"
# Create a new client and connect to the server
try:
    client = pymongo.MongoClient(uri, server_api=ServerApi('1'))
except pymongo.errors.ConfigurationError:
    print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
    sys.exit(1)

db = client["thai-slang-dict"]
slang_collection = db["slangs"]


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/find")
# func_name(param_name: param_data_type ) -> return_data_type
def find_slang(slang: str) -> str:
    result = slang_collection.find_one({"key": slang})
    if result is None:
        llm_result = get_slang_meaning(slang)
        slang_collection.insert_one({"key": slang, "value": llm_result})
        return llm_result
    else:
        return result["value"]
