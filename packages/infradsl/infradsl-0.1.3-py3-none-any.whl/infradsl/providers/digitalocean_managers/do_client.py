from pydo import Client
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


def find_project_root_env() -> Optional[str]:
    """
    Search for .env file starting from current directory and walking up the tree.
    Returns the path to the .env file if found, None otherwise.
    """
    current_path = Path.cwd()
    
    # Walk up the directory tree
    for path in [current_path] + list(current_path.parents):
        env_file = path / '.env'
        if env_file.exists():
            return str(env_file)
    
    return None


def load_project_env() -> bool:
    """
    Load environment variables from project root .env file.
    Returns True if .env file was found and loaded, False otherwise.
    """
    env_file = find_project_root_env()
    if env_file:
        load_dotenv(env_file)
        return True
    return False


class DoClient:
    """Wrapper around DigitalOcean API client for centralized authentication and access"""
    
    def __init__(self, token: Optional[str] = None):
        self._token = token
        self._client = None
        
        # Auto-load environment if no token provided
        if not token:
            load_project_env()
            # Try to get token from environment after loading .env
            env_token = os.getenv("DO_TOKEN")
            if env_token:
                self._token = env_token
                self._client = Client(token=env_token)
        else:
            self._client = Client(token=token)
    
    def authenticate(self, token: Optional[str] = None) -> 'DoClient':
        """
        Set the DigitalOcean API token.
        If no token provided, tries to load from project .env file.
        """
        if not token:
            # Try to load from project root .env
            load_project_env()
            token = os.getenv("DO_TOKEN")
            
        if not token:
            raise ValueError(
                "No DigitalOcean token found. Either:\n"
                "1. Pass token directly: .authenticate('your-token')\n"
                "2. Set DO_TOKEN environment variable\n"
                "3. Create .env file in project root with DO_TOKEN=your-token"
            )
            
        self._token = token
        self._client = Client(token=token)
        return self
    
    @property
    def client(self) -> Client:
        """Get the DigitalOcean API client"""
        if not self._client:
            # Try auto-authentication first
            try:
                self.authenticate()
            except ValueError:
                raise ValueError("Authentication token not set. Use .authenticate() first.")
        return self._client
    
    @property
    def token(self) -> str:
        """Get the DigitalOcean API token"""
        if not self._token:
            # Try auto-authentication first
            try:
                self.authenticate()
            except ValueError:
                raise ValueError("Authentication token not set. Use .authenticate() first.")
        return self._token
    
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated"""
        return self._client is not None and self._token is not None 