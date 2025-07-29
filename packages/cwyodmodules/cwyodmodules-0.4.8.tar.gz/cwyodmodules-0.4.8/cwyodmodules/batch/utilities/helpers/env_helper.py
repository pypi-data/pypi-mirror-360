import json
import os

import threading                        
# from dotenv import load_dotenv

from ..helpers.config.conversation_flow import ConversationFlow

from mgmt_config import logger, identity, keyvault, head_keyvault



class EnvHelper:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super(EnvHelper, cls).__new__(cls)
                instance.__load_config()
                cls._instance = instance
            return cls._instance
        
    @logger.trace_function(log_execution=True, log_args=False, log_result=False)
    def __load_config(self, **kwargs) -> None:

        logger.info("Initializing EnvHelper!")
        logger.info(f"AZURE_CLIENT_ID: {os.getenv('AZURE_CLIENT_ID', 'Not set')}")
        logger.info(f"key_vault_uri: {os.getenv('key_vault_uri', 'Not set')}")
        logger.info(f"head_key_vault_uri: {os.getenv('head_key_vault_uri', 'Not set')}")
        
        if not keyvault:
            raise ValueError("keyvault is not configured. Please set 'key_vault_uri' environment variable.")
        
        if not head_keyvault:
            raise ValueError("head_keyvault is not configured. Please set 'head_key_vault_uri' environment variable.")

        # Wrapper for Azure Key Vault
        os.environ["APPLICATIONINSIGHTS_ENABLED"] = "true"

        # keyvault = SecretHelper(
        #     keyvault_uri="https://www.kv-main-cwyod-res1.vault.azure.net/"
        # )
        # head_keyvault = SecretHelper(
        #     keyvault_uri="https://www.kv-main-cwyod-hd-res1.vault.azure.net/"
        # )

        # Set AZURE_CLIENT_ID from environment variable
        self.AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")

        self.LOGLEVEL = keyvault.get_secret("logging-level")
        self.LOG_EXECUTION = self.get_env_var_bool(
                "LOG_EXECUTION", "True"
            )
        self.LOG_ARGS = self.get_env_var_bool(
                "LOG_ARGS", "True"
            )
        self.LOG_RESULT = self.get_env_var_bool(
                "LOG_RESULT", "True"
            )

        # Azure
        self.AZURE_SUBSCRIPTION_ID = keyvault.get_secret("subscription-id")
        self.AZURE_RESOURCE_GROUP = keyvault.get_secret("resource-group-name")
        self.AZURE_HEAD_RESOURCE_GROUP = head_keyvault.get_secret(
            "resource-group-name"
        )
        self.AZURE_RESOURCE_ENVIRONMENT = keyvault.get_secret(
            "resource-group-environment"
        )
        self.AZURE_RESOURCE_PRIVATE = (
            keyvault.get_secret("run-private-endpoint").lower() == "true"
        )
        self.PROJECT_CODE = keyvault.get_secret("project-code")
        self.APP_NAME = os.getenv("REFLECTION_NAME", "Default")
        self.POSTGRESQL_NAME = (
            f"psql-main-{self.PROJECT_CODE}-{self.AZURE_RESOURCE_ENVIRONMENT}"
        )
        self.AZURE_AUTH_TYPE = "rbac"
        access_information = identity.get_token_provider(scopes="https://cognitiveservices.azure.com/.default")
        self.AZURE_TOKEN_PROVIDER = access_information
        self.AZURE_BLOB_ACCOUNT_NAME = (
            f"stqueue{self.PROJECT_CODE}{self.AZURE_RESOURCE_ENVIRONMENT}"
        )
        self.AZURE_STORAGE_ACCOUNT_ENDPOINT = (
            f"https://{self.AZURE_BLOB_ACCOUNT_NAME}.blob.core.windows.net/"
        )

        self.AZURE_FUNCTION_APP_ENDPOINT = keyvault.get_secret(
            f"func-backend-{self.PROJECT_CODE}-{self.AZURE_RESOURCE_ENVIRONMENT}-endpoint"
        )
        self.AZURE_BLOB_CONTAINER_NAME = "documents"
        self.DOCUMENT_PROCESSING_QUEUE_NAME = "doc-processing"

        # PostgreSQL configuration - Direct setup without database type switching
        self.AZURE_POSTGRES_SEARCH_TOP_K = 5
        
        # Load PostgreSQL connection details
        azure_postgresql_info = self.get_info_from_env("AZURE_POSTGRESQL_INFO", "")
        if azure_postgresql_info:
            self.POSTGRESQL_USER = azure_postgresql_info.get("user", "")
            self.POSTGRESQL_DATABASE = azure_postgresql_info.get("dbname", "")
            self.POSTGRESQL_HOST = azure_postgresql_info.get("host", "")
        else:
            self.POSTGRESQL_USER = "cwyod_project_uai"
            self.POSTGRESQL_DATABASE = keyvault.get_secret(
                f"{self.POSTGRESQL_NAME}-default-database-name"
            )
            self.POSTGRESQL_HOST = keyvault.get_secret(
                f"{self.POSTGRESQL_NAME}-server-name"
            )
        
        # PostgreSQL feature configuration
        self.AZURE_SEARCH_USE_INTEGRATED_VECTORIZATION = False
        self.USE_ADVANCED_IMAGE_PROCESSING = False
        self.CONVERSATION_FLOW = ConversationFlow.CUSTOM.value
        self.ORCHESTRATION_STRATEGY = "semantic_kernel"

        # Azure OpenAI
        self.AZURE_OPENAI_MODEL = "gpt-4o-default"
        self.AZURE_OPENAI_MODEL_NAME = self.AZURE_OPENAI_MODEL
        self.AZURE_OPENAI_VISION_MODEL = "gpt-4"
        self.AZURE_OPENAI_TEMPERATURE = "0"
        self.AZURE_OPENAI_TOP_P = "1.0"
        self.AZURE_OPENAI_MAX_TOKENS = "1500"
        self.AZURE_OPENAI_STOP_SEQUENCE = ""
        self.AZURE_OPENAI_SYSTEM_MESSAGE = (
            "You are an AI assistant that helps people find information."
        )
        self.AZURE_OPENAI_API_VERSION = "2024-02-01"
        self.AZURE_OPENAI_STREAM = "true"
        self.AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"

        self.SHOULD_STREAM = (
            True if self.AZURE_OPENAI_STREAM.lower() == "true" else False
        )

        # self.AZURE_COMPUTER_VISION_NAME = head_keyvault.get_secret(
        #     "cognitive-kind-ComputerVision"
        # )
        self.AZURE_COMPUTER_VISION_NAME = ""
        # self.AZURE_COMPUTER_VISION_ENDPOINT = head_keyvault.get_secret(
        #     f"{self.AZURE_COMPUTER_VISION_NAME}-endpoint"
        # )
        self.AZURE_COMPUTER_VISION_ENDPOINT = ""
        self.ADVANCED_IMAGE_PROCESSING_MAX_IMAGES = 1
        self.AZURE_COMPUTER_VISION_TIMEOUT = 30
        self.AZURE_COMPUTER_VISION_VECTORIZE_IMAGE_API_VERSION = "2024-02-01"
        self.AZURE_COMPUTER_VISION_VECTORIZE_IMAGE_MODEL_VERSION = "2023-04-15"

        # Initialize Azure keys based on authentication type and environment settings.
        # When AZURE_AUTH_TYPE is "rbac", azure keys are None or an empty string.
        if self.AZURE_AUTH_TYPE == "rbac":
            self.AZURE_SEARCH_KEY = None
            self.AZURE_OPENAI_API_KEY = ""
            self.AZURE_COMPUTER_VISION_KEY = None
        else:
            self.AZURE_SEARCH_KEY = keyvault.get_secret("AZURE_SEARCH_KEY")
            self.AZURE_OPENAI_API_KEY = keyvault.get_secret(
                "AZURE_OPENAI_API_KEY"
            )
            self.AZURE_COMPUTER_VISION_KEY = keyvault.get_secret(
                "AZURE_COMPUTER_VISION_KEY"
            )

        # Set env for Azure OpenAI
        self.AZURE_AI_SERVICES_NAME = head_keyvault.get_secret(
            "cognitive-kind-AIServices"
        )
        self.AZURE_OPENAI_ENDPOINT = (
            f"https://{self.AZURE_AI_SERVICES_NAME}.openai.azure.com/"
        )

        # Set env for OpenAI SDK
        self.OPENAI_API_TYPE = "azure" if self.AZURE_AUTH_TYPE == "keys" else "azure_ad"
        self.OPENAI_API_KEY = self.AZURE_OPENAI_API_KEY
        self.OPENAI_API_VERSION = self.AZURE_OPENAI_API_VERSION
        os.environ["OPENAI_API_TYPE"] = self.OPENAI_API_TYPE
        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY
        os.environ["OPENAI_API_VERSION"] = self.OPENAI_API_VERSION
        # Azure Functions - Batch processing
        self.BACKEND_URL = self.AZURE_FUNCTION_APP_ENDPOINT
        self.FUNCTION_KEY = None

        # Azure Form Recognizer

        self.AZURE_FORM_RECOGNIZER_NAME = keyvault.get_secret(
            "cognitive-kind-FormRecognizer"
        )
        self.AZURE_FORM_RECOGNIZER_ENDPOINT = keyvault.get_secret(
            f"{self.AZURE_FORM_RECOGNIZER_NAME}-endpoint"
        )

        # Azure App Insights
        # APPLICATIONINSIGHTS_ENABLED will be True when the application runs in App Service
        self.APPLICATIONINSIGHTS_ENABLED = "True"

        # Azure AI Content Safety
        self.AZURE_CONTENT_SAFETY_NAME = head_keyvault.get_secret(
            "cognitive-kind-ContentSafety"
        )
        self.AZURE_CONTENT_SAFETY_ENDPOINT = head_keyvault.get_secret(
            f"{self.AZURE_CONTENT_SAFETY_NAME}-endpoint"
        )

        # Speech Service
        self.AZURE_SPEECH_SERVICE_NAME = head_keyvault.get_secret(
            "cognitive-kind-SpeechServices"
        )
        self.AZURE_SPEECH_ENDPOINT = head_keyvault.get_secret(
            f"{self.AZURE_SPEECH_SERVICE_NAME}-endpoint"
        )

        self.AZURE_SPEECH_SERVICE_REGION = "westeurope"
        self.AZURE_SPEECH_RECOGNIZER_LANGUAGES = self.get_env_var_array(
            "AZURE_SPEECH_RECOGNIZER_LANGUAGES", "en-US"
        )
        self.AZURE_MAIN_CHAT_LANGUAGE = "en-US"
    
        self.AZURE_SPEECH_REGION_ENDPOINT = (
            f"https://{self.AZURE_SPEECH_SERVICE_REGION}.api.cognitive.microsoft.com/"
        )
        self.AZURE_SPEECH_KEY = head_keyvault.get_secret(f"{self.AZURE_SPEECH_SERVICE_NAME}-key") # changed from None to allow private endpoint communication

        self.LOAD_CONFIG_FROM_BLOB_STORAGE = self.get_env_var_bool(
            "LOAD_CONFIG_FROM_BLOB_STORAGE"
        )
        # Azure Search
        self.AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE", "")
        self.AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "")
        self.AZURE_SEARCH_USE_SEMANTIC_SEARCH = "True"
        self.AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG = os.getenv(
            "AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG", "default"
        )
        self.AZURE_SEARCH_INDEX_IS_PRECHUNKED = os.getenv(
            "AZURE_SEARCH_INDEX_IS_PRECHUNKED", ""
        )
        self.AZURE_SEARCH_FILTER = os.getenv("AZURE_SEARCH_FILTER", "")
        self.AZURE_SEARCH_TOP_K = self.get_env_var_int("AZURE_SEARCH_TOP_K", 5)
        self.AZURE_SEARCH_ENABLE_IN_DOMAIN = (
            os.getenv("AZURE_SEARCH_ENABLE_IN_DOMAIN", "true").lower() == "true"
        )
        self.AZURE_SEARCH_FIELDS_ID = os.getenv("AZURE_SEARCH_FIELDS_ID", "id")
        self.AZURE_SEARCH_CONTENT_COLUMN = os.getenv(
            "AZURE_SEARCH_CONTENT_COLUMN", "content"
        )
        self.AZURE_SEARCH_CONTENT_VECTOR_COLUMN = os.getenv(
            "AZURE_SEARCH_CONTENT_VECTOR_COLUMN", "content_vector"
        )
        self.AZURE_SEARCH_DIMENSIONS = os.getenv("AZURE_SEARCH_DIMENSIONS", "1536")
        self.AZURE_SEARCH_FILENAME_COLUMN = os.getenv(
            "AZURE_SEARCH_FILENAME_COLUMN", "filepath"
        )
        self.AZURE_SEARCH_TITLE_COLUMN = os.getenv("AZURE_SEARCH_TITLE_COLUMN", "title")
        self.AZURE_SEARCH_URL_COLUMN = os.getenv("AZURE_SEARCH_URL_COLUMN", "url")
        self.AZURE_SEARCH_FIELDS_TAG = os.getenv("AZURE_SEARCH_FIELDS_TAG", "tag")
        self.AZURE_SEARCH_FIELDS_METADATA = os.getenv(
            "AZURE_SEARCH_FIELDS_METADATA", "metadata"
        )
        self.AZURE_SEARCH_SOURCE_COLUMN = os.getenv(
            "AZURE_SEARCH_SOURCE_COLUMN", "source"
        )
        self.AZURE_SEARCH_CHUNK_COLUMN = os.getenv("AZURE_SEARCH_CHUNK_COLUMN", "chunk")
        self.AZURE_SEARCH_OFFSET_COLUMN = os.getenv(
            "AZURE_SEARCH_OFFSET_COLUMN", "offset"
        )
        self.AZURE_SEARCH_CONVERSATIONS_LOG_INDEX = os.getenv(
            "AZURE_SEARCH_CONVERSATIONS_LOG_INDEX", "conversations"
        )
        self.AZURE_SEARCH_DOC_UPLOAD_BATCH_SIZE = os.getenv(
            "AZURE_SEARCH_DOC_UPLOAD_BATCH_SIZE", 100
        )
        # Integrated Vectorization
        self.AZURE_SEARCH_DATASOURCE_NAME = os.getenv(
            "AZURE_SEARCH_DATASOURCE_NAME", ""
        )
        self.AZURE_SEARCH_INDEXER_NAME = os.getenv("AZURE_SEARCH_INDEXER_NAME", "")

        self.AZURE_ML_WORKSPACE_NAME = ""

        self.PROMPT_FLOW_ENDPOINT_NAME = ""

        self.PROMPT_FLOW_DEPLOYMENT_NAME = ""

        self.OPEN_AI_FUNCTIONS_SYSTEM_PROMPT = ""
        self.SEMENTIC_KERNEL_SYSTEM_PROMPT = ""

        logger.info("Initializing EnvHelper completed")

    def is_chat_model(self):
        if "gpt-4" in self.AZURE_OPENAI_MODEL_NAME.lower():
            return True
        return False

    def get_env_var_bool(self, var_name: str, default: str = "True") -> bool:
        return os.getenv(var_name, default).lower() == "true"

    def get_env_var_array(self, var_name: str, default: str = ""):
        return os.getenv(var_name, default).split(",")

    def get_env_var_int(self, var_name: str, default: int):
        try:
            return int(os.getenv(var_name, default))
        except (ValueError, TypeError):
            return default

    def get_env_var_float(self, var_name: str, default: float):
        try:
            return float(os.getenv(var_name, default))
        except (ValueError, TypeError):
            return default

    def is_auth_type_keys(self):
        return self.AZURE_AUTH_TYPE == "keys"

    def get_info_from_env(self, env_var: str, default_info: str) -> dict:
        # Fetch and parse model info from the environment variable.
        info_str = os.getenv(env_var, default_info)
        # Handle escaped characters in the JSON string by wrapping it in double quotes for parsing.
        if "\\" in info_str:
            info_str = json.loads(f'"{info_str}"')
        try:
            return {} if not info_str else json.loads(info_str)
        except (json.JSONDecodeError, ValueError, TypeError):
            try:
                return json.loads(default_info) if default_info else {}
            except (json.JSONDecodeError, ValueError, TypeError):
                return {}

    @staticmethod
    def check_env():
        for attr, value in EnvHelper().__dict__.items():
            if value == "":
                logger.warning(f"{attr} is not set in the environment variables.")

    @classmethod
    def clear_instance(cls):
        if cls._instance is not None:
            cls._instance = None
