# AzPaddyPy

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Azure](https://img.shields.io/badge/Azure-Cloud-blue.svg)](https://azure.microsoft.com/)

**AzPaddyPy** is a comprehensive Python package for Azure cloud services integration with standardized configuration management, OpenTelemetry tracing, and builder patterns. It simplifies Azure service orchestration while providing flexible, production-ready patterns for complex cloud applications.

## 🌟 Key Features

- **🔐 Azure Identity Management** - Token caching, multiple credential types, seamless authentication
- **🗝️ Azure Key Vault Integration** - Secrets, keys, and certificates management  
- **💾 Azure Storage Operations** - Blob, file, and queue storage with unified APIs
- **📊 Comprehensive Logging** - Application Insights integration with OpenTelemetry tracing
- **🏗️ Builder Patterns** - Flexible service composition and configuration
- **🌍 Environment Detection** - Docker vs local development with smart defaults
- **⚙️ Configuration Management** - Environment variables, .env files, and service discovery

## 📦 Installation

```bash
# Install with pip
pip install azpaddypy

# Install with uv (recommended)
uv add azpaddypy
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

### Working with Key Vault

```python
from azpaddypy.builder import AzureManagementBuilder, ConfigurationSetupBuilder

# Setup
env_config = ConfigurationSetupBuilder().with_local_env_management().build()
management = (
    AzureManagementBuilder(env_config)
    .with_identity()
    .with_keyvault(name="primary", vault_url="https://my-vault.vault.azure.net/")
    .with_keyvault(name="admin", vault_url="https://my-admin-vault.vault.azure.net/")
    .build()
)

# Access secrets
database_password = management.keyvaults["primary"].get_secret("database-password")
admin_key = management.keyvaults["admin"].get_secret("admin-api-key")

# Set secrets
management.keyvaults["primary"].set_secret("new-secret", "secret-value")
```

### Working with Storage

```python
from azpaddypy.builder import AzureResourceBuilder

# Build storage configuration
resources = (
    AzureResourceBuilder(management, env_config)
    .with_storage(
        name="main",
        account_url="https://mystorageaccount.blob.core.windows.net/",
        enable_blob=True,
        enable_file=True,
        enable_queue=True
    )
    .build()
)

# Use storage services
storage = resources.storage_accounts["main"]

# Blob operations
blob_client = storage.blob_service_client
container_client = blob_client.get_container_client("my-container")

# Upload a file
with open("local-file.txt", "rb") as data:
    container_client.upload_blob(name="remote-file.txt", data=data)

# Queue operations  
queue_client = storage.queue_service_client
queue = queue_client.get_queue_client("my-queue")
queue.send_message("Hello from azpaddypy!")

# File share operations
file_client = storage.file_service_client
share_client = file_client.get_share_client("my-share")
```

### Advanced Logging

```python
from azpaddypy.builder import AzureManagementBuilder

management = (
    AzureManagementBuilder(env_config)
    .with_logger(
        log_level="DEBUG",
        enable_console=True
    )
    .build()
)

logger = management.logger

# Structured logging
logger.info("User action", extra={
    "user_id": "12345",
    "action": "login",
    "ip_address": "192.168.1.1"
})

# Error logging with context
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", extra={
        "error_type": type(e).__name__,
        "operation": "risky_operation"
    }, exc_info=True)
```

### Environment-Specific Configuration

```python
from azpaddypy.builder import ConfigurationSetupBuilder

# Local development configuration
local_config = {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "DATABASE_URL": "sqlite:///local.db"
}

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
    .build()
)
```

### Director Patterns (Simplified Setup)

```python
from azpaddypy.builder.directors import (
    ConfigurationSetupDirector,
    AzureManagementDirector,
    AzureResourceDirector
)

# Quick setup with sensible defaults
env_config = ConfigurationSetupDirector.build_default_config()
management = AzureManagementDirector.build_default_config(env_config)
full_config = AzureResourceDirector.build_default_config(env_config, management)

# Access services
logger = full_config.management.logger
keyvault = full_config.management.keyvault
storage = full_config.resources.storage_account
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

### v0.6.8
- Comprehensive builder patterns for Azure services
- OpenTelemetry integration for advanced tracing
- Environment detection and local development support
- Multi-Key Vault support with named configurations
- Enhanced storage operations with unified APIs

---

**Made with ❤️ for Azure developers** 