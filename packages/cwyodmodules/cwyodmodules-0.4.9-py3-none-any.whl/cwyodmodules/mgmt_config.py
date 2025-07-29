"""Azure Management Configuration Module.

This module provides a centralized configuration setup for Azure services using the
azpaddypy builder pattern. It creates standardized configurations for identity management,
key vault access, logging, and storage resources.

The configuration follows the recommended azpaddypy pattern:
1. Environment setup with local development support
2. Management services (logging, identity, key vaults)
3. Resource services (storage)

Environment Variables Required:
    - key_vault_uri: Primary Key Vault URL
    - head_key_vault_uri: Head/Admin Key Vault URL

Environment Variables Optional:
    - LOGGER_LOG_LEVEL: Logging level (default: INFO)
    - APPLICATIONINSIGHTS_CONNECTION_STRING: Application Insights connection
    
Usage:
    from mgmt_config import logger, identity, keyvault, head_keyvault
    
    # Use logger for application logging
    logger.info("Application started")
    
    # Use identity for Azure authentication
    token = identity.get_token("https://management.azure.com/.default")
    
    # Access secrets from key vaults
    secret = keyvault.get_secret("my-secret")
    admin_secret = head_keyvault.get_secret("admin-secret")

Notes:
    - Local development uses Azure CLI authentication or environment variables
    - Production uses Managed Identity
    - Development storage is configured for local machine testing
"""

import os
from typing import Optional

from azpaddypy.builder import (
    ConfigurationSetupBuilder,
    AzureManagementBuilder,
    AzureResourceBuilder,
    AzureManagementConfiguration,
    AzureResourceConfiguration,
)


# =============================================================================
# Environment Configuration
# =============================================================================

# Azure Web Jobs storage configuration for local development
# These settings enable local Azure Functions development with Azurite storage emulator
LOCAL_DEVELOPMENT_STORAGE_CONFIG = {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AzureWebJobsDashboard": "UseDevelopmentStorage=true", 
    "input_queue_connection__queueServiceUri": "UseDevelopmentStorage=true",
    "AzureWebJobsStorage__accountName": "UseDevelopmentStorage=true",
    "AzureWebJobsStorage__blobServiceUri": "UseDevelopmentStorage=true",
    "AZURE_CLIENT_ID": "aa7...",
    "AZURE_TENANT_ID": "e55...",
    "AZURE_CLIENT_SECRET": "IQ0..."
}

# Build environment configuration following azpaddypy recommended pattern
environment_configuration = (
    ConfigurationSetupBuilder()
    .with_local_env_management()  # FIRST: Load .env files and environment variables
    .with_environment_detection()  # Detect Docker vs local environment
    .with_environment_variables(
        LOCAL_DEVELOPMENT_STORAGE_CONFIG, 
        in_docker=True,  # Only apply to local machine
        in_machine=True   # Enable for local development
    )
    .with_service_configuration()    # Parse service settings (name, version, etc.)
    .with_logging_configuration()    # Setup Application Insights and console logging
    .with_identity_configuration()   # Configure Azure Identity with token caching
    .build()
)


# =============================================================================
# Key Vault URIs from Environment
# =============================================================================

# Primary key vault for application secrets
primary_key_vault_uri: Optional[str] = os.getenv('key_vault_uri')

# Head/admin key vault for elevated permissions and admin secrets  
head_key_vault_uri: Optional[str] = os.getenv('head_key_vault_uri')

# Validate required environment variables
if not primary_key_vault_uri:
    raise ValueError(
        "key_vault_uri environment variable is required. "
        "Set it to your primary Key Vault URL (e.g., https://my-vault.vault.azure.net/)"
    )

if not head_key_vault_uri:
    raise ValueError(
        "head_key_vault_uri environment variable is required. "
        "Set it to your head/admin Key Vault URL (e.g., https://my-head-vault.vault.azure.net/)"
    )


# =============================================================================
# Azure Management Services Configuration
# =============================================================================

# Build management configuration with logger, identity, and key vaults
azure_management_configuration: AzureManagementConfiguration = (
    AzureManagementBuilder(environment_configuration)
    .with_logger()  # Application Insights + console logging
    .with_identity()  # Azure Identity with token caching
    .with_keyvault(vault_url=primary_key_vault_uri, name="main")  # Primary key vault
    .with_keyvault(vault_url=head_key_vault_uri, name="head")        # Admin key vault
    .build()
)

# =============================================================================
# Exported Core Services for Application Use
# =============================================================================

# Application logger with Application Insights integration
# Use for all application logging: logger.info(), logger.error(), etc.
logger = azure_management_configuration.logger

# Azure Identity for authentication to Azure services
# Automatically handles Managed Identity in production, Azure CLI in development
identity = azure_management_configuration.identity

# Primary key vault client for application secrets
# Access secrets with: keyvault.get_secret("secret-name")
keyvault = azure_management_configuration.keyvaults.get("main")

# Head/admin key vault client for elevated permissions
# Access admin secrets with: head_keyvault.get_secret("admin-secret-name") 
head_keyvault = azure_management_configuration.keyvaults.get("head")

# =============================================================================
# Azure Resource Services Configuration  
# =============================================================================
project_code = keyvault.get_secret("project-code")
azure_environment = keyvault.get_secret("resource-group-environment")
storage_account_name = f"stqueue{project_code}{azure_environment}"
storage_account_url = f"https://{storage_account_name}.blob.core.windows.net/"

# Build resource configuration with storage account access
azure_resource_configuration: AzureResourceConfiguration = (
    AzureResourceBuilder(
        management_config=azure_management_configuration,
        env_config=environment_configuration
    )
    .with_storage(name="main", account_url=storage_account_url)  # Azure Storage (blob, file, queue) from STORAGE_ACCOUNT_URL env var
    .build()
)


# =============================================================================
# Exported Services for Application Use
# =============================================================================

# Storage account client (if needed)
# Access with: storage_account.blob_service_client, storage_account.file_service_client

storage_account = azure_resource_configuration.storage_accounts.get("main")


# =============================================================================
# Configuration Validation
# =============================================================================

# Validate that all required services are properly initialized
try:
    azure_management_configuration.validate()
    azure_resource_configuration.validate()
    logger.info("Azure management configuration initialized successfully")
    logger.info(f"Connected to key vaults: {list(azure_management_configuration.keyvaults.keys())}")
except Exception as config_error:
    # Log configuration errors for debugging
    if 'logger' in locals():
        logger.error(f"Configuration validation failed: {config_error}")
    else:
        print(f"CRITICAL: Configuration validation failed: {config_error}")
    raise


# Export all for convenient importing
__all__ = [
    "logger",
    "identity", 
    "keyvault",
    "head_keyvault",
    "storage_account",
]
