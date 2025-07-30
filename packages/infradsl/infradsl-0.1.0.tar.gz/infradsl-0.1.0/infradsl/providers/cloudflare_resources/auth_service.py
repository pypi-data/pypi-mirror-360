"""
Cloudflare Authentication Service

Handles authentication and API client setup for Cloudflare resources.
Follows the same pattern as AWS authentication but for Cloudflare API.
"""

import os
import sys
from typing import Optional, Dict, Any
import requests
from dataclasses import dataclass


@dataclass
class CloudflareCredentials:
    """Cloudflare API credentials"""
    api_token: Optional[str] = None
    api_key: Optional[str] = None
    email: Optional[str] = None
    zone_id: Optional[str] = None


class CloudflareAuthenticationService:
    """Handles Cloudflare API authentication"""

    _authenticated = False
    _credentials: Optional[CloudflareCredentials] = None
    _api_client = None

    @classmethod
    def authenticate(cls, silent: bool = False) -> bool:
        """
        Authenticate with Cloudflare API

        Args:
            silent: If True, suppress output messages

        Returns:
            bool: True if authentication successful
        """
        if cls._authenticated:
            return True

        if not silent:
            print("🔐 Authenticating with Cloudflare...")

        try:
            cls._credentials = cls._load_credentials()
            cls._validate_credentials()
            cls._setup_api_client()
            cls._authenticated = True

            if not silent:
                print("✅ Cloudflare authentication successful!")

            return True

        except Exception as e:
            if not silent:
                print(f"❌ Cloudflare authentication failed: {str(e)}")
            return False

    @classmethod
    def _load_credentials(cls) -> CloudflareCredentials:
        """Load Cloudflare credentials from environment variables"""
        return CloudflareCredentials(
            api_token=os.getenv('CLOUDFLARE_API_TOKEN'),
            api_key=os.getenv('CLOUDFLARE_API_KEY'),
            email=os.getenv('CLOUDFLARE_EMAIL'),
            zone_id=os.getenv('CLOUDFLARE_ZONE_ID')
        )

    @classmethod
    def _validate_credentials(cls):
        """Validate that we have the required credentials"""
        if not cls._credentials:
            raise ValueError("No Cloudflare credentials loaded")

        # We need either API token or API key + email
        if not cls._credentials.api_token and not (cls._credentials.api_key and cls._credentials.email):
            raise ValueError(
                "Missing Cloudflare credentials. Set either:\n"
                "- CLOUDFLARE_API_TOKEN (recommended)\n"
                "- CLOUDFLARE_API_KEY and CLOUDFLARE_EMAIL"
            )

    @classmethod
    def _setup_api_client(cls):
        """Setup the Cloudflare API client"""
        # Test the credentials with a simple API call
        headers = cls.get_headers()
        response = requests.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers=headers,
            timeout=10
        )

        if not response.ok:
            raise ValueError(f"Invalid Cloudflare credentials: {response.text}")

        cls._api_client = True  # Simple flag for now

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get headers for Cloudflare API requests"""
        if not cls._authenticated:
            cls.authenticate()

        if cls._credentials.api_token:
            return {
                "Authorization": f"Bearer {cls._credentials.api_token}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "X-Auth-Key": cls._credentials.api_key,
                "X-Auth-Email": cls._credentials.email,
                "Content-Type": "application/json"
            }

    @classmethod
    def get_credentials(cls) -> CloudflareCredentials:
        """Get the current credentials"""
        if not cls._authenticated:
            cls.authenticate()
        return cls._credentials

    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if we're currently authenticated"""
        return cls._authenticated

    @classmethod
    def reset(cls):
        """Reset authentication state (useful for testing)"""
        cls._authenticated = False
        cls._credentials = None
        cls._api_client = None

    @classmethod
    def get_api_base_url(cls) -> str:
        """Get the Cloudflare API base URL"""
        return "https://api.cloudflare.com/client/v4"

    @classmethod
    def make_request(cls, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated request to Cloudflare API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response: The API response
        """
        if not cls._authenticated:
            cls.authenticate()

        url = f"{cls.get_api_base_url()}/{endpoint.lstrip('/')}"
        headers = cls.get_headers()

        # Merge headers if provided in kwargs
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        kwargs['headers'] = headers

        return requests.request(method, url, **kwargs)
