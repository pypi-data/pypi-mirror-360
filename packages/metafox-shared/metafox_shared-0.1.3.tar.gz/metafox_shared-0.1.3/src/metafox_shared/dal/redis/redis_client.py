from redis import Redis

from metafox_shared.config import Config
from metafox_shared.constants.api_constants import *
from metafox_shared.dal.idatastore import IDataStore

class RedisClient(IDataStore):
    """
    RedisClient is a class that provides an interface to interact with a Redis datastore.
    
    Methods:
        __init__() -> None:
            Initializes the Redis client and establishes a connection to the Redis server.
        set(key: str, value: str, collection_name: str) -> None:
            Sets a key-value pair in the Redis datastore. Raises an exception if the key already exists.
        get(key: str, collection_name: str) -> str:
            Retrieves the value associated with the given key from the Redis datastore. Raises an exception if the key does not exist.
        update(key: str, value: str, collection_name: str) -> None:
            Updates the value of an existing key in the Redis datastore. If the key does not exist, it sets the key-value pair.
        delete(key: str, collection_name: str) -> None:
            Deletes the key-value pair from the Redis datastore. Raises an exception if the key does not exist.
        get_automl_job_ids(collection_name: str) -> list:
            Retrieves a list of keys that match the CELERY_KEY_PREFIX from the Redis datastore.
        get_keys_by_pattern(pattern: str, collection_name: str) -> list:
            Retrieves a list of keys that match the given pattern from the Redis datastore.
        close() -> None:
            Closes the connection to the Redis server and prints a message indicating that the Redis client has been destroyed.
    """
    def __init__(self) -> None:
        self.redis = Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            password=Config.REDIS_PASSWORD,
            decode_responses=True
        )
        
        print("Redis connection established.")
        
    def set(self, key: str, value: str, collection_name: str) -> None:
        if self.redis.exists(key):
            raise Exception(f"Key {key} already exists.")
        
        self.redis.set(key, value)
        
    def get(self, key: str, collection_name: str) -> str:
        if self.redis.exists(key):
            return self.redis.get(key)
        
        raise Exception(f"Key {key} does not exist.")
        
    def update(self, key: str, value: str, collection_name: str) -> None:
        if self.redis.exists(key):
            self.redis.delete(key)
            self.redis.set(key, value)
        else:
            self.redis.set(key, value)
    
    def delete(self, key: str, collection_name: str) -> None:
        if self.redis.exists(key):
            self.redis.delete(key)
            return
        
        raise Exception(f"Key {key} does not exist.")
            
    def get_automl_job_ids(self, collection_name: str) -> list:
        cursor = '0'
        matching_keys = []
        
        while cursor != 0:
            cursor, keys = self.redis.scan(cursor = cursor)
            
            for key in keys:
                if key.startswith(CELERY_KEY_PREFIX):
                    matching_keys.append(key.replace(CELERY_KEY_PREFIX, ""))
                    
        return matching_keys
        
    def get_keys_by_pattern(self, pattern: str, collection_name: str) -> list:
        cursor = '0'
        redis_keys = []

        while cursor != 0:
            cursor, keys = self.redis.scan(cursor=cursor, match=pattern)
            redis_keys.extend(keys)

        return redis_keys

    def close(self) -> None:
        print("Redis client destroyed.")
        self.redis.close()