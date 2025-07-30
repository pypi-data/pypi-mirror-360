"""
Maylng Python SDK

A Python SDK for agentic email management. Create email addresses and send emails 
programmatically for AI agents.

Basic Usage:
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
        subject="Hello from AI Agent",
        text="This email was sent by an AI agent!"
    )
    ```

Async Usage:
    ```python
    from maylng import AsyncMayl
    import asyncio
    
    async def main():
        mayl = AsyncMayl(api_key="your-api-key")
        email = await mayl.email_addresses.create(type="temporary")
        await mayl.emails.send(
            from_email_id=email.id,
            to=[{"email": "user@example.com"}],
            subject="Hello",
            text="Hello from async!"
        )
    
    asyncio.run(main())
    ```
"""

from .client import Mayl, AsyncMayl, create_mayl, create_async_mayl
from .types import (
    MaylConfig,
    CreateEmailAddressOptions,
    EmailAddress,
    EmailRecipient,
    EmailAttachment,
    SendEmailOptions,
    SentEmail,
    APIResponse,
    PaginationOptions,
    PaginatedResponse,
    HealthCheckResponse,
    AccountInfo,
    DeliveryStatus,
)
from .errors import (
    MaylError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    NetworkError,
    ServerError,
    TimeoutError,
    EmailAddressError,
    EmailSendError,
)

__version__ = "0.2.1b0"
__author__ = "KnextKoder"
__email__ = "hello@knextkoder.com"
__license__ = "MIT"

__all__ = [
    # Main clients
    "Mayl",
    "AsyncMayl",
    "create_mayl",
    "create_async_mayl",
    
    # Types
    "MaylConfig",
    "CreateEmailAddressOptions", 
    "EmailAddress",
    "EmailRecipient",
    "EmailAttachment",
    "SendEmailOptions",
    "SentEmail",
    "APIResponse",
    "PaginationOptions",
    "PaginatedResponse",
    "HealthCheckResponse",
    "AccountInfo",
    "DeliveryStatus",
    
    # Errors
    "MaylError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError", 
    "RateLimitError",
    "NetworkError",
    "ServerError",
    "TimeoutError",
    "EmailAddressError",
    "EmailSendError",
]
