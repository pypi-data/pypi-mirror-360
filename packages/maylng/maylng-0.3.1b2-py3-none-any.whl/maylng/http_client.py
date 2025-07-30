"""
HTTP client for making API requests to the Maylng API.

This module provides both synchronous and asynchronous HTTP clients
with automatic error handling, retry logic, and response parsing.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, Optional, Union, Type, TypeVar
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from .types import MaylConfig, APIResponse
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
)

T = TypeVar('T', bound=BaseModel)


class HTTPClient:
    """Synchronous HTTP client for the Maylng API."""
    
    def __init__(self, config: MaylConfig) -> None:
        self.config = self._prepare_config(config)
        self.client = self._create_client()
    
    def _prepare_config(self, config: MaylConfig) -> Dict[str, Any]:
        """Prepare and validate configuration."""
        return {
            "api_key": config["api_key"],
            "base_url": config.get("base_url", "http://api.mayl.ng:8080"),
            "timeout": config.get("timeout", 30.0),
            "max_retries": config.get("max_retries", 3),
            "retry_delay": config.get("retry_delay", 1.0),
        }
    
    def _create_client(self) -> httpx.Client:
        """Create HTTP client with proper configuration."""
        return httpx.Client(
            base_url=self.config["base_url"],
            timeout=self.config["timeout"],
            headers={
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json",
                "User-Agent": "maylng-python/0.2.1b0",
            }
        )
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return f"req_{int(time.time())}_{uuid.uuid4().hex[:9]}"
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and convert errors."""
        request_id = response.request.headers.get("X-Request-ID")
        
        if response.is_success:
            try:
                return response.json()
            except Exception:
                return {"data": response.text, "success": True}
        
        # Handle error responses
        try:
            error_data = response.json()
            message = error_data.get("error", response.text or f"HTTP {response.status_code}")
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
        
        if response.status_code == 401:
            raise AuthenticationError(message, request_id)
        elif response.status_code == 403:
            raise AuthorizationError(message, request_id)
        elif response.status_code == 404:
            raise NotFoundError("Resource", None, request_id)
        elif response.status_code == 400:
            raise ValidationError(message, None, request_id)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after else None
            raise RateLimitError(message, retry_after_int, request_id)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, request_id)
        else:
            raise ServerError(f"HTTP {response.status_code}: {message}", response.status_code, request_id)
    
    def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = endpoint if endpoint.startswith("http") else urljoin(self.config["base_url"], endpoint.lstrip("/"))
        
        # Add request ID
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["X-Request-ID"] = self._generate_request_id()
        
        last_exception = None
        
        for attempt in range(self.config["max_retries"] + 1):
            try:
                response = self.client.request(method, url, **kwargs)
                return self._handle_response(response)
            
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt == self.config["max_retries"]:
                    break
                time.sleep(self.config["retry_delay"] * (attempt + 1))
            
            except (AuthenticationError, AuthorizationError, ValidationError, NotFoundError):
                # Don't retry these errors
                raise
            
            except Exception as e:
                last_exception = e
                if attempt == self.config["max_retries"]:
                    break
                time.sleep(self.config["retry_delay"] * (attempt + 1))
        
        # If we get here, all retries failed
        if isinstance(last_exception, httpx.TimeoutException):
            raise TimeoutError("Request timeout")
        elif isinstance(last_exception, httpx.ConnectError):
            raise NetworkError(f"Connection error: {last_exception}")
        else:
            raise NetworkError(f"Network error: {last_exception}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request_with_retry("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request_with_retry("POST", endpoint, data=data, json=json)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self._make_request_with_retry("PUT", endpoint, data=data, json=json)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self._make_request_with_retry("PATCH", endpoint, data=data, json=json)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self._make_request_with_retry("DELETE", endpoint)
    
    def update_api_key(self, api_key: str) -> None:
        """Update the API key."""
        self.config["api_key"] = api_key
        self.client.headers["Authorization"] = f"Bearer {api_key}"
    
    def update_base_url(self, base_url: str) -> None:
        """Update the base URL."""
        self.config["base_url"] = base_url
        self.client.base_url = base_url
    
    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncHTTPClient:
    """Asynchronous HTTP client for the Maylng API."""
    
    def __init__(self, config: MaylConfig) -> None:
        self.config = self._prepare_config(config)
        self.client: Optional[httpx.AsyncClient] = None
    
    def _prepare_config(self, config: MaylConfig) -> Dict[str, Any]:
        """Prepare and validate configuration."""
        return {
            "api_key": config["api_key"],
            "base_url": config.get("base_url", "http://api.mayl.ng:8080"),
            "timeout": config.get("timeout", 30.0),
            "max_retries": config.get("max_retries", 3),
            "retry_delay": config.get("retry_delay", 1.0),
        }
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self.config["base_url"],
                timeout=self.config["timeout"],
                headers={
                    "Authorization": f"Bearer {self.config['api_key']}",
                    "Content-Type": "application/json",
                    "User-Agent": "maylng-python/0.2.1b0",
                }
            )
        return self.client
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return f"req_{int(time.time())}_{uuid.uuid4().hex[:9]}"
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and convert errors."""
        request_id = response.request.headers.get("X-Request-ID")
        
        if response.is_success:
            try:
                return response.json()
            except Exception:
                return {"data": response.text, "success": True}
        
        # Handle error responses
        try:
            error_data = response.json()
            message = error_data.get("error", response.text or f"HTTP {response.status_code}")
        except Exception:
            message = response.text or f"HTTP {response.status_code}"
        
        if response.status_code == 401:
            raise AuthenticationError(message, request_id)
        elif response.status_code == 403:
            raise AuthorizationError(message, request_id)
        elif response.status_code == 404:
            raise NotFoundError("Resource", None, request_id)
        elif response.status_code == 400:
            raise ValidationError(message, None, request_id)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after else None
            raise RateLimitError(message, retry_after_int, request_id)
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, request_id)
        else:
            raise ServerError(f"HTTP {response.status_code}: {message}", response.status_code, request_id)
    
    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        client = self._get_client()
        url = endpoint if endpoint.startswith("http") else urljoin(self.config["base_url"], endpoint.lstrip("/"))
        
        # Add request ID
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["X-Request-ID"] = self._generate_request_id()
        
        last_exception = None
        
        for attempt in range(self.config["max_retries"] + 1):
            try:
                response = await client.request(method, url, **kwargs)
                return self._handle_response(response)
            
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt == self.config["max_retries"]:
                    break
                await asyncio.sleep(self.config["retry_delay"] * (attempt + 1))
            
            except (AuthenticationError, AuthorizationError, ValidationError, NotFoundError):
                # Don't retry these errors
                raise
            
            except Exception as e:
                last_exception = e
                if attempt == self.config["max_retries"]:
                    break
                await asyncio.sleep(self.config["retry_delay"] * (attempt + 1))
        
        # If we get here, all retries failed
        if isinstance(last_exception, httpx.TimeoutException):
            raise TimeoutError("Request timeout")
        elif isinstance(last_exception, httpx.ConnectError):
            raise NetworkError(f"Connection error: {last_exception}")
        else:
            raise NetworkError(f"Network error: {last_exception}")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request_with_retry("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._make_request_with_retry("POST", endpoint, data=data, json=json)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request_with_retry("PUT", endpoint, data=data, json=json)
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return await self._make_request_with_retry("PATCH", endpoint, data=data, json=json)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request_with_retry("DELETE", endpoint)
    
    def update_api_key(self, api_key: str) -> None:
        """Update the API key."""
        self.config["api_key"] = api_key
        if self.client:
            self.client.headers["Authorization"] = f"Bearer {api_key}"
    
    def update_base_url(self, base_url: str) -> None:
        """Update the base URL."""
        self.config["base_url"] = base_url
        if self.client:
            self.client.base_url = base_url
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
