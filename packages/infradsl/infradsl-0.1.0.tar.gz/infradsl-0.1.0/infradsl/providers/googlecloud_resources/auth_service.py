import os
from typing import List
from ..googlecloud_managers.gcp_client import GcpClient


class GcpAuthenticationService:
    """Centralized authentication service for Google Cloud resources"""

    @staticmethod
    def get_credentials_paths() -> List[str]:
        """Get possible paths for oopscli.json credentials file"""
        return [
            "oopscli.json",  # Current directory
            os.path.join(os.getcwd(), "oopscli.json"),  # Current working directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "oopscli.json"),  # Project root
        ]

    @staticmethod
    def authenticate_client(gcp_client: GcpClient, silent: bool = False) -> bool:
        """Authenticate a GCP client with service account credentials"""
        possible_paths = GcpAuthenticationService.get_credentials_paths()

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    gcp_client.authenticate(credentials_path=path, silent=silent)
                    return True
                except Exception as e:
                    if not silent:
                        print(f"⚠️  Failed to authenticate with {path}: {str(e)}")
                    continue

        raise Exception("Could not find or authenticate with oopscli.json. Please ensure the file exists and contains valid Google Cloud service account credentials.")

    @staticmethod
    def authenticate_for_cloud_run(gcp_client: GcpClient, silent: bool = False) -> bool:
        """Authenticate specifically for Cloud Run services (may use different auth method)"""
        possible_paths = GcpAuthenticationService.get_credentials_paths()

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    gcp_client.authenticate_with_service_account_file(path)
                    return True
                except Exception as e:
                    if not silent:
                        print(f"⚠️  Failed to authenticate with {path}: {str(e)}")
                    continue

        raise Exception("Could not find or authenticate with oopscli.json. Please ensure the file exists and contains valid Google Cloud service account credentials.")
