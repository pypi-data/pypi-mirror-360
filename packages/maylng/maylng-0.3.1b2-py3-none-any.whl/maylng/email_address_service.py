"""
Service for managing email addresses (temporary and persistent).

This module provides functionality to create, list, update, extend, and delete
email addresses through the Maylng API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast
from urllib.parse import urlencode

from .http_client import HTTPClient, AsyncHTTPClient
from .types import (
    CreateEmailAddressOptions,
    EmailAddress,
    ListEmailAddressesOptions,
    UpdateEmailAddressOptions,
    PaginatedResponse,
)
from .errors import ValidationError, EmailAddressError


class BaseEmailAddressService:
    """Base class for email address service functionality."""
    
    def _validate_create_options(self, options: CreateEmailAddressOptions) -> None:
        """Validate create email address options."""
        if not isinstance(options, dict):
            raise ValidationError("Options must be a dictionary")
        
        if "type" not in options:
            raise ValidationError("Type is required")
        
        if options["type"] not in ["temporary", "persistent"]:
            raise ValidationError("Type must be either 'temporary' or 'persistent'")
        
        if "prefix" in options and not isinstance(options["prefix"], str):
            raise ValidationError("Prefix must be a string")
        
        if "domain" in options and not isinstance(options["domain"], str):
            raise ValidationError("Domain must be a string")
        
        if "expiration_minutes" in options:
            if not isinstance(options["expiration_minutes"], int) or options["expiration_minutes"] <= 0:
                raise ValidationError("Expiration minutes must be a positive integer")
            
            if options["type"] == "persistent":
                raise ValidationError("Expiration minutes cannot be set for persistent email addresses")
        
        if "metadata" in options and not isinstance(options["metadata"], dict):
            raise ValidationError("Metadata must be a dictionary")
    
    def _validate_email_id(self, email_id: str) -> None:
        """Validate email address ID."""
        if not email_id or not isinstance(email_id, str):
            raise ValidationError("Email address ID is required and must be a string")
    
    def _validate_update_options(self, updates: UpdateEmailAddressOptions) -> None:
        """Validate update options."""
        if not isinstance(updates, dict):
            raise ValidationError("Updates must be a dictionary")
        
        if not updates:
            raise ValidationError("At least one update field is required")
        
        if "metadata" in updates and not isinstance(updates["metadata"], dict):
            raise ValidationError("Metadata must be a dictionary")
        
        if "status" in updates and updates["status"] not in ["active", "disabled"]:
            raise ValidationError("Status must be either 'active' or 'disabled'")
    
    def _build_list_params(self, options: Optional[ListEmailAddressesOptions] = None) -> str:
        """Build query parameters for list endpoint."""
        if not options:
            return ""
        
        params = {}
        
        if "type" in options:
            params["type"] = options["type"]
        
        if "status" in options:
            params["status"] = options["status"]
        
        if "page" in options:
            params["page"] = str(options["page"])
        
        if "limit" in options:
            params["limit"] = str(options["limit"])
        
        return f"?{urlencode(params)}" if params else ""
    
    def _parse_email_address(self, data: Dict[str, Any]) -> EmailAddress:
        """Parse email address data from API response."""
        # Convert date strings to datetime objects
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        expires_at = None
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        
        return EmailAddress(
            id=data["id"],
            email=data["email"],
            type=data["type"],
            created_at=created_at,
            expires_at=expires_at,
            status=data["status"],
            metadata=data.get("metadata")
        )


class EmailAddressService(BaseEmailAddressService):
    """Synchronous service for managing email addresses."""
    
    def __init__(self, http_client: HTTPClient) -> None:
        self.http_client = http_client
    
    def create(self, **options: Any) -> EmailAddress:
        """Create a new email address."""
        create_options = cast(CreateEmailAddressOptions, options)
        self._validate_create_options(create_options)
        
        response = self.http_client.post("/email-addresses", json=dict(create_options))
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to create email address"))
        
        return self._parse_email_address(response["data"])
    
    def get(self, email_id: str) -> EmailAddress:
        """Get an email address by ID."""
        self._validate_email_id(email_id)
        
        response = self.http_client.get(f"/email-addresses/{email_id}")
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to get email address"))
        
        return self._parse_email_address(response["data"])
    
    def list(self, **options: Any) -> PaginatedResponse[EmailAddress]:
        """List email addresses with pagination and filters."""
        list_options = cast(ListEmailAddressesOptions, options)
        query_string = self._build_list_params(list_options)
        endpoint = f"/email-addresses{query_string}"
        
        response = self.http_client.get(endpoint)
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to list email addresses"))
        
        data = response["data"]
        items = [self._parse_email_address(item) for item in data["items"]]
        
        return PaginatedResponse(
            items=items,
            page=data["page"],
            limit=data["limit"],
            total=data["total"],
            total_pages=data["total_pages"],
            has_next=data["has_next"],
            has_previous=data["has_previous"]
        )
    
    def update(self, email_id: str, **updates: Any) -> EmailAddress:
        """Update an email address (for persistent emails)."""
        self._validate_email_id(email_id)
        
        update_options = cast(UpdateEmailAddressOptions, updates)
        self._validate_update_options(update_options)
        
        response = self.http_client.patch(f"/email-addresses/{email_id}", json=dict(update_options))
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to update email address"))
        
        return self._parse_email_address(response["data"])
    
    def delete(self, email_id: str) -> None:
        """Delete an email address."""
        self._validate_email_id(email_id)
        
        response = self.http_client.delete(f"/email-addresses/{email_id}")
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to delete email address"))
    
    def extend(self, email_id: str, additional_minutes: int) -> EmailAddress:
        """Extend expiration time for a temporary email address."""
        self._validate_email_id(email_id)
        
        if not isinstance(additional_minutes, int) or additional_minutes <= 0:
            raise ValidationError("Additional minutes must be a positive integer")
        
        response = self.http_client.post(
            f"/email-addresses/{email_id}/extend",
            json={"additional_minutes": additional_minutes}
        )
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to extend email address"))
        
        return self._parse_email_address(response["data"])


class AsyncEmailAddressService(BaseEmailAddressService):
    """Asynchronous service for managing email addresses."""
    
    def __init__(self, http_client: AsyncHTTPClient) -> None:
        self.http_client = http_client
    
    async def create(self, **options: Any) -> EmailAddress:
        """Create a new email address."""
        create_options = cast(CreateEmailAddressOptions, options)
        self._validate_create_options(create_options)
        
        response = await self.http_client.post("/email-addresses", json=dict(create_options))
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to create email address"))
        
        return self._parse_email_address(response["data"])
    
    async def get(self, email_id: str) -> EmailAddress:
        """Get an email address by ID."""
        self._validate_email_id(email_id)
        
        response = await self.http_client.get(f"/email-addresses/{email_id}")
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to get email address"))
        
        return self._parse_email_address(response["data"])
    
    async def list(self, **options: Any) -> PaginatedResponse[EmailAddress]:
        """List email addresses with pagination and filters."""
        list_options = cast(ListEmailAddressesOptions, options)
        query_string = self._build_list_params(list_options)
        endpoint = f"/email-addresses{query_string}"
        
        response = await self.http_client.get(endpoint)
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to list email addresses"))
        
        data = response["data"]
        items = [self._parse_email_address(item) for item in data["items"]]
        
        return PaginatedResponse(
            items=items,
            page=data["page"],
            limit=data["limit"],
            total=data["total"],
            total_pages=data["total_pages"],
            has_next=data["has_next"],
            has_previous=data["has_previous"]
        )
    
    async def update(self, email_id: str, **updates: Any) -> EmailAddress:
        """Update an email address (for persistent emails)."""
        self._validate_email_id(email_id)
        
        update_options = cast(UpdateEmailAddressOptions, updates)
        self._validate_update_options(update_options)
        
        response = await self.http_client.patch(f"/email-addresses/{email_id}", json=dict(update_options))
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to update email address"))
        
        return self._parse_email_address(response["data"])
    
    async def delete(self, email_id: str) -> None:
        """Delete an email address."""
        self._validate_email_id(email_id)
        
        response = await self.http_client.delete(f"/email-addresses/{email_id}")
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to delete email address"))
    
    async def extend(self, email_id: str, additional_minutes: int) -> EmailAddress:
        """Extend expiration time for a temporary email address."""
        self._validate_email_id(email_id)
        
        if not isinstance(additional_minutes, int) or additional_minutes <= 0:
            raise ValidationError("Additional minutes must be a positive integer")
        
        response = await self.http_client.post(
            f"/email-addresses/{email_id}/extend",
            json={"additional_minutes": additional_minutes}
        )
        
        if not response.get("success", True):
            raise EmailAddressError(response.get("error", "Failed to extend email address"))
        
        return self._parse_email_address(response["data"])
