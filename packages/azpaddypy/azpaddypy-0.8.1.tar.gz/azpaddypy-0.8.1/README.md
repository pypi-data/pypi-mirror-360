# AzPaddyPy

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Azure](https://img.shields.io/badge/Azure-Cloud-blue.svg)](https://azure.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AzPaddyPy** is a comprehensive Python package for Azure cloud services integration with standardized configuration management, OpenTelemetry tracing, and builder patterns. It simplifies Azure service orchestration while providing flexible, production-ready patterns for complex cloud applications.

## 🌟 Key Features

- **🔐 Azure Identity Management** - Token caching, multiple credential types, seamless authentication
- **🗝️ Azure Key Vault Integration** - Secrets, keys, and certificates management  
- **💾 Azure Storage Operations** - Blob, file, and queue storage with unified APIs
- **📊 Comprehensive Logging** - Application Insights integration with OpenTelemetry tracing
- **🏗️ Builder Patterns** - Flexible service composition and configuration
- **🌍 Environment Detection** - Docker vs local development with smart defaults
- **⚙️ Configuration Management** - Environment variables, .env files, and service discovery
- **🗄️ CosmosDB Integration** - Document database operations with unified client

## 📦 Installation

```bash
# Install with pip
pip install azpaddypy

# Install with uv (recommended)
uv add azpaddypy

# Install with development dependencies
uv add azpaddypy[dev]
```

## 🚀 Quick Start

### Simple Usage (Direct Imports)

```python
from azpaddypy import logger, identity, keyvault, storage_account

# Use logger for application logging
logger.info("Application started")

# Use identity for Azure authentication  
token = identity.get_token("https://management.azure.com/.default")

# Access secrets from Key Vault
secret_value = keyvault.get_secret("my-secret")

# Use storage services
blob_client = storage_account.blob_service_client
```

### Builder Pattern Usage (Recommended)

```python
from azpaddypy.builder import (
    ConfigurationSetupBuilder, 
    AzureManagementBuilder, 
    AzureResourceBuilder
)

# 1. Setup environment configuration
env_config = (
    ConfigurationSetupBuilder()
    .with_local_env_management()      # Load .env files (FIRST)
    .with_environment_detection()     # Detect Docker vs local
    .with_service_configuration()     # Parse service settings
    .with_logging_configuration()     # Setup logging
    .with_identity_configuration()    # Configure authentication
    .build()
)

# 2. Build management services (logger, identity, key vault)
management = (
    AzureManagementBuilder(env_config)
    .with_logger()
    .with_identity() 
    .with_keyvault(vault_url="https://my-vault.vault.azure.net/")
    .build()
)

# 3. Build resource services (storage, etc.)
resources = (
    AzureResourceBuilder(management, env_config)
    .with_storage(account_url="https://mystorageaccount.blob.core.windows.net/")
    .build()
)

# 4. Use the configured services
management.logger.info("Services configured successfully")
secret = management.keyvault.get_secret("database-password")
blob_client = resources.storage_account.blob_service_client
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```env
# Required: Key Vault Configuration
key_vault_uri=https://my-vault.vault.azure.net/
head_key_vault_uri=https://my-admin-vault.vault.azure.net/

# Required: Storage Configuration  
STORAGE_ACCOUNT_URL=https://mystorageaccount.blob.core.windows.net/

# Optional: Service Configuration
REFLECTION_NAME=my-application
REFLECTION_KIND=functionapp
SERVICE_VERSION=1.0.0

# Optional: Logging Configuration
LOGGER_LOG_LEVEL=INFO
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# Optional: Identity Configuration
IDENTITY_ENABLE_TOKEN_CACHE=true
IDENTITY_ALLOW_UNENCRYPTED_STORAGE=true

# Optional: Feature Toggles
KEYVAULT_ENABLE_SECRETS=true
KEYVAULT_ENABLE_KEYS=false
KEYVAULT_ENABLE_CERTIFICATES=false

STORAGE_ENABLE_BLOB=true
STORAGE_ENABLE_FILE=true  
STORAGE_ENABLE_QUEUE=true
```

### Azure Authentication

AzPaddyPy supports multiple authentication methods automatically:

**Local Development:**
```bash
# Option 1: Azure CLI (recommended)
az login

# Option 2: Environment variables
export AZURE_CLIENT_ID=your-client-id
export AZURE_TENANT_ID=your-tenant-id  
export AZURE_CLIENT_SECRET=your-client-secret
```

**Production (Azure):**
- Managed Identity (automatically detected)
- Service Principal (via environment variables)

## 📚 Usage Examples

### 1. Basic Logging Setup

```python
from azpaddypy.builder.directors import ConfigurationSetupDirector, AzureManagementDirector

# Quick setup with sensible defaults
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)

logger = management.logger

# Basic logging
logger.info("Application started")
logger.warning("This is a warning")
logger.error("This is an error")

# Structured logging with custom fields
logger.info("User action", extra={
    "user_id": "12345",
    "action": "login",
    "ip_address": "192.168.1.1",
    "session_id": "abc123"
})

# Error logging with context
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", extra={
        "error_type": type(e).__name__,
        "operation": "risky_operation",
        "user_id": "12345"
    }, exc_info=True)
```

### 2. Key Vault Operations

```python
from azpaddypy.builder.directors import AzureManagementDirector, ConfigurationSetupDirector

# Setup
env_config = ConfigurationSetupDirector.build_default_config()
management = (
    AzureManagementDirector.build_default_config(env_config)
    .with_keyvault(name="primary", vault_url="https://my-vault.vault.azure.net/")
    .with_keyvault(name="admin", vault_url="https://my-admin-vault.vault.azure.net/")
    .build()
)

# Access secrets
database_password = management.keyvaults["primary"].get_secret("database-password")
api_key = management.keyvaults["admin"].get_secret("external-api-key")

# Set secrets
management.keyvaults["primary"].set_secret("new-secret", "secret-value")

# List secrets
secrets = management.keyvaults["primary"].list_secrets()

# Delete secrets
management.keyvaults["primary"].delete_secret("old-secret")

# Working with keys
key = management.keyvaults["primary"].get_key("my-key")
encrypted_data = management.keyvaults["primary"].encrypt("my-key", "Hello World")

# Working with certificates
cert = management.keyvaults["primary"].get_certificate("my-cert")
```

### 3. Storage Operations

```python
from azpaddypy.builder.directors import AzureResourceDirector

# Build storage configuration
resources = (
    AzureResourceDirector.build_default_config(env_config, management)
    .with_storage(
        name="main",
        account_url="https://mystorageaccount.blob.core.windows.net/",
        enable_blob=True,
        enable_file=True,
        enable_queue=True
    )
    .build()
)

storage = resources.storage_accounts["main"]

# Blob Storage Operations
blob_client = storage.blob_service_client
container_client = blob_client.get_container_client("my-container")

# Upload a file
with open("local-file.txt", "rb") as data:
    container_client.upload_blob(name="remote-file.txt", data=data)

# Download a file
with open("downloaded-file.txt", "wb") as data:
    container_client.download_blob(name="remote-file.txt").readinto(data)

# List blobs
blobs = container_client.list_blobs()
for blob in blobs:
    print(f"Blob: {blob.name}")

# Delete blob
container_client.delete_blob("remote-file.txt")

# Queue Storage Operations
queue_client = storage.queue_service_client
queue = queue_client.get_queue_client("my-queue")

# Send message
queue.send_message("Hello from azpaddypy!")

# Receive messages
messages = queue.receive_messages()
for message in messages:
    print(f"Message: {message.content}")
    queue.delete_message(message)

# File Share Operations
file_client = storage.file_service_client
share_client = file_client.get_share_client("my-share")

# Create directory
directory_client = share_client.get_directory_client("my-directory")
directory_client.create_directory()

# Upload file to file share
file_client = directory_client.get_file_client("my-file.txt")
with open("local-file.txt", "rb") as data:
    file_client.upload_file(data)
```

### 4. CosmosDB Operations

```python
from azpaddypy.builder.directors import AzureResourceDirector

# Build configuration with CosmosDB
resources = (
    AzureResourceDirector.build_default_config(env_config, management)
    .with_cosmosdb(
        name="main",
        endpoint="https://my-cosmosdb.documents.azure.com:443/",
        database_name="my-database"
    )
    .build()
)

cosmosdb = resources.cosmosdb_accounts["main"]

# Create container
container = cosmosdb.create_container(
    container_name="users",
    partition_key_path="/id"
)

# Insert document
document = {
    "id": "user123",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00Z"
}
cosmosdb.insert_document("users", document)

# Query documents
query = "SELECT * FROM c WHERE c.name = @name"
parameters = [{"name": "@name", "value": "John Doe"}]
results = cosmosdb.query_documents("users", query, parameters)

for doc in results:
    print(f"User: {doc['name']}")

# Update document
updated_doc = {
    "id": "user123",
    "name": "John Doe",
    "email": "john.updated@example.com",
    "updated_at": "2024-01-02T00:00:00Z"
}
cosmosdb.upsert_document("users", updated_doc)

# Delete document
cosmosdb.delete_document("users", "user123", partition_key="user123")
```

### 5. Advanced Configuration Patterns

```python
from azpaddypy.builder import ConfigurationSetupBuilder, AzureManagementBuilder, AzureResourceBuilder

# Environment-specific configuration
local_config = {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "DATABASE_URL": "sqlite:///local.db",
    "LOGGER_LOG_LEVEL": "DEBUG"
}

production_config = {
    "LOGGER_LOG_LEVEL": "WARNING",
    "IDENTITY_ALLOW_UNENCRYPTED_STORAGE": "false"
}

# Build environment configuration
env_config = (
    ConfigurationSetupBuilder()
    .with_local_env_management()
    .with_environment_detection()
    .with_environment_variables(
        local_config,
        in_docker=False,    # Don't apply in Docker
        in_machine=True     # Apply on local machine
    )
    .with_service_configuration()
    .with_logging_configuration()
    .with_identity_configuration()
    .build()
)

# Build management with multiple Key Vaults
management = (
    AzureManagementBuilder(env_config)
    .with_logger(
        log_level="DEBUG",
        enable_console=True,
        enable_application_insights=True
    )
    .with_identity(
        enable_token_cache=True,
        allow_unencrypted_storage=True
    )
    .with_keyvault(
        name="primary",
        vault_url="https://primary-vault.vault.azure.net/",
        enable_secrets=True,
        enable_keys=True,
        enable_certificates=False
    )
    .with_keyvault(
        name="admin",
        vault_url="https://admin-vault.vault.azure.net/",
        enable_secrets=True,
        enable_keys=False,
        enable_certificates=True
    )
    .build()
)

# Build resources with multiple storage accounts
resources = (
    AzureResourceBuilder(management, env_config)
    .with_storage(
        name="main",
        account_url="https://mainstorage.blob.core.windows.net/",
        enable_blob=True,
        enable_file=True,
        enable_queue=True
    )
    .with_storage(
        name="backup",
        account_url="https://backupstorage.blob.core.windows.net/",
        enable_blob=True,
        enable_file=False,
        enable_queue=False
    )
    .with_cosmosdb(
        name="main",
        endpoint="https://my-cosmosdb.documents.azure.com:443/",
        database_name="my-database"
    )
    .build()
)
```

### 6. Azure Functions Integration

```python
# function_app.py
import azure.functions as func
from azpaddypy.builder.directors import AzureManagementDirector, ConfigurationSetupDirector

# Initialize once at module level
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)

app = func.FunctionApp()

@app.function_name("HttpTrigger")
@app.route(route="api/data")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    management.logger.info("Function triggered", extra={
        "function_name": "HttpTrigger",
        "request_method": req.method,
        "request_url": req.url
    })
    
    try:
        # Access secrets
        api_key = management.keyvault.get_secret("external-api-key")
        
        # Your function logic here
        result = process_request(req, api_key)
        
        management.logger.info("Function completed successfully", extra={
            "function_name": "HttpTrigger",
            "result_status": "success"
        })
        
        return func.HttpResponse(result)
        
    except Exception as e:
        management.logger.error("Function failed", extra={
            "function_name": "HttpTrigger",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=True)
        
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )

def process_request(req: func.HttpRequest, api_key: str):
    # Your business logic here
    return "Success"
```

### 7. Web Application Integration

```python
# app.py (Flask example)
from flask import Flask, request, jsonify
from azpaddypy.builder.directors import AzureResourceDirector, AzureManagementDirector, ConfigurationSetupDirector

# Initialize Azure services
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)
resources = AzureResourceDirector.build_default_config(env_config, management)

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    management.logger.info("GET /api/users", extra={
        "user_id": request.headers.get('X-User-ID'),
        "ip_address": request.remote_addr
    })
    
    try:
        # Query CosmosDB for users
        users = resources.cosmosdb_accounts["main"].query_documents(
            "users",
            "SELECT * FROM c"
        )
        
        return jsonify(list(users))
        
    except Exception as e:
        management.logger.error("Failed to get users", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=True)
        
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    user_data = request.json
    
    try:
        # Store user in CosmosDB
        user_id = resources.cosmosdb_accounts["main"].insert_document(
            "users",
            user_data
        )
        
        # Store user avatar in blob storage
        if 'avatar' in user_data:
            blob_client = resources.storage_accounts["main"].blob_service_client
            container_client = blob_client.get_container_client("avatars")
            container_client.upload_blob(
                name=f"{user_id}.jpg",
                data=user_data['avatar']
            )
        
        management.logger.info("User created", extra={
            "user_id": user_id,
            "user_email": user_data.get('email')
        })
        
        return jsonify({"id": user_id}), 201
        
    except Exception as e:
        management.logger.error("Failed to create user", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=True)
        
        return jsonify({"error": "Internal server error"}), 500
```

### 8. Background Job Processing

```python
# job_processor.py
import time
from azpaddypy.builder.directors import AzureResourceDirector, AzureManagementDirector, ConfigurationSetupDirector

# Initialize Azure services
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)
resources = AzureResourceDirector.build_default_config(env_config, management)

def process_jobs():
    """Background job processor using Azure Queue Storage."""
    queue_client = resources.storage_accounts["main"].queue_service_client
    queue = queue_client.get_queue_client("job-queue")
    
    management.logger.info("Starting job processor")
    
    while True:
        try:
            # Receive messages from queue
            messages = queue.receive_messages(max_messages=10, visibility_timeout=300)
            
            for message in messages:
                try:
                    management.logger.info("Processing job", extra={
                        "job_id": message.id,
                        "job_content": message.content
                    })
                    
                    # Process the job
                    result = process_job(message.content)
                    
                    # Store result in blob storage
                    blob_client = resources.storage_accounts["main"].blob_service_client
                    container_client = blob_client.get_container_client("job-results")
                    container_client.upload_blob(
                        name=f"{message.id}.json",
                        data=result
                    )
                    
                    # Delete message from queue
                    queue.delete_message(message)
                    
                    management.logger.info("Job completed", extra={
                        "job_id": message.id,
                        "status": "success"
                    })
                    
                except Exception as e:
                    management.logger.error("Job failed", extra={
                        "job_id": message.id,
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }, exc_info=True)
                    
                    # Message will return to queue after visibility timeout
                    
            time.sleep(5)  # Wait before next poll
            
        except Exception as e:
            management.logger.error("Queue processing error", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            time.sleep(30)  # Wait longer on error

def process_job(job_data):
    """Process individual job."""
    # Your job processing logic here
    return {"status": "completed", "result": "success"}
```

### 9. Data Pipeline Example

```python
# data_pipeline.py
from azpaddypy.builder.directors import AzureResourceDirector, AzureManagementDirector, ConfigurationSetupDirector

# Initialize Azure services
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)
resources = AzureResourceDirector.build_default_config(env_config, management)

def process_data_pipeline():
    """Example data pipeline using multiple Azure services."""
    
    management.logger.info("Starting data pipeline")
    
    try:
        # 1. Read data from blob storage
        blob_client = resources.storage_accounts["main"].blob_service_client
        container_client = blob_client.get_container_client("raw-data")
        
        blobs = container_client.list_blobs()
        processed_data = []
        
        for blob in blobs:
            # Download blob
            blob_data = container_client.download_blob(blob.name).read()
            
            # Process data
            processed_item = process_data_item(blob_data)
            processed_data.append(processed_item)
            
            management.logger.info("Processed blob", extra={
                "blob_name": blob.name,
                "processed_size": len(processed_item)
            })
        
        # 2. Store processed data in CosmosDB
        for item in processed_data:
            resources.cosmosdb_accounts["main"].upsert_document(
                "processed-data",
                item
            )
        
        # 3. Send notification to queue
        queue_client = resources.storage_accounts["main"].queue_service_client
        queue = queue_client.get_queue_client("notifications")
        queue.send_message(f"Pipeline completed: {len(processed_data)} items processed")
        
        management.logger.info("Data pipeline completed", extra={
            "items_processed": len(processed_data)
        })
        
    except Exception as e:
        management.logger.error("Data pipeline failed", extra={
            "error_type": type(e).__name__,
            "error_message": str(e)
        }, exc_info=True)
        raise

def process_data_item(data):
    """Process individual data item."""
    # Your data processing logic here
    return {"processed": True, "data": data.decode()}
```

### 10. Multi-Environment Configuration

```python
# config_manager.py
import os
from azpaddypy.builder import ConfigurationSetupBuilder, AzureManagementBuilder, AzureResourceBuilder

class EnvironmentManager:
    """Manages different environment configurations."""
    
    @staticmethod
    def get_development_config():
        """Development environment configuration."""
        local_config = {
            "AzureWebJobsStorage": "UseDevelopmentStorage=true",
            "LOGGER_LOG_LEVEL": "DEBUG",
            "IDENTITY_ALLOW_UNENCRYPTED_STORAGE": "true"
        }
        
        env_config = (
            ConfigurationSetupBuilder()
            .with_local_env_management()
            .with_environment_detection()
            .with_environment_variables(local_config, in_docker=False, in_machine=True)
            .with_service_configuration()
            .with_logging_configuration()
            .with_identity_configuration()
            .build()
        )
        
        management = (
            AzureManagementBuilder(env_config)
            .with_logger(log_level="DEBUG")
            .with_identity(allow_unencrypted_storage=True)
            .with_keyvault(vault_url="https://dev-vault.vault.azure.net/")
            .build()
        )
        
        resources = (
            AzureResourceBuilder(management, env_config)
            .with_storage(account_url="https://devstorage.blob.core.windows.net/")
            .with_cosmosdb(
                endpoint="https://dev-cosmosdb.documents.azure.com:443/",
                database_name="dev-database"
            )
            .build()
        )
        
        return management, resources
    
    @staticmethod
    def get_production_config():
        """Production environment configuration."""
        production_config = {
            "LOGGER_LOG_LEVEL": "WARNING",
            "IDENTITY_ALLOW_UNENCRYPTED_STORAGE": "false"
        }
        
        env_config = (
            ConfigurationSetupBuilder()
            .with_local_env_management()
            .with_environment_detection()
            .with_environment_variables(production_config, in_docker=True, in_machine=False)
            .with_service_configuration()
            .with_logging_configuration()
            .with_identity_configuration()
            .build()
        )
        
        management = (
            AzureManagementBuilder(env_config)
            .with_logger(log_level="WARNING")
            .with_identity(allow_unencrypted_storage=False)
            .with_keyvault(vault_url="https://prod-vault.vault.azure.net/")
            .build()
        )
        
        resources = (
            AzureResourceBuilder(management, env_config)
            .with_storage(account_url="https://prodstorage.blob.core.windows.net/")
            .with_cosmosdb(
                endpoint="https://prod-cosmosdb.documents.azure.com:443/",
                database_name="prod-database"
            )
            .build()
        )
        
        return management, resources

# Usage
if os.getenv("ENVIRONMENT") == "production":
    management, resources = EnvironmentManager.get_production_config()
else:
    management, resources = EnvironmentManager.get_development_config()
```

## 🏗️ Architecture

AzPaddyPy follows a layered builder pattern architecture:

```
┌─────────────────────────────────────┐
│        Application Layer           │
├─────────────────────────────────────┤
│     AzureConfiguration (Combined)   │
├─────────────────────────────────────┤
│  AzureResourceConfiguration         │
│  - Storage Accounts                 │
│  - CosmosDB Accounts               │
│  - Additional Resources             │
├─────────────────────────────────────┤
│  AzureManagementConfiguration       │  
│  - Logger (App Insights)            │
│  - Identity (Token Cache)           │
│  - Key Vaults                       │
├─────────────────────────────────────┤
│  EnvironmentConfiguration           │
│  - Environment Detection            │
│  - Service Configuration            │
│  - Local Development Support        │
└─────────────────────────────────────┘
```

### Builder Flow

1. **ConfigurationSetupBuilder** - Environment setup and detection
2. **AzureManagementBuilder** - Core management services  
3. **AzureResourceBuilder** - Azure resource services
4. **Directors** - Pre-configured common patterns

## 🔒 Security Best Practices

### Key Vault Security
```python
# ✅ Good: Use specific vault URLs
management.with_keyvault(vault_url="https://prod-vault.vault.azure.net/")

# ❌ Avoid: Hardcoding secrets
database_password = "hardcoded-password"  # DON'T DO THIS

# ✅ Good: Retrieve from Key Vault
database_password = keyvault.get_secret("database-password")
```

### Identity Security
```python
# ✅ Good: Enable token caching for performance
.with_identity_configuration(
    enable_token_cache=True,
    allow_unencrypted_storage=False  # Use encrypted cache in production
)

# ✅ Good: Use Managed Identity in production
# No additional configuration needed - automatically detected
```

### Environment Security
```python
# ✅ Good: Environment-specific configurations
production_config = {
    "IDENTITY_ALLOW_UNENCRYPTED_STORAGE": "false",
    "LOGGER_LOG_LEVEL": "WARNING"
}

development_config = {
    "IDENTITY_ALLOW_UNENCRYPTED_STORAGE": "true", 
    "LOGGER_LOG_LEVEL": "DEBUG"
}
```

## 🚀 Production Deployment

### Azure Functions

```python
# function_app.py
import azure.functions as func
from azpaddypy.builder.directors import AzureManagementDirector, ConfigurationSetupDirector

# Initialize once at module level
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)

app = func.FunctionApp()

@app.function_name("HttpTrigger")
@app.route(route="api/data")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    management.logger.info("Function triggered")
    
    # Access secrets
    api_key = management.keyvault.get_secret("external-api-key")
    
    # Your function logic here
    return func.HttpResponse("Success")
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment variables
ENV REFLECTION_KIND=functionapp
ENV LOGGER_LOG_LEVEL=INFO

CMD ["python", "app.py"]
```

### Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - key_vault_uri=https://prod-vault.vault.azure.net/
      - STORAGE_ACCOUNT_URL=https://prodstorage.blob.core.windows.net/
      - APPLICATIONINSIGHTS_CONNECTION_STRING=${APP_INSIGHTS_CONN_STRING}
    depends_on:
      - azurite
  
  azurite:
    image: mcr.microsoft.com/azure-storage/azurite
    ports:
      - "10000:10000"
      - "10001:10001" 
      - "10002:10002"
```

## 🧪 Testing

```python
# test_azpaddypy.py
import pytest
from azpaddypy.builder import ConfigurationSetupBuilder, AzureManagementBuilder

def test_configuration_setup():
    """Test basic configuration setup."""
    env_config = (
        ConfigurationSetupBuilder()
        .with_local_env_management()
        .with_environment_detection()
        .build()
    )
    
    assert env_config.service_name is not None
    assert env_config.logger_log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]

@pytest.mark.asyncio
async def test_key_vault_integration():
    """Test Key Vault integration.""" 
    management = (
        AzureManagementBuilder(env_config)
        .with_identity()
        .with_keyvault(vault_url="https://test-vault.vault.azure.net/")
        .build()
    )
    
    # Test secret retrieval (requires actual vault in integration tests)
    # secret = management.keyvault.get_secret("test-secret")
    # assert secret is not None

def test_storage_operations():
    """Test storage operations."""
    resources = (
        AzureResourceBuilder(management, env_config)
        .with_storage(account_url="https://teststorage.blob.core.windows.net/")
        .build()
    )
    
    # Test storage client creation
    assert resources.storage_accounts["default"] is not None
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [GitHub Repository](https://github.com/your-org/azpaddypy)
- **Issues**: [GitHub Issues](https://github.com/your-org/azpaddypy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/azpaddypy/discussions)

## 🔄 Changelog

### v0.7.9
- Enhanced builder patterns for Azure services
- OpenTelemetry integration for advanced tracing
- Environment detection and local development support
- Multi-Key Vault support with named configurations
- Enhanced storage operations with unified APIs
- CosmosDB integration with unified client
- Comprehensive logging with Application Insights

---

**Made with ❤️ for Azure developers** 