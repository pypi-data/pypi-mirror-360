"""
Firebase Configuration for InfraDSL Registry

This module provides Firebase configuration and setup for the InfraDSL CLI.
"""

import os
from typing import Dict, Any


# Load environment variables from registry/.env file
def load_env_file():
    """Load environment variables from registry/.env file"""
    from pathlib import Path
    
    # Look for .env file in registry directory (relative to this file)
    # Current file: infradsl/infradsl/cli/firebase_config.py
    # Target: registry/.env (at same level as infradsl/)
    registry_env_file = Path(__file__).parent.parent.parent.parent / 'registry' / '.env'
    
    if registry_env_file.exists():
        with open(registry_env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Load environment variables at import time
load_env_file()

# Firebase configuration - use environment variables with fallbacks
def get_firebase_config():
    """Get Firebase configuration from environment variables"""
    return {
        "apiKey": os.getenv('VITE_FIREBASE_API_KEY', 'AIzaSyBxRo_SuIf3gX7PSHYdSXVXt3rjEOGBHiA'),
        "authDomain": os.getenv('VITE_FIREBASE_AUTH_DOMAIN', 'infradsl.firebaseapp.com'),
        "projectId": os.getenv('VITE_FIREBASE_PROJECT_ID', 'infradsl'),
        "storageBucket": os.getenv('VITE_FIREBASE_STORAGE_BUCKET', 'infradsl.firebasestorage.app'),
        "messagingSenderId": os.getenv('VITE_FIREBASE_MESSAGING_SENDER_ID', '123456789000'),
        "appId": os.getenv('VITE_FIREBASE_APP_ID', '1:123456789000:web:abcdefghijklmnop123456')
    }

# For backward compatibility
FIREBASE_CONFIG = get_firebase_config()


def get_firebase_api_key() -> str:
    """Get Firebase API key from environment or config"""
    config = get_firebase_config()
    return config["apiKey"]


# get_firebase_config is already defined above


def get_registry_url() -> str:
    """Get registry URL"""
    return os.getenv('INFRADSL_REGISTRY_URL', 'https://registry.infradsl.dev')


def get_project_id() -> str:
    """Get Firebase project ID"""
    return os.getenv('FIREBASE_PROJECT_ID', 'infradsl')