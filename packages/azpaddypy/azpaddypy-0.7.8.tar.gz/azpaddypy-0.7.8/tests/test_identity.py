import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from azure.identity import DefaultAzureCredential, TokenCachePersistenceOptions
from azure.core.credentials import AccessToken
from opentelemetry.trace import Span, StatusCode, Status

from azpaddypy.mgmt.identity import (
    AzureIdentity,
    create_azure_identity,
)
from azpaddypy.mgmt.logging import AzureLogger


@pytest.fixture
def azure_identity():
    """Configured AzureIdentity instance for testing."""
    with patch('azpaddypy.mgmt.identity.DefaultAzureCredential') as mock_credential:
        with patch('azpaddypy.mgmt.identity.AzureLogger') as mock_logger_class:
            # Mock credential to avoid real authentication
            mock_credential.return_value = Mock()
            
            # Mock AzureLogger with tracer support
            mock_logger = Mock(spec=AzureLogger)
            
            # Mock tracer with context manager support
            mock_span = MagicMock()
            mock_context_manager = MagicMock()
            mock_context_manager.__enter__.return_value = mock_span
            mock_context_manager.__exit__.return_value = None
            
            mock_tracer = Mock()
            mock_tracer.start_as_current_span.return_value = mock_context_manager
            mock_logger.tracer = mock_tracer
            mock_logger.create_span.return_value = mock_context_manager
            
            mock_logger_class.return_value = mock_logger
            
            identity = AzureIdentity(
                service_name="test_service",
                enable_token_cache=True,
            )
            return identity


@pytest.fixture
def mock_access_token():
    """Mock AccessToken for testing."""
    token = AccessToken(token="test_token_value", expires_on=1234567890)
    return token


class TestAzureIdentityInitialization:
    """Test AzureIdentity initialization and configuration."""

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_init_with_defaults(self, mock_logger_class, mock_credential):
        """Test AzureIdentity initializes with default parameters."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        identity = AzureIdentity()
        
        assert identity.service_name == "azure_identity"
        assert identity.service_version == "1.0.0"
        assert identity.enable_token_cache is True
        assert identity.allow_unencrypted_storage is True
        assert identity._credential is not None
        
        # Verify AzureLogger created with correct parameters
        mock_logger_class.assert_called_once_with(
            service_name="azure_identity",
            service_version="1.0.0",
            connection_string=None,
            enable_console_logging=True,
        )
        mock_credential.assert_called_once()

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_init_with_custom_params(self, mock_logger_class, mock_credential):
        """Test AzureIdentity initializes with custom parameters."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        custom_options = {"exclude_managed_identity_credential": True}
        
        identity = AzureIdentity(
            service_name="custom_service",
            service_version="2.0.0",
            enable_token_cache=False,
            allow_unencrypted_storage=False,
            custom_credential_options=custom_options,
            connection_string="test_connection_string",
        )
        
        assert identity.service_name == "custom_service"
        assert identity.service_version == "2.0.0"
        assert identity.enable_token_cache is False
        assert identity.allow_unencrypted_storage is False
        
        # Verify AzureLogger created with custom parameters
        mock_logger_class.assert_called_once_with(
            service_name="custom_service",
            service_version="2.0.0",
            connection_string="test_connection_string",
            enable_console_logging=True,
        )
        mock_credential.assert_called_once_with(exclude_managed_identity_credential=True)

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    def test_init_with_provided_logger(self, mock_credential):
        """Test AzureIdentity uses provided logger instead of creating new one."""
        mock_credential.return_value = Mock()
        provided_logger = Mock(spec=AzureLogger)
        provided_logger.tracer = Mock()
        provided_logger.create_span.return_value = MagicMock()
        
        identity = AzureIdentity(logger=provided_logger)
        
        assert identity.logger == provided_logger

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    @patch('azpaddypy.mgmt.identity.TokenCachePersistenceOptions')
    def test_init_with_token_cache_enabled(self, mock_cache_options, mock_logger_class, mock_credential):
        """Test token cache options are passed when enabled."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        mock_cache_instance = Mock()
        mock_cache_options.return_value = mock_cache_instance
        
        identity = AzureIdentity(enable_token_cache=True, allow_unencrypted_storage=False)
        
        # Verify TokenCachePersistenceOptions created with correct settings
        mock_cache_options.assert_called_once_with(allow_unencrypted_storage=False)
        
        # Verify DefaultAzureCredential called with token cache options
        call_args = mock_credential.call_args
        assert "token_cache_persistence_options" in call_args.kwargs
        assert call_args.kwargs["token_cache_persistence_options"] == mock_cache_instance

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_init_with_token_cache_disabled(self, mock_logger_class, mock_credential):
        """Test token cache options are not passed when disabled."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        identity = AzureIdentity(enable_token_cache=False)
        
        # Verify DefaultAzureCredential called without token cache options
        call_args = mock_credential.call_args
        assert "token_cache_persistence_options" not in call_args.kwargs

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_init_credential_failure(self, mock_logger_class, mock_credential):
        """Test proper error handling when credential initialization fails."""
        mock_credential.side_effect = Exception("Credential init failed")
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        with pytest.raises(Exception, match="Credential init failed"):
            AzureIdentity()

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_init_with_all_custom_credential_options(self, mock_logger_class, mock_credential):
        """Test initialization with comprehensive custom credential options."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        custom_options = {
            "exclude_managed_identity_credential": True,
            "exclude_environment_credential": True,
            "exclude_azure_cli_credential": False,
            "tenant_id": "test-tenant-id"
        }
        
        identity = AzureIdentity(
            service_name="test_service",
            custom_credential_options=custom_options,
        )
        
        # Verify all custom options passed to DefaultAzureCredential
        call_args = mock_credential.call_args
        for key, value in custom_options.items():
            assert call_args.kwargs[key] == value


class TestAzureIdentityMethods:
    """Test AzureIdentity core methods."""

    def test_get_credential_success(self, azure_identity):
        """Test get_credential returns configured credential."""
        credential = azure_identity.get_credential()
        assert credential is not None

    def test_get_credential_not_initialized(self):
        """Test get_credential raises RuntimeError when credential not initialized."""
        with patch('azpaddypy.mgmt.identity.AzureLogger') as mock_logger_class:
            mock_logger = Mock(spec=AzureLogger)
            mock_logger.tracer = Mock()
            mock_logger.create_span.return_value = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            identity = AzureIdentity()
            identity._credential = None
            
            with pytest.raises(RuntimeError, match="Credential not initialized"):
                identity.get_credential()

    def test_get_token_with_string_scope(self, azure_identity, mock_access_token):
        """Test get_token with string scope returns access token."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        token = azure_identity.get_token("https://management.azure.com/.default")
        
        assert token == mock_access_token
        azure_identity._credential.get_token.assert_called_once_with("https://management.azure.com/.default")

    def test_get_token_with_list_scopes(self, azure_identity, mock_access_token):
        """Test get_token with list of scopes returns access token."""
        scopes = ["https://management.azure.com/.default", "https://graph.microsoft.com/.default"]
        azure_identity._credential.get_token.return_value = mock_access_token
        
        token = azure_identity.get_token(scopes)
        
        assert token == mock_access_token
        azure_identity._credential.get_token.assert_called_once_with(*scopes)

    def test_get_token_with_kwargs(self, azure_identity, mock_access_token):
        """Test get_token passes additional kwargs to credential."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        token = azure_identity.get_token(
            "https://management.azure.com/.default",
            claims="test_claims",
            tenant_id="test_tenant"
        )
        
        assert token == mock_access_token
        azure_identity._credential.get_token.assert_called_once_with(
            "https://management.azure.com/.default",
            claims="test_claims",
            tenant_id="test_tenant"
        )

    def test_get_token_failure(self, azure_identity):
        """Test get_token propagates exceptions from credential."""
        azure_identity._credential.get_token.side_effect = Exception("Token acquisition failed")
        
        with pytest.raises(Exception, match="Token acquisition failed"):
            azure_identity.get_token("https://management.azure.com/.default")

    def test_get_token_uninitialized_credential(self, azure_identity):
        """Test get_token raises RuntimeError when credential not initialized."""
        azure_identity._credential = None
        
        with pytest.raises(RuntimeError, match="Credential not initialized"):
            azure_identity.get_token("https://management.azure.com/.default")

    @patch('azpaddypy.mgmt.identity.get_bearer_token_provider')
    def test_get_token_provider_with_string_scope(self, mock_provider, azure_identity):
        """Test get_token_provider with string scope returns provider function."""
        mock_provider_func = Mock()
        mock_provider.return_value = mock_provider_func
        
        provider = azure_identity.get_token_provider("https://management.azure.com/.default")
        
        assert provider == mock_provider_func
        mock_provider.assert_called_once_with(
            azure_identity._credential, "https://management.azure.com/.default"
        )

    @patch('azpaddypy.mgmt.identity.get_bearer_token_provider')
    def test_get_token_provider_with_list_scopes(self, mock_provider, azure_identity):
        """Test get_token_provider with list of scopes returns provider function."""
        scopes = ["https://management.azure.com/.default", "https://graph.microsoft.com/.default"]
        mock_provider_func = Mock()
        mock_provider.return_value = mock_provider_func
        
        provider = azure_identity.get_token_provider(scopes)
        
        assert provider == mock_provider_func
        mock_provider.assert_called_once_with(azure_identity._credential, *scopes)

    @patch('azpaddypy.mgmt.identity.get_bearer_token_provider')
    def test_get_token_provider_with_kwargs(self, mock_provider, azure_identity):
        """Test get_token_provider passes additional kwargs."""
        mock_provider_func = Mock()
        mock_provider.return_value = mock_provider_func
        
        provider = azure_identity.get_token_provider(
            "https://management.azure.com/.default",
            custom_param="test_value"
        )
        
        assert provider == mock_provider_func
        mock_provider.assert_called_once_with(
            azure_identity._credential,
            "https://management.azure.com/.default",
            custom_param="test_value"
        )

    @patch('azpaddypy.mgmt.identity.get_bearer_token_provider')
    def test_get_token_provider_failure(self, mock_provider, azure_identity):
        """Test get_token_provider propagates exceptions."""
        mock_provider.side_effect = Exception("Provider creation failed")
        
        with pytest.raises(Exception, match="Provider creation failed"):
            azure_identity.get_token_provider("https://management.azure.com/.default")

    @patch('azpaddypy.mgmt.identity.get_bearer_token_provider')  
    def test_get_token_provider_uninitialized_credential(self, mock_provider, azure_identity):
        """Test get_token_provider raises RuntimeError when credential not initialized."""
        azure_identity._credential = None
        
        with pytest.raises(RuntimeError, match="Credential not initialized"):
            azure_identity.get_token_provider("https://management.azure.com/.default")

    def test_test_credential_success(self, azure_identity, mock_access_token):
        """Test test_credential returns True when token acquisition succeeds."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        result = azure_identity.test_credential()
        
        assert result is True
        azure_identity._credential.get_token.assert_called_once_with("https://management.azure.com/.default")

    def test_test_credential_custom_scopes(self, azure_identity, mock_access_token):
        """Test test_credential with custom scopes."""
        custom_scopes = ["https://graph.microsoft.com/.default"]
        azure_identity._credential.get_token.return_value = mock_access_token
        
        result = azure_identity.test_credential(custom_scopes)
        
        assert result is True
        azure_identity._credential.get_token.assert_called_once_with(*custom_scopes)

    def test_test_credential_string_scope(self, azure_identity, mock_access_token):
        """Test test_credential with string scope."""
        custom_scope = "https://graph.microsoft.com/.default"
        azure_identity._credential.get_token.return_value = mock_access_token
        
        result = azure_identity.test_credential(custom_scope)
        
        assert result is True
        azure_identity._credential.get_token.assert_called_once_with(custom_scope)

    def test_test_credential_failure(self, azure_identity):
        """Test test_credential returns False when token acquisition fails."""
        azure_identity._credential.get_token.side_effect = Exception("Auth failed")
        
        result = azure_identity.test_credential()
        
        assert result is False

    def test_test_credential_empty_token(self, azure_identity):
        """Test test_credential returns False when token is empty."""
        empty_token = AccessToken(token="", expires_on=1234567890)
        azure_identity._credential.get_token.return_value = empty_token
        
        result = azure_identity.test_credential()
        
        assert result is False

    def test_test_credential_none_token(self, azure_identity):
        """Test test_credential returns False when token is None."""
        azure_identity._credential.get_token.return_value = None
        
        result = azure_identity.test_credential()
        
        assert result is False

    def test_test_credential_token_without_token_attribute(self, azure_identity):
        """Test test_credential returns False when token object lacks token attribute."""
        mock_token = Mock()
        del mock_token.token  # Remove token attribute
        azure_identity._credential.get_token.return_value = mock_token
        
        result = azure_identity.test_credential()
        
        assert result is False

    def test_set_get_correlation_id(self, azure_identity):
        """Test setting and getting correlation ID."""
        test_correlation_id = "test-correlation-123"
        
        # Mock the logger's get_correlation_id to return None initially
        azure_identity.logger.get_correlation_id.return_value = None
        
        # Initially should be None
        assert azure_identity.get_correlation_id() is None
        
        # Set correlation ID and verify
        azure_identity.set_correlation_id(test_correlation_id)
        
        # Mock the return value after setting
        azure_identity.logger.get_correlation_id.return_value = test_correlation_id
        assert azure_identity.get_correlation_id() == test_correlation_id
        
        # Verify it was set on the logger
        azure_identity.logger.set_correlation_id.assert_called_once_with(test_correlation_id)


class TestLoggingIntegration:
    """Test AzureIdentity logging integration."""

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_initialization_logging(self, mock_logger_class, mock_credential):
        """Test that initialization logs appropriate messages."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        service_name = "test_service"
        service_version = "2.0.0"
        
        identity = AzureIdentity(
            service_name=service_name,
            service_version=service_version
        )
        
        # Verify initialization logging
        mock_logger.info.assert_called_with(
            f"Azure Identity initialized for service '{service_name}' v{service_version}"
        )

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_error_logging_on_credential_failure(self, mock_logger_class, mock_credential):
        """Test error logging when credential setup fails."""
        mock_credential.side_effect = Exception("Credential setup failed")
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        with pytest.raises(Exception):
            AzureIdentity()
        
        # Verify error was logged
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args
        assert "Failed to initialize DefaultAzureCredential" in call_args[0][0]
        assert call_args[1]["exc_info"] is True

    def test_debug_logging_on_success(self, azure_identity, mock_access_token):
        """Test debug logging when operations succeed."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        # Test credential retrieval
        azure_identity.get_credential()
        
        # Test token acquisition
        azure_identity.get_token("https://management.azure.com/.default")
        
        # Verify debug messages were logged
        azure_identity.logger.debug.assert_called()

    def test_info_logging_on_token_success(self, azure_identity, mock_access_token):
        """Test info logging when token acquisition succeeds."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        azure_identity.get_token("https://management.azure.com/.default")
        
        # Verify info message was logged for successful token acquisition
        info_calls = azure_identity.logger.info.call_args_list
        assert any("Access token acquired successfully" in call[0][0] for call in info_calls)

    def test_warning_logging_on_test_credential_failure(self, azure_identity):
        """Test warning logging when credential test fails."""
        azure_identity._credential.get_token.side_effect = Exception("Test failed")
        
        result = azure_identity.test_credential()
        
        assert result is False
        # Verify warning was logged
        azure_identity.logger.warning.assert_called()
        call_args = azure_identity.logger.warning.call_args
        assert "Credential test failed" in call_args[0][0]


class TestFactoryFunction:
    """Test create_azure_identity factory function."""

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_create_azure_identity_defaults(self, mock_logger_class, mock_credential):
        """Test factory function with default parameters."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        identity = create_azure_identity()
        
        assert isinstance(identity, AzureIdentity)
        assert identity.service_name == "azure_identity"
        assert identity.service_version == "1.0.0"
        assert identity.enable_token_cache is True
        assert identity.allow_unencrypted_storage is True

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_create_azure_identity_custom_params(self, mock_logger_class, mock_credential):
        """Test factory function with custom parameters."""
        mock_credential.return_value = Mock()
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        custom_options = {"exclude_managed_identity_credential": True}
        
        identity = create_azure_identity(
            service_name="custom_service",
            service_version="3.0.0",
            enable_token_cache=False,
            allow_unencrypted_storage=False,
            custom_credential_options=custom_options,
            connection_string="test_connection_string",
        )
        
        assert identity.service_name == "custom_service"
        assert identity.service_version == "3.0.0"
        assert identity.enable_token_cache is False
        assert identity.allow_unencrypted_storage is False

    def test_create_azure_identity_with_provided_logger(self):
        """Test factory function with provided logger."""
        provided_logger = Mock(spec=AzureLogger)
        provided_logger.tracer = Mock()
        provided_logger.create_span.return_value = MagicMock()
        
        with patch('azpaddypy.mgmt.identity.DefaultAzureCredential') as mock_credential:
            mock_credential.return_value = Mock()
            
            identity = create_azure_identity(logger=provided_logger)
            
            assert identity.logger == provided_logger


class TestTracingIntegration:
    """Test AzureIdentity OpenTelemetry tracing integration."""

    def test_get_credential_creates_span(self, azure_identity):
        """Test that get_credential creates a span."""
        azure_identity.get_credential()
        
        # Verify span was created with correct attributes
        azure_identity.logger.create_span.assert_called_once_with(
            "AzureIdentity.get_credential",
            attributes={
                "service.name": azure_identity.service_name,
                "operation.type": "credential_retrieval"
            }
        )

    def test_get_token_creates_span(self, azure_identity, mock_access_token):
        """Test that get_token creates a span with correct attributes."""
        azure_identity._credential.get_token.return_value = mock_access_token
        scopes = ["https://management.azure.com/.default"]
        
        azure_identity.get_token(scopes)
        
        # Verify span was created with correct attributes
        azure_identity.logger.create_span.assert_called_once_with(
            "AzureIdentity.get_token",
            attributes={
                "service.name": azure_identity.service_name,
                "operation.type": "token_acquisition",
                "token.scopes": ", ".join(scopes),
                "token.scope_count": len(scopes)
            }
        )

    def test_get_token_provider_creates_span(self, azure_identity):
        """Test that get_token_provider creates a span with correct attributes."""
        with patch('azpaddypy.mgmt.identity.get_bearer_token_provider') as mock_provider:
            mock_provider.return_value = Mock()
            scopes = ["https://management.azure.com/.default"]
            
            azure_identity.get_token_provider(scopes)
            
            # Verify span was created with correct attributes
            azure_identity.logger.create_span.assert_called_once_with(
                "AzureIdentity.get_token_provider",
                attributes={
                    "service.name": azure_identity.service_name,
                    "operation.type": "token_provider_creation",
                    "token.scopes": ", ".join(scopes),
                    "token.scope_count": len(scopes)
                }
            )

    def test_test_credential_creates_span(self, azure_identity, mock_access_token):
        """Test that test_credential creates a span with correct attributes."""
        azure_identity._credential.get_token.return_value = mock_access_token
        test_scopes = ["https://graph.microsoft.com/.default"]
        
        azure_identity.test_credential(test_scopes)
        
        # Verify span was created with correct attributes (test_credential creates spans for both itself and get_token)
        span_calls = azure_identity.logger.create_span.call_args_list
        test_credential_calls = [call for call in span_calls if call[0][0] == "AzureIdentity.test_credential"]
        
        assert len(test_credential_calls) == 1
        call_args, call_kwargs = test_credential_calls[0]
        assert call_args[0] == "AzureIdentity.test_credential"
        assert call_kwargs["attributes"]["service.name"] == azure_identity.service_name
        assert call_kwargs["attributes"]["operation.type"] == "credential_test"
        assert call_kwargs["attributes"]["test.scopes"] == ", ".join(test_scopes)

    def test_multiple_spans_in_nested_calls(self, azure_identity, mock_access_token):
        """Test that nested method calls create separate spans."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        # test_credential internally calls get_token, so we should see both spans
        azure_identity.test_credential()
        
        # Verify multiple spans were created
        assert azure_identity.logger.create_span.call_count >= 2


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""

    def test_empty_scopes_list(self, azure_identity):
        """Test behavior with empty scopes list."""
        azure_identity._credential.get_token.return_value = Mock()
        
        # Should work with empty list (though unusual)
        azure_identity.get_token([])
        azure_identity._credential.get_token.assert_called_once_with()

    def test_none_scopes(self, azure_identity):
        """Test behavior when scopes is None."""
        with pytest.raises(TypeError):
            azure_identity.get_token(None)

    def test_invalid_scope_type(self, azure_identity):
        """Test behavior with invalid scope type."""
        with pytest.raises((TypeError, AttributeError)):
            azure_identity.get_token(123)  # Invalid type

    def test_large_number_of_scopes(self, azure_identity, mock_access_token):
        """Test handling of large number of scopes."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        # Create many scopes
        large_scope_list = [f"https://api{i}.example.com/.default" for i in range(100)]
        
        azure_identity.get_token(large_scope_list)
        azure_identity._credential.get_token.assert_called_once_with(*large_scope_list)

    @patch('azpaddypy.mgmt.identity.DefaultAzureCredential')
    @patch('azpaddypy.mgmt.identity.AzureLogger')
    def test_credential_setup_with_invalid_options(self, mock_logger_class, mock_credential):
        """Test credential setup with invalid options."""
        mock_credential.side_effect = ValueError("Invalid credential option")
        mock_logger = Mock(spec=AzureLogger)
        mock_logger.tracer = Mock()
        mock_logger.create_span.return_value = MagicMock()
        mock_logger_class.return_value = mock_logger
        
        with pytest.raises(ValueError, match="Invalid credential option"):
            AzureIdentity(custom_credential_options={"invalid_option": True})

    def test_unicode_and_special_characters_in_scopes(self, azure_identity, mock_access_token):
        """Test handling of Unicode and special characters in scopes."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        # Test with Unicode characters
        unicode_scope = "https://api.example.com/测试/.default"
        azure_identity.get_token(unicode_scope)
        
        azure_identity._credential.get_token.assert_called_once_with(unicode_scope)

    def test_concurrent_token_requests_simulation(self, azure_identity, mock_access_token):
        """Test that multiple rapid token requests work correctly."""
        azure_identity._credential.get_token.return_value = mock_access_token
        
        # Simulate multiple rapid requests
        for i in range(10):
            azure_identity.get_token(f"https://api{i}.example.com/.default")
        
        assert azure_identity._credential.get_token.call_count == 10
