import uuid
from abc import ABC, abstractmethod
from datetime import datetime

class IDataStore(ABC):
    """
    An abstract base class that defines the interface for a datastore.
    This class provides a set of abstract methods that must be implemented by any concrete
    datastore class. These methods cover basic CRUD operations, as well as additional
    functionalities such as retrieving AutoML job IDs and keys by pattern, and closing the
    datastore connection.
    
    Methods:
        - set(key: str, value: str, collection_name: str) -> None:
        - get(key: str, collection_name: str) -> str:
        - update(key: str, value: str, collection_name: str) -> None:
        - delete(key: str, collection_name: str) -> None:
        - get_automl_job_ids(collection_name: str) -> list:
        - get_keys_by_pattern(pattern: str, collection_name: str) -> list:
        - close() -> None:
        - generate_unique_job_key() -> str:
    """
    @abstractmethod
    def set(self, key: str, value: str, collection_name: str) -> None:
        """
        Sets a value in the specified collection with the given key.

        Args:
            key (str): The key under which the value will be stored.
            value (str): The value to be stored.
            collection_name (str): The name of the collection where the key-value pair will be stored. In some datastores, this argument may be ignored (e.g., Redis) but is included for consistency.

        Returns:
            None
        """
        pass
    
    @abstractmethod
    def get(self, key: str, collection_name: str) -> str:
        """
        Retrieve a value from the datastore based on the given key and collection name.

        Args:
            key (str): The key to look up in the datastore.
            collection_name (str): The name of the collection where the key is stored. In some datastores, this argument may be ignored (e.g., Redis) but is included for consistency.

        Returns:
            str: The value associated with the given key in the specified collection.
        """
        pass
    
    @abstractmethod
    def update(self, key: str, value: str, collection_name: str) -> None:
        """
        Update the value associated with a given key in a specified collection.

        Args:
            key (str): The key for which the value needs to be updated.
            value (str): The new value to be associated with the key.
            collection_name (str): The name of the collection where the key-value pair is stored. In some datastores, this argument may be ignored (e.g., Redis) but is included for consistency.

        Returns:
            None
        """
        pass
    
    @abstractmethod
    def delete(self, key: str, collection_name: str) -> None:
        """
        Deletes an item from the specified collection in the datastore.

        Args:
            key (str): The key of the item to delete.
            collection_name (str): The name of the collection from which to delete the item. In some datastores, this argument may be ignored (e.g., Redis) but is included for consistency.

        Returns:
            None
        """
        pass
    
    @abstractmethod
    def get_automl_job_ids(self, collection_name: str) -> list:
        """
        Retrieve a list of AutoML job IDs from the specified collection.

        Args:
            collection_name (str): The name of the collection from which to retrieve AutoML job IDs. In some datastores, this argument may be ignored (e.g., Redis) but is included for consistency.

        Returns:
            list: A list of AutoML job IDs.
        """
        pass
    
    @abstractmethod
    def get_keys_by_pattern(self, pattern: str, collection_name: str) -> list:
        """
        Retrieve a list of keys from a specified collection that match a given pattern.

        Args:
            pattern (str): The pattern to match keys against.
            collection_name (str): The name of the collection to search within. In some datastores, this argument may be ignored (e.g., Redis) but is included for consistency.

        Returns:
            list: A list of keys that match the specified pattern.
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Closes the datastore connection.

        This method should be implemented by subclasses to handle the
        necessary steps for closing the connection to the datastore.
        """
        pass
    
    def generate_unique_job_key(self) -> str:
        """
        Generates a unique job key.

        This method creates a unique identifier by combining a UUID (Universally Unique Identifier)
        with the current timestamp. The UUID ensures global uniqueness, while the timestamp
        provides a human-readable component indicating when the key was generated.

        Returns:
            str: A unique job key in the format 'UUID-TIMESTAMP'.
        """
        unique_id = uuid.uuid4()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{unique_id}-{timestamp}"