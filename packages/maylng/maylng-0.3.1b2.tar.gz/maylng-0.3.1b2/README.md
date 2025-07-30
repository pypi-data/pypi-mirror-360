# Maylng Python SDK

Python SDK for agentic email management - create email addresses and send emails programmatically for AI agents.

## Installation

```bash
pip install maylng
```

## Quick Start

```python
from maylng import Mayl

# Initialize the SDK
mayl = Mayl(api_key="your-api-key")

# Create a temporary email
email = mayl.email_addresses.create(
    type="temporary",
    expiration_minutes=30
)

# Send an email
sent_email = mayl.emails.send(
    from_email_id=email.id,
    to=[{"email": "user@example.com", "name": "User"}],
    subject="Hello from AI Agent",
    text="This email was sent by an AI agent!"
)

print(f"Email sent with ID: {sent_email.id}")
```

## Features

- 🚀 **Email Address Management**: Create temporary and persistent email addresses
- 📧 **Email Sending**: Send emails with attachments, scheduling, and threading  
- 🤖 **AI Agent Focused**: Built specifically for AI agent email workflows
- 📊 **Analytics**: Track email delivery, opens, and clicks
- 🔒 **Secure**: API key authentication with rate limiting
- 🐍 **Pythonic**: Follows Python best practices with type hints and async support

## Advanced Usage

### Async Support

```python
import asyncio
from maylng import AsyncMayl

async def main():
    mayl = AsyncMayl(api_key="your-api-key")
    
    # Create email address
    email = await mayl.email_addresses.create(
        type="persistent",
        prefix="support"
    )
    
    # Send email with attachment
    await mayl.emails.send(
        from_email_id=email.id,
        to=[{"email": "user@example.com"}],
        subject="Important Document",
        text="Please find the attached document.",
        attachments=[
            {
                "filename": "document.pdf",
                "content_type": "application/pdf",
                "content": "base64_encoded_content"
            }
        ]
    )

asyncio.run(main())
```

### Email Address Management

```python
# Create temporary email (expires in 1 hour)
temp_email = mayl.email_addresses.create(
    type="temporary",
    expiration_minutes=60,
    prefix="agent-temp",
    metadata={"purpose": "verification"}
)

# Create persistent email
persistent_email = mayl.email_addresses.create(
    type="persistent",
    prefix="support",
    domain="custom-domain.com",  # Optional
    metadata={"department": "customer-service"}
)

# List all email addresses
emails = mayl.email_addresses.list(
    type="temporary",
    status="active",
    page=1,
    limit=10
)

# Extend temporary email expiration
extended_email = mayl.email_addresses.extend(
    email_id=temp_email.id,
    additional_minutes=30
)

# Update email metadata
updated_email = mayl.email_addresses.update(
    email_id=persistent_email.id,
    metadata={"updated": True},
    status="active"
)
```

### Email Sending

```python
# Simple text email
simple_email = mayl.emails.send(
    from_email_id=email.id,
    to=[{"email": "recipient@example.com"}],
    subject="Simple Text Email",
    text="Hello from Maylng!"
)

# HTML email with attachments
html_email = mayl.emails.send(
    from_email_id=email.id,
    to=[
        {"email": "user1@example.com", "name": "User One"},
        {"email": "user2@example.com", "name": "User Two"}
    ],
    cc=[{"email": "manager@example.com"}],
    subject="Monthly Report",
    html="""
    <h2>Monthly Report</h2>
    <p>Please find the monthly report attached.</p>
    <p>Best regards,<br>AI Assistant</p>
    """,
    attachments=[
        {
            "filename": "report.pdf",
            "content_type": "application/pdf",
            "content": base64_content
        }
    ],
    metadata={"campaign": "monthly-reports"}
)

# Scheduled email
from datetime import datetime, timedelta

scheduled_email = mayl.emails.send(
    from_email_id=email.id,
    to=[{"email": "recipient@example.com"}],
    subject="Scheduled Email",
    text="This email was scheduled!",
    scheduled_at=datetime.now() + timedelta(hours=1)
)

# Reply to existing thread
reply_email = mayl.emails.send(
    from_email_id=email.id,
    to=[{"email": "original-sender@example.com"}],
    subject="Re: Original Subject",
    text="This is a reply to your email.",
    thread_id="thread_123"
)
```

### Email Management

```python
# List sent emails
sent_emails = mayl.emails.list(
    from_email_id=email.id,
    status="delivered",
    since=datetime.now() - timedelta(days=7),
    page=1,
    limit=20
)

# Get email details
email_details = mayl.emails.get(email_id="email_123")

# Get delivery status
delivery_status = mayl.emails.get_delivery_status(email_id="email_123")
print(f"Status: {delivery_status.status}")
print(f"Opens: {delivery_status.opens}")
print(f"Clicks: {delivery_status.clicks}")

# Cancel scheduled email
mayl.emails.cancel(email_id="scheduled_email_123")

# Resend failed email
resent_email = mayl.emails.resend(email_id="failed_email_123")
```

### Error Handling

```python
from maylng.errors import (
    MaylError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    EmailSendError
)

try:
    email = mayl.emails.send(
        from_email_id="invalid_id",
        to=[{"email": "invalid-email"}],
        subject="Test",
        text="Test message"
    )
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e.message}")
    if e.field:
        print(f"Field: {e.field}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except EmailSendError as e:
    print(f"Failed to send email: {e.message}")
    print(f"Request ID: {e.request_id}")
except MaylError as e:
    print(f"General Mayl error: {e.message}")
```

### Configuration

```python
# Basic configuration
mayl = Mayl(api_key="your-api-key")

# Custom configuration
mayl = Mayl(
    api_key="your-api-key",
    base_url="http://api.mayl.ng:8080",
    timeout=60,  # seconds
    max_retries=3,
    retry_delay=1.0  # seconds
)

# Update configuration
mayl.update_api_key("new-api-key")
mayl.update_base_url("https://new-api.example.com")
```

### Account Information

```python
# Health check
health = mayl.health_check()
print(f"API Status: {health.status}")

# Account details
account = mayl.get_account_info()
print(f"Plan: {account.plan}")
print(f"Emails used: {account.emails_sent_this_month}/{account.email_limit_per_month}")
print(f"Email addresses: {account.email_address_used}/{account.email_address_limit}")
```

## Type Safety

The Python SDK includes comprehensive type hints for better IDE support and type checking:

```python
from maylng.types import (
    EmailAddress,
    SentEmail,
    CreateEmailAddressOptions,
    SendEmailOptions,
    EmailRecipient,
    EmailAttachment
)

# Type-safe email creation
options: CreateEmailAddressOptions = {
    "type": "temporary",
    "expiration_minutes": 60,
    "metadata": {"purpose": "demo"}
}

email: EmailAddress = mayl.email_addresses.create(**options)
```

## Requirements

- Python 3.8+
- httpx >= 0.25.0
- pydantic >= 2.0.0

## Error Reference

- `AuthenticationError` - Invalid API key
- `AuthorizationError` - Insufficient permissions  
- `ValidationError` - Invalid input parameters
- `NotFoundError` - Resource not found
- `RateLimitError` - Rate limit exceeded
- `NetworkError` - Network connectivity issues
- `ServerError` - Server-side errors
- `TimeoutError` - Request timeout
- `EmailAddressError` - Email address specific errors
- `EmailSendError` - Email sending specific errors

## Support

- 📖 [Documentation](https://docs.maylng.com)
- 💬 [Discord Community](https://discord.gg/maylng)
- 🐛 [Issue Tracker](https://github.com/maylng/mayl-sdk/issues)
- 📧 [Email Support](mailto:support@maylng.com)

## License

MIT License - see [LICENSE](../LICENSE) for details.
