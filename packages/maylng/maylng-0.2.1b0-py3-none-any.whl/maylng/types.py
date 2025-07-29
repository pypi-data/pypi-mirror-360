"""
Type definitions for the Maylng Python SDK.

This module contains all the type definitions used throughout the SDK,
including request/response models, configuration types, and data structures.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union, TypeVar, Generic
from pydantic import BaseModel, Field, EmailStr, validator
import sys

if sys.version_info >= (3, 11):
    from typing import TypedDict, Required, NotRequired
elif sys.version_info >= (3, 10):
    from typing import TypedDict
    from typing_extensions import Required, NotRequired
else:
    from typing_extensions import TypedDict, Required, NotRequired

# TypeVar for generic types
T = TypeVar('T')

# Configuration Types
class MaylConfig(TypedDict, total=False):
    """Configuration options for the Mayl client."""
    
    api_key: Required[str]  # Required field
    base_url: NotRequired[Optional[str]]  # Optional fields
    timeout: NotRequired[Optional[float]]
    max_retries: NotRequired[Optional[int]]
    retry_delay: NotRequired[Optional[float]]


# Email Address Types
class CreateEmailAddressOptions(TypedDict, total=False):
    """Options for creating an email address."""
    
    type: Literal["temporary", "persistent"]
    prefix: Optional[str]
    domain: Optional[str]
    expiration_minutes: Optional[int]
    metadata: Optional[Dict[str, Any]]


class EmailAddress(BaseModel):
    """Represents an email address created through the SDK."""
    
    id: str = Field(..., description="Unique identifier for the email address")
    email: EmailStr = Field(..., description="The actual email address")
    type: Literal["temporary", "persistent"] = Field(..., description="Type of email address")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp (null for persistent emails)")
    status: Literal["active", "expired", "disabled"] = Field(..., description="Current status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Associated metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Email Types
class EmailRecipient(BaseModel):
    """Email recipient information."""
    
    email: EmailStr = Field(..., description="Email address")
    name: Optional[str] = Field(None, description="Display name")


class EmailAttachment(BaseModel):
    """Email attachment information."""
    
    filename: str = Field(..., description="Filename")
    content_type: str = Field(..., description="Content type (MIME type)")
    content: Union[str, bytes] = Field(..., description="File content as base64 string or bytes")
    cid: Optional[str] = Field(None, description="Content ID for inline attachments")


class SendEmailOptions(TypedDict):
    """Options for sending an email."""
    
    from_email_id: str
    to: List[Dict[str, str]]
    subject: str
    
    # Optional fields
    cc: Optional[List[Dict[str, str]]]
    bcc: Optional[List[Dict[str, str]]]
    text: Optional[str]
    html: Optional[str]
    attachments: Optional[List[Dict[str, Any]]]
    headers: Optional[Dict[str, str]]
    scheduled_at: Optional[datetime]
    thread_id: Optional[str]
    metadata: Optional[Dict[str, Any]]


class SentEmail(BaseModel):
    """Represents a sent email."""
    
    id: str = Field(..., description="Unique identifier for the sent email")
    from_email_id: str = Field(..., description="Email address ID used to send")
    to: List[EmailRecipient] = Field(..., description="Recipients")
    cc: Optional[List[EmailRecipient]] = Field(None, description="CC recipients")
    bcc: Optional[List[EmailRecipient]] = Field(None, description="BCC recipients")
    subject: str = Field(..., description="Subject")
    sent_at: datetime = Field(..., description="Send timestamp")
    status: Literal["sent", "delivered", "failed", "scheduled"] = Field(..., description="Delivery status")
    thread_id: Optional[str] = Field(None, description="Thread ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Associated metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# API Response Types
class APIResponse(BaseModel):
    """API response wrapper."""
    
    data: Any = Field(..., description="Response data")
    success: bool = Field(..., description="Success indicator")
    error: Optional[str] = Field(None, description="Error message if any")
    request_id: Optional[str] = Field(None, description="Request ID for debugging")


class PaginationOptions(TypedDict, total=False):
    """Pagination options."""
    
    page: Optional[int]
    limit: Optional[int]


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""
    
    items: List[T] = Field(..., description="Array of items")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")


# Health and Account Types
class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: Literal["healthy", "unhealthy"] = Field(..., description="Health status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Check timestamp")
    api_version: Optional[str] = Field(None, description="API version")
    account_id: Optional[str] = Field(None, description="Account ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AccountInfo(BaseModel):
    """Account information and usage statistics."""
    
    account_id: str = Field(..., description="Account ID")
    plan: str = Field(..., description="Account plan")
    email_address_limit: int = Field(..., description="Email address limit")
    email_address_used: int = Field(..., description="Email addresses used")
    emails_sent_this_month: int = Field(..., description="Emails sent this month")
    email_limit_per_month: int = Field(..., description="Email limit per month")
    created_at: datetime = Field(..., description="Account creation date")
    last_activity: datetime = Field(..., description="Last activity date")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeliveryStatus(BaseModel):
    """Email delivery status and analytics."""
    
    status: Literal["sent", "delivered", "failed", "scheduled"] = Field(..., description="Delivery status")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")
    failure_reason: Optional[str] = Field(None, description="Failure reason if failed")
    bounce_type: Optional[str] = Field(None, description="Bounce type if bounced")
    opens: Optional[int] = Field(None, description="Number of opens")
    clicks: Optional[int] = Field(None, description="Number of clicks")
    last_opened_at: Optional[datetime] = Field(None, description="Last opened timestamp")
    last_clicked_at: Optional[datetime] = Field(None, description="Last clicked timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Update options types
class UpdateEmailAddressOptions(TypedDict, total=False):
    """Options for updating an email address."""
    
    metadata: Optional[Dict[str, Any]]
    status: Optional[Literal["active", "disabled"]]


class ListEmailAddressesOptions(TypedDict, total=False):
    """Options for listing email addresses."""
    
    type: Optional[Literal["temporary", "persistent"]]
    status: Optional[Literal["active", "expired", "disabled"]]
    page: Optional[int]
    limit: Optional[int]


class ListEmailsOptions(TypedDict, total=False):
    """Options for listing sent emails."""
    
    from_email_id: Optional[str]
    status: Optional[Literal["sent", "delivered", "failed", "scheduled"]]
    thread_id: Optional[str]
    since: Optional[datetime]
    until: Optional[datetime]
    page: Optional[int]
    limit: Optional[int]
