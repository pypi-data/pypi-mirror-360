"""
Service for sending and managing emails.

This module provides functionality to send emails, manage attachments,
schedule emails, and track delivery status through the Maylng API.
"""

import base64
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from .http_client import HTTPClient, AsyncHTTPClient
from .types import (
    SendEmailOptions,
    SentEmail,
    EmailRecipient,
    EmailAttachment,
    ListEmailsOptions,
    PaginatedResponse,
    DeliveryStatus,
)
from .errors import ValidationError, EmailSendError


class BaseEmailService:
    """Base class for email service functionality."""
    
    def _validate_email_address(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_email_recipient(self, recipient: Dict[str, str], field: str) -> None:
        """Validate email recipient."""
        if not isinstance(recipient, dict):
            raise ValidationError(f"{field} must be a dictionary")
        
        if "email" not in recipient:
            raise ValidationError(f"{field}.email is required")
        
        if not isinstance(recipient["email"], str):
            raise ValidationError(f"{field}.email must be a string")
        
        if not self._validate_email_address(recipient["email"]):
            raise ValidationError(f"{field}.email is not a valid email address")
        
        if "name" in recipient and not isinstance(recipient["name"], str):
            raise ValidationError(f"{field}.name must be a string")
    
    def _validate_email_attachment(self, attachment: Dict[str, Any], field: str) -> None:
        """Validate email attachment."""
        if not isinstance(attachment, dict):
            raise ValidationError(f"{field} must be a dictionary")
        
        required_fields = ["filename", "content_type", "content"]
        for field_name in required_fields:
            if field_name not in attachment:
                raise ValidationError(f"{field}.{field_name} is required")
        
        if not isinstance(attachment["filename"], str):
            raise ValidationError(f"{field}.filename must be a string")
        
        if not isinstance(attachment["content_type"], str):
            raise ValidationError(f"{field}.content_type must be a string")
        
        if not isinstance(attachment["content"], (str, bytes)):
            raise ValidationError(f"{field}.content must be a string or bytes")
        
        if "cid" in attachment and not isinstance(attachment["cid"], str):
            raise ValidationError(f"{field}.cid must be a string")
    
    def _validate_send_options(self, options: Dict[str, Any]) -> None:
        """Validate send email options."""
        if not isinstance(options, dict):
            raise ValidationError("Options must be a dictionary")
        
        # Validate required fields
        if "from_email_id" not in options:
            raise ValidationError("from_email_id is required")
        
        if not isinstance(options["from_email_id"], str):
            raise ValidationError("from_email_id must be a string")
        
        if "to" not in options:
            raise ValidationError("to is required")
        
        if not isinstance(options["to"], list) or len(options["to"]) == 0:
            raise ValidationError("At least one recipient in 'to' is required")
        
        # Validate recipients
        for i, recipient in enumerate(options["to"]):
            self._validate_email_recipient(recipient, f"to[{i}]")
        
        if "cc" in options:
            if not isinstance(options["cc"], list):
                raise ValidationError("cc must be a list")
            for i, recipient in enumerate(options["cc"]):
                self._validate_email_recipient(recipient, f"cc[{i}]")
        
        if "bcc" in options:
            if not isinstance(options["bcc"], list):
                raise ValidationError("bcc must be a list")
            for i, recipient in enumerate(options["bcc"]):
                self._validate_email_recipient(recipient, f"bcc[{i}]")
        
        # Validate subject
        if "subject" not in options:
            raise ValidationError("subject is required")
        
        if not isinstance(options["subject"], str) or not options["subject"].strip():
            raise ValidationError("subject must be a non-empty string")
        
        # Validate content
        if "text" not in options and "html" not in options:
            raise ValidationError("Either text or html content is required")
        
        if "text" in options and not isinstance(options["text"], str):
            raise ValidationError("text content must be a string")
        
        if "html" in options and not isinstance(options["html"], str):
            raise ValidationError("html content must be a string")
        
        # Validate attachments
        if "attachments" in options:
            if not isinstance(options["attachments"], list):
                raise ValidationError("attachments must be a list")
            
            for i, attachment in enumerate(options["attachments"]):
                self._validate_email_attachment(attachment, f"attachments[{i}]")
        
        # Validate scheduled_at
        if "scheduled_at" in options:
            if not isinstance(options["scheduled_at"], datetime):
                raise ValidationError("scheduled_at must be a datetime object")
            
            if options["scheduled_at"] <= datetime.now():
                raise ValidationError("scheduled_at must be in the future")
        
        # Validate thread_id
        if "thread_id" in options and not isinstance(options["thread_id"], str):
            raise ValidationError("thread_id must be a string")
        
        # Validate metadata
        if "metadata" in options and not isinstance(options["metadata"], dict):
            raise ValidationError("metadata must be a dictionary")
        
        # Validate headers
        if "headers" in options and not isinstance(options["headers"], dict):
            raise ValidationError("headers must be a dictionary")
    
    def _process_attachment(self, attachment: Dict[str, Any]) -> Dict[str, Any]:
        """Process attachment for API request."""
        processed = {
            "filename": attachment["filename"],
            "content_type": attachment["content_type"],
            "cid": attachment.get("cid")
        }
        
        # Convert content to base64 if it's bytes
        if isinstance(attachment["content"], bytes):
            processed["content"] = base64.b64encode(attachment["content"]).decode('utf-8')
        else:
            processed["content"] = attachment["content"]
        
        return processed
    
    def _build_list_params(self, options: Optional[Dict[str, Any]] = None) -> str:
        """Build query parameters for list endpoint."""
        if not options:
            return ""
        
        params = {}
        
        if "from_email_id" in options:
            params["from_email_id"] = options["from_email_id"]
        
        if "status" in options:
            params["status"] = options["status"]
        
        if "thread_id" in options:
            params["thread_id"] = options["thread_id"]
        
        if "since" in options and options["since"] is not None:
            params["since"] = options["since"].isoformat()
        
        if "until" in options and options["until"] is not None:
            params["until"] = options["until"].isoformat()
        
        if "page" in options:
            params["page"] = str(options["page"])
        
        if "limit" in options:
            params["limit"] = str(options["limit"])
        
        return f"?{urlencode(params)}" if params else ""
    
    def _parse_sent_email(self, data: Dict[str, Any]) -> SentEmail:
        """Parse sent email data from API response."""
        # Convert date strings to datetime objects
        sent_at = datetime.fromisoformat(data["sent_at"].replace("Z", "+00:00"))
        
        # Parse recipients
        to_recipients = [EmailRecipient(**recipient) for recipient in data["to"]]
        cc_recipients = [EmailRecipient(**recipient) for recipient in data.get("cc", [])]
        bcc_recipients = [EmailRecipient(**recipient) for recipient in data.get("bcc", [])]
        
        return SentEmail(
            id=data["id"],
            from_email_id=data["from_email_id"],
            to=to_recipients,
            cc=cc_recipients if cc_recipients else None,
            bcc=bcc_recipients if bcc_recipients else None,
            subject=data["subject"],
            sent_at=sent_at,
            status=data["status"],
            thread_id=data.get("thread_id"),
            metadata=data.get("metadata")
        )
    
    def _parse_delivery_status(self, data: Dict[str, Any]) -> DeliveryStatus:
        """Parse delivery status data from API response."""
        delivered_at = None
        if data.get("delivered_at"):
            delivered_at = datetime.fromisoformat(data["delivered_at"].replace("Z", "+00:00"))
        
        last_opened_at = None
        if data.get("last_opened_at"):
            last_opened_at = datetime.fromisoformat(data["last_opened_at"].replace("Z", "+00:00"))
        
        last_clicked_at = None
        if data.get("last_clicked_at"):
            last_clicked_at = datetime.fromisoformat(data["last_clicked_at"].replace("Z", "+00:00"))
        
        return DeliveryStatus(
            status=data["status"],
            delivered_at=delivered_at,
            failure_reason=data.get("failure_reason"),
            bounce_type=data.get("bounce_type"),
            opens=data.get("opens"),
            clicks=data.get("clicks"),
            last_opened_at=last_opened_at,
            last_clicked_at=last_clicked_at
        )


class EmailService(BaseEmailService):
    """Synchronous service for sending and managing emails."""
    
    def __init__(self, http_client: HTTPClient) -> None:
        self.http_client = http_client
    
    def send(self, **options: Any) -> SentEmail:
        """Send an email."""
        self._validate_send_options(options)
        
        # Prepare request body
        request_body = {
            "from_email_id": options["from_email_id"],
            "to": options["to"],
            "subject": options["subject"]
        }
        
        # Add optional fields
        if "cc" in options:
            request_body["cc"] = options["cc"]
        
        if "bcc" in options:
            request_body["bcc"] = options["bcc"]
        
        if "text" in options:
            request_body["text"] = options["text"]
        
        if "html" in options:
            request_body["html"] = options["html"]
        
        if "attachments" in options and options["attachments"] is not None:
            request_body["attachments"] = [
                self._process_attachment(attachment) 
                for attachment in options["attachments"]
            ]
        
        if "headers" in options:
            request_body["headers"] = options["headers"]
        
        if "scheduled_at" in options and options["scheduled_at"] is not None:
            request_body["scheduled_at"] = options["scheduled_at"].isoformat()
        
        if "thread_id" in options:
            request_body["thread_id"] = options["thread_id"]
        
        if "metadata" in options:
            request_body["metadata"] = options["metadata"]
        
        response = self.http_client.post("/emails/send", json=request_body)
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to send email"))
        
        return self._parse_sent_email(response["data"])
    
    def get(self, email_id: str) -> SentEmail:
        """Get a sent email by ID."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = self.http_client.get(f"/emails/{email_id}")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to get email"))
        
        return self._parse_sent_email(response["data"])
    
    def list(self, **options: Any) -> PaginatedResponse[SentEmail]:
        """List sent emails with pagination and filters."""
        query_string = self._build_list_params(options if options else None)
        endpoint = f"/emails{query_string}"
        
        response = self.http_client.get(endpoint)
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to list emails"))
        
        data = response["data"]
        items = [self._parse_sent_email(item) for item in data["items"]]
        
        return PaginatedResponse(
            items=items,
            page=data["page"],
            limit=data["limit"],
            total=data["total"],
            total_pages=data["total_pages"],
            has_next=data["has_next"],
            has_previous=data["has_previous"]
        )
    
    def cancel(self, email_id: str) -> None:
        """Cancel a scheduled email."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = self.http_client.post(f"/emails/{email_id}/cancel")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to cancel email"))
    
    def resend(self, email_id: str) -> SentEmail:
        """Resend a failed email."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = self.http_client.post(f"/emails/{email_id}/resend")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to resend email"))
        
        return self._parse_sent_email(response["data"])
    
    def get_delivery_status(self, email_id: str) -> DeliveryStatus:
        """Get email delivery status and analytics."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = self.http_client.get(f"/emails/{email_id}/status")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to get delivery status"))
        
        return self._parse_delivery_status(response["data"])


class AsyncEmailService(BaseEmailService):
    """Asynchronous service for sending and managing emails."""
    
    def __init__(self, http_client: AsyncHTTPClient) -> None:
        self.http_client = http_client
    
    async def send(self, **options: Any) -> SentEmail:
        """Send an email."""
        self._validate_send_options(options)
        
        # Prepare request body
        request_body = {
            "from_email_id": options["from_email_id"],
            "to": options["to"],
            "subject": options["subject"]
        }
        
        # Add optional fields
        if "cc" in options:
            request_body["cc"] = options["cc"]
        
        if "bcc" in options:
            request_body["bcc"] = options["bcc"]
        
        if "text" in options:
            request_body["text"] = options["text"]
        
        if "html" in options:
            request_body["html"] = options["html"]
        
        if "attachments" in options and options["attachments"] is not None:
            request_body["attachments"] = [
                self._process_attachment(attachment) 
                for attachment in options["attachments"]
            ]
        
        if "headers" in options:
            request_body["headers"] = options["headers"]
        
        if "scheduled_at" in options and options["scheduled_at"] is not None:
            request_body["scheduled_at"] = options["scheduled_at"].isoformat()
        
        if "thread_id" in options:
            request_body["thread_id"] = options["thread_id"]
        
        if "metadata" in options:
            request_body["metadata"] = options["metadata"]
        
        response = await self.http_client.post("/emails/send", json=request_body)
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to send email"))
        
        return self._parse_sent_email(response["data"])
    
    async def get(self, email_id: str) -> SentEmail:
        """Get a sent email by ID."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = await self.http_client.get(f"/emails/{email_id}")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to get email"))
        
        return self._parse_sent_email(response["data"])
    
    async def list(self, **options: Any) -> PaginatedResponse[SentEmail]:
        """List sent emails with pagination and filters."""
        query_string = self._build_list_params(options if options else None)
        endpoint = f"/emails{query_string}"
        
        response = await self.http_client.get(endpoint)
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to list emails"))
        
        data = response["data"]
        items = [self._parse_sent_email(item) for item in data["items"]]
        
        return PaginatedResponse(
            items=items,
            page=data["page"],
            limit=data["limit"],
            total=data["total"],
            total_pages=data["total_pages"],
            has_next=data["has_next"],
            has_previous=data["has_previous"]
        )
    
    async def cancel(self, email_id: str) -> None:
        """Cancel a scheduled email."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = await self.http_client.post(f"/emails/{email_id}/cancel")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to cancel email"))
    
    async def resend(self, email_id: str) -> SentEmail:
        """Resend a failed email."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = await self.http_client.post(f"/emails/{email_id}/resend")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to resend email"))
        
        return self._parse_sent_email(response["data"])
    
    async def get_delivery_status(self, email_id: str) -> DeliveryStatus:
        """Get email delivery status and analytics."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email ID is required and must be a string")
        
        response = await self.http_client.get(f"/emails/{email_id}/status")
        
        if not response.get("success", True):
            raise EmailSendError(response.get("error", "Failed to get delivery status"))
        
        return self._parse_delivery_status(response["data"])
