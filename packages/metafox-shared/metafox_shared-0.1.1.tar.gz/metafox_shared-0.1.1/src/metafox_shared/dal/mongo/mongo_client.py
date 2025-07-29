from datetime import datetime

from pymongo.database import Database
from pymongo.collection import Collection
from pymongo import MongoClient as PyMongoClient

from metafox_shared.config import Config
from metafox_shared.dal.idatastore import IDataStore

class MongoClient(IDataStore):
    """
    A client for interacting with a MongoDB database.
    
    Methods:
        __init__() -> None
            Initializes the MongoDB client and establishes a connection to the database.
        set(key: str, value: str, collection_name: str) -> None
            Inserts a document with the specified key and value into the specified collection.
        get(key: str, collection_name: str) -> str
            Retrieves the value of the document with the specified key from the specified collection.
        update(key: str, value: str, collection_name: str) -> None
            Updates the value of the document with the specified key in the specified collection.
        delete(key: str, collection_name: str) -> None
            Deletes the document with the specified key from the specified collection.
        get_automl_job_ids(collection_name: str) -> list
            Retrieves a list of all document IDs from the specified collection.
        get_keys_by_pattern(pattern: str, collection_name: str) -> list
            Retrieves a list of document IDs that match the specified pattern from the specified collection.
        close() -> None
            Closes the MongoDB connection.
        __get_collection(collection_name: str) -> Collection
            Retrieves the specified collection from the database.
    """
    def __init__(self) -> None:        
        self.client: PyMongoClient = PyMongoClient(Config.MONGO_URI)
        self.db: Database = self.client.get_database(Config.MONGO_DATABASE)
        
        print("MongoDB connection established.")
    
    def set(self, key: str, value: str, collection_name: str) -> None:
        collection = self.__get_collection(collection_name)
        collection.insert_one({
            "_id": key, 
            "value": value, 
            "created_at": datetime.now()
        })

    def get(self, key: str, collection_name: str) -> str:
        collection = self.__get_collection(collection_name)
        document = collection.find_one({"_id": key})
        return document["value"] if document else None

    def update(self, key: str, value: str, collection_name: str) -> None:
        collection = self.__get_collection(collection_name)
        collection.update_one({"_id": key}, {"$set": {"value": value}})

    def delete(self, key: str, collection_name: str) -> None:
        collection = self.__get_collection(collection_name)
        collection.delete_one({"_id": key})

    def get_automl_job_ids(self, collection_name: str) -> list:
        collection = self.__get_collection(collection_name)
        return [doc["_id"] for doc in collection.find({}, {"_id": 1})]

    def get_keys_by_pattern(self, pattern: str, collection_name) -> list:
        collection = self.__get_collection(collection_name)
        regex_pattern = f".*{pattern}.*"
        return [doc["_id"] for doc in collection.find({"_id": {"$regex": regex_pattern}})]
    
    def close(self) -> None:
        print("Closing MongoDB connection...")
        self.client.close()
        
    def __get_collection(self, collection_name: str) -> Collection:
        return self.db.get_collection(collection_name)