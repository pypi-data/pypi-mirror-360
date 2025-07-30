import os
import json
from typing import Optional
from google.cloud import compute_v1
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account

class GcpClient:
    """Google Cloud Platform client for managing authentication and API access"""
    
    # Singleton authentication state - shared across all instances
    _shared_auth_state = {
        'credentials': None,
        'project_id': None,
        'is_authenticated': False,
        'auth_displayed': False  # Track if we've shown auth messages
    }

    def __init__(self):
        self.project_id = None
        self._credentials = None
        self.compute_client = None
        self.is_authenticated = False

    def authenticate(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None, silent: bool = False) -> None:
        """Authenticate with Google Cloud using service account credentials"""
        
        # Check if we already have shared authentication
        if self._shared_auth_state['is_authenticated']:
            # Use shared authentication state
            self._credentials = self._shared_auth_state['credentials']
            self.project_id = self._shared_auth_state['project_id']
            self.is_authenticated = True
            
            # Create compute client with shared credentials
            self.compute_client = compute_v1.InstancesClient(credentials=self._credentials)
            
            # Only show authentication success message once per session
            if not self._shared_auth_state['auth_displayed'] and not silent:
                print(f"✅ Authentication successful.")
                self._shared_auth_state['auth_displayed'] = True
            
            return

        try:
            # Try to get credentials from various sources
            if credentials_path and os.path.exists(credentials_path):
                # Use provided service account key file
                self._credentials = service_account.Credentials.from_service_account_file(credentials_path)
            elif os.path.exists("oopscli.json"):
                # Use default oopscli.json file
                self._credentials = service_account.Credentials.from_service_account_file("oopscli.json")
            else:
                # Try to use default credentials (Application Default Credentials)
                self._credentials, _ = default()

            # Get project ID
            if project_id:
                self.project_id = project_id
            elif credentials_path and os.path.exists(credentials_path):
                # Extract project ID from service account key
                with open(credentials_path, 'r') as f:
                    key_data = json.load(f)
                    self.project_id = key_data.get('project_id')
            elif os.path.exists("oopscli.json"):
                # Extract project ID from oopscli.json
                with open("oopscli.json", 'r') as f:
                    key_data = json.load(f)
                    self.project_id = key_data.get('project_id')
            else:
                # Try to get project ID from environment or default credentials
                self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
                if not self.project_id:
                    raise ValueError("Project ID not found. Please set GOOGLE_CLOUD_PROJECT environment variable or provide project_id parameter.")

            # Create compute client
            self.compute_client = compute_v1.InstancesClient(credentials=self._credentials)

            # Test authentication by making a simple API call (only once)
            if not self._shared_auth_state['is_authenticated']:
                request = compute_v1.ListInstancesRequest(project=self.project_id, zone="us-central1-a")
                self.compute_client.list(request=request)

            self.is_authenticated = True
            
            # Store in shared state
            self._shared_auth_state['credentials'] = self._credentials
            self._shared_auth_state['project_id'] = self.project_id
            self._shared_auth_state['is_authenticated'] = True
            
            # Show simple auth success message only once
            if not silent and not self._shared_auth_state['auth_displayed']:
                print(f"✅ Authentication successful.")
                self._shared_auth_state['auth_displayed'] = True

        except Exception as e:
            if not silent:
                print(f"❌ Authentication failed: {str(e)}")
            raise Exception(f"Failed to authenticate with Google Cloud: {str(e)}")

    def check_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.is_authenticated or self._shared_auth_state['is_authenticated']

    @property
    def client(self):
        """Get the compute client"""
        if not self.check_authenticated():
            raise ValueError("Not authenticated. Call authenticate() first.")
        return self.compute_client

    @property
    def project(self):
        """Get the project ID"""
        if not self.check_authenticated():
            raise ValueError("Not authenticated. Call authenticate() first.")
        return self.project_id or self._shared_auth_state['project_id']

    @property
    def credentials(self):
        """Get the credentials"""
        if not self.check_authenticated():
            raise ValueError("Not authenticated. Call authenticate() first.")
        return self._credentials or self._shared_auth_state['credentials']

    def authenticate_with_service_account_file(self, credentials_path: str) -> None:
        """Authenticate with Google Cloud using service account file (compatibility method)"""
        self.authenticate(credentials_path=credentials_path)
