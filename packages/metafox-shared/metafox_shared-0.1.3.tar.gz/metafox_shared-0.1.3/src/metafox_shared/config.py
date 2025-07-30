import os
import yaml
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# Determine the project root directory assuming config.py is located in src/metafox_shared/
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Path to the custom defaults YAML file, defaults to 'custom_defaults.yaml' in the project root
CUSTOM_DEFAULTS_PATH = os.getenv("CUSTOM_DEFAULTS_PATH", os.path.join(_PROJECT_ROOT, "custom_defaults.yaml"))

class Config:
    # API Configuration
    METAFOX_API_VERSION = os.getenv("METAFOX_API_VERSION", "1.0.0")
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_AUTH_ENABLED = os.getenv("API_AUTH_ENABLED", "False") == "True"
    API_ORIGINS = os.getenv("API_ORIGINS", "*").split(",")
    API_ALLOW_CREDENTIALS = os.getenv("API_ALLOW_CREDENTIALS", "True") == "True"
    API_ALLOW_METHODS = os.getenv("API_ALLOW_METHODS", "*").split(",")
    API_ALLOW_HEADERS = os.getenv("API_ALLOW_HEADERS", "*").split(",")
    
    # Keycloak Configuration
    KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "")
    KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "")
    KEYCLOAK_REALM_NAME = os.getenv("KEYCLOAK_REALM_NAME", "")
    KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    KEYCLOAK_AUTHORIZATION_URL = os.getenv("KEYCLOAK_AUTHORIZATION_URL", "")
    KEYCLOAK_TOKEN_URL = os.getenv("KEYCLOAK_TOKEN_URL", "")
    KEYCLOAK_REFRESH_URL = os.getenv("KEYCLOAK_REFRESH_URL", "")
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv("BROKER_URL", "pyamqp://guest@localhost:5672//")
    CELERY_RESULT_BACKEND = os.getenv("RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", str(os.cpu_count())))
    
    # MongoDB Configuration
    MONGO_DATABASE = os.getenv("MONGO_DB", "metafox")
    MONGO_TASKMETA_COLLECTION = os.getenv("MONGO_COLLECTION_TASK_META", "taskmeta")
    MONGO_AUTOMLJOBDETAILS_COLLECTION = os.getenv("MONGO_COLLECTION_AUTOML_JOB_DETAILS", "automl_job_details")
    MONGO_TASKINFO_COLLECTION = os.getenv("MONGO_COLLECTION_TASK_INFO", "task_info")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    
    # MLflow Configuration
    USE_MLFLOW = os.getenv("USE_MLFLOW", "False") == "True"
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # Load custom defaults from YAML file
    _custom_defaults = {}
    if os.path.exists(CUSTOM_DEFAULTS_PATH):
        try:
            with open(CUSTOM_DEFAULTS_PATH, 'r') as file:
                _custom_defaults = yaml.safe_load(file) or {}
            print(f"Custom defaults loaded from {CUSTOM_DEFAULTS_PATH}")
        except Exception as e:
            print(f"Error loading custom defaults from {CUSTOM_DEFAULTS_PATH}: {e}")
    else:
        print(f"Custom defaults file not found at {CUSTOM_DEFAULTS_PATH}. Using default configuration.")
    @classmethod
    def get_custom_default(cls, section: str, key: str, fallback: Any) -> Any:
        """
        Retrieves a custom default value from the loaded YAML configuration.
        Args:
            section (str): The section in the YAML file (e.g., 'tpot_job').
            key (str): The key for the specific default value.
            fallback (any): The value to return if the key is not found in the custom defaults.
        Returns:
            any: The custom default value or the fallback.
        """
        section_content = cls._custom_defaults.get(section)
        if isinstance(section_content, dict):
            return section_content.get(key, fallback)
        return fallback
    
    # Other Configuration
    DB_TYPE = os.getenv("DB_TYPE", "mongo")
    CHUNK_SIZE_READ = int(os.getenv("CHUNK_SIZE_READ", 1000))
    CHUNK_SIZE_WRITE = int(os.getenv("CHUNK_SIZE_WRITE", 1000))
    INTEGRATION_SMARTICITY = os.getenv("INTEGRATION_SMARTICITY", "False") == "True"
    TRAINER_ENDPOINT = os.getenv("TRAINER_ENDPOINT", "http://localhost:8000")
    TUS_STORAGE_ENDPOINT = os.getenv("TUS_STORAGE_ENDPOINT", "http://localhost:8000/files")