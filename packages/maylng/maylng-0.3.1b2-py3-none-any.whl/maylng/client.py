"""
Main Mayl client classes for both synchronous and asynchronous usage.

This module provides the primary entry points for interacting with the Maylng API,
including client initialization, configuration, and high-level operations.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .http_client import HTTPClient, AsyncHTTPClient
from .email_address_service import EmailAddressService, AsyncEmailAddressService
from .email_service import EmailService, AsyncEmailService
from .types import MaylConfig, HealthCheckResponse, AccountInfo
from .errors import ValidationError, MaylError


class Mayl:
    """
    Main synchronous Mayl client for managing email addresses and sending emails.
    
    Example:
        ```python
        from maylng import Mayl
        
        mayl = Mayl(api_key="your-api-key")
        
        # Create email address
        email = mayl.email_addresses.create(
            type="temporary",
            expiration_minutes=30
        )
        
        # Send email
        sent_email = mayl.emails.send(
            from_email_id=email.id,
            to=[{"email": "user@example.com"}],
            subject="Hello",
            text="Hello from Maylng!"
        )
        ```
    """
    
    def __init__(self, **config: Any) -> None:
        """
        Initialize the Mayl client.
        
        Args:
            api_key: Your Maylng API key
            base_url: Custom API base URL (optional)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        
        Raises:
            ValidationError: If required configuration is missing or invalid
        """
        self._validate_config(config)
        
        self.http_client = HTTPClient(config)  # type: ignore
        self.email_addresses = EmailAddressService(self.http_client)
        self.emails = EmailService(self.http_client)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate client configuration."""
        if not isinstance(config, dict):
            raise ValidationError("Configuration must be a dictionary")
        
        if "api_key" not in config:
            raise ValidationError("api_key is required")
        
        if not isinstance(config["api_key"], str):
            raise ValidationError("api_key must be a string")
        
        if "base_url" in config and not isinstance(config["base_url"], str):
            raise ValidationError("base_url must be a string")
        
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                raise ValidationError("timeout must be a positive number")
        
        if "max_retries" in config:
            if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
                raise ValidationError("max_retries must be a non-negative integer")
        
        if "retry_delay" in config:
            if not isinstance(config["retry_delay"], (int, float)) or config["retry_delay"] < 0:
                raise ValidationError("retry_delay must be a non-negative number")
    
    def update_api_key(self, api_key: str) -> None:
        """
        Update the API key.
        
        Args:
            api_key: New API key
            
        Raises:
            ValidationError: If API key is invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise ValidationError("API key is required and must be a string")
        
        self.http_client.update_api_key(api_key)
    
    def update_base_url(self, base_url: str) -> None:
        """
        Update the base URL.
        
        Args:
            base_url: New base URL
            
        Raises:
            ValidationError: If base URL is invalid
        """
        if not base_url or not isinstance(base_url, str):
            raise ValidationError("Base URL is required and must be a string")
        
        self.http_client.update_base_url(base_url)
    
    def health_check(self) -> HealthCheckResponse:
        """
        Perform a health check to verify API connectivity and authentication.
        
        Returns:
            Health check response with status and details
            
        Raises:
            MaylError: If health check fails
        """
        try:
            response = self.http_client.get("/health")
            
            data = response.get("data", {})
            return HealthCheckResponse(
                status="healthy",
                message=data.get("message", "API is healthy"),
                timestamp=datetime.now(),
                api_version=data.get("api_version"),
                account_id=data.get("account_id")
            )
        except Exception as error:
            return HealthCheckResponse(
                status="unhealthy",
                message=str(error),
                timestamp=datetime.now(),
                api_version=None,
                account_id=None
            )
    
    def get_account_info(self) -> AccountInfo:
        """
        Get account information and usage statistics.
        
        Returns:
            Account information including limits and usage
            
        Raises:
            MaylError: If request fails
        """
        response = self.http_client.get("/account")
        
        if not response.get("success", True):
            raise MaylError(response.get("error", "Failed to get account info"))
        
        data = response["data"]
        
        return AccountInfo(
            account_id=data["account_id"],
            plan=data["plan"],
            email_address_limit=data["email_address_limit"],
            email_address_used=data["email_address_used"],
            emails_sent_this_month=data["emails_sent_this_month"],
            email_limit_per_month=data["email_limit_per_month"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            last_activity=datetime.fromisoformat(data["last_activity"].replace("Z", "+00:00"))
        )
    
    def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        self.http_client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncMayl:
    """
    Main asynchronous Mayl client for managing email addresses and sending emails.
    
    Example:
        ```python
        import asyncio
        from maylng import AsyncMayl
        
        async def main():
            mayl = AsyncMayl(api_key="your-api-key")
            
            # Create email address
            email = await mayl.email_addresses.create(
                type="temporary",
                expiration_minutes=30
            )
            
            # Send email
            sent_email = await mayl.emails.send(
                from_email_id=email.id,
                to=[{"email": "user@example.com"}],
                subject="Hello",
                text="Hello from Maylng!"
            )
            
            await mayl.close()
        
        asyncio.run(main())
        ```
    """
    
    def __init__(self, **config: Any) -> None:
        """
        Initialize the async Mayl client.
        
        Args:
            api_key: Your Maylng API key
            base_url: Custom API base URL (optional)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        
        Raises:
            ValidationError: If required configuration is missing or invalid
        """
        self._validate_config(config)
        
        self.http_client = AsyncHTTPClient(config)  # type: ignore
        self.email_addresses = AsyncEmailAddressService(self.http_client)
        self.emails = AsyncEmailService(self.http_client)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate client configuration."""
        if not isinstance(config, dict):
            raise ValidationError("Configuration must be a dictionary")
        
        if "api_key" not in config:
            raise ValidationError("api_key is required")
        
        if not isinstance(config["api_key"], str):
            raise ValidationError("api_key must be a string")
        
        if "base_url" in config and not isinstance(config["base_url"], str):
            raise ValidationError("base_url must be a string")
        
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                raise ValidationError("timeout must be a positive number")
        
        if "max_retries" in config:
            if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
                raise ValidationError("max_retries must be a non-negative integer")
        
        if "retry_delay" in config:
            if not isinstance(config["retry_delay"], (int, float)) or config["retry_delay"] < 0:
                raise ValidationError("retry_delay must be a non-negative number")
    
    def update_api_key(self, api_key: str) -> None:
        """
        Update the API key.
        
        Args:
            api_key: New API key
            
        Raises:
            ValidationError: If API key is invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise ValidationError("API key is required and must be a string")
        
        self.http_client.update_api_key(api_key)
    
    def update_base_url(self, base_url: str) -> None:
        """
        Update the base URL.
        
        Args:
            base_url: New base URL
            
        Raises:
            ValidationError: If base URL is invalid
        """
        if not base_url or not isinstance(base_url, str):
            raise ValidationError("Base URL is required and must be a string")
        
        self.http_client.update_base_url(base_url)
    
    async def health_check(self) -> HealthCheckResponse:
        """
        Perform a health check to verify API connectivity and authentication.
        
        Returns:
            Health check response with status and details
            
        Raises:
            MaylError: If health check fails
        """
        try:
            response = await self.http_client.get("/health")
            
            data = response.get("data", {})
            return HealthCheckResponse(
                status="healthy",
                message=data.get("message", "API is healthy"),
                timestamp=datetime.now(),
                api_version=data.get("api_version"),
                account_id=data.get("account_id")
            )
        except Exception as error:
            return HealthCheckResponse(
                status="unhealthy",
                message=str(error),
                timestamp=datetime.now(),
                api_version=None,
                account_id=None
            )
    
    async def get_account_info(self) -> AccountInfo:
        """
        Get account information and usage statistics.
        
        Returns:
            Account information including limits and usage
            
        Raises:
            MaylError: If request fails
        """
        response = await self.http_client.get("/account")
        
        if not response.get("success", True):
            raise MaylError(response.get("error", "Failed to get account info"))
        
        data = response["data"]
        
        return AccountInfo(
            account_id=data["account_id"],
            plan=data["plan"],
            email_address_limit=data["email_address_limit"],
            email_address_used=data["email_address_used"],
            emails_sent_this_month=data["emails_sent_this_month"],
            email_limit_per_month=data["email_limit_per_month"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            last_activity=datetime.fromisoformat(data["last_activity"].replace("Z", "+00:00"))
        )
    
    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        await self.http_client.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def create_mayl(**config: Any) -> Mayl:
    """
    Create a new synchronous Mayl client instance.
    
    Args:
        **config: Configuration options (api_key required)
        
    Returns:
        Configured Mayl client instance
        
    Example:
        ```python
        from maylng import create_mayl
        
        mayl = create_mayl(api_key="your-api-key")
        ```
    """
    return Mayl(**config)


def create_async_mayl(**config: Any) -> AsyncMayl:
    """
    Create a new asynchronous Mayl client instance.
    
    Args:
        **config: Configuration options (api_key required)
        
    Returns:
        Configured AsyncMayl client instance
        
    Example:
        ```python
        from maylng import create_async_mayl
        
        mayl = create_async_mayl(api_key="your-api-key")
        ```
    """
    return AsyncMayl(**config)
