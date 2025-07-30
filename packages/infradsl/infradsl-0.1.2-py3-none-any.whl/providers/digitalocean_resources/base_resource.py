from abc import ABC, abstractmethod
from typing import Dict, Any
from .auth_service import DigitalOceanAuthenticationService

class BaseDigitalOceanResource(ABC):
    _auth_call_count = 0

    def __init__(self, name: str):
        self.name = name
        self._auto_authenticated = False
        self._initialize_managers()

    @abstractmethod
    def _initialize_managers(self):
        """Initialize resource-specific managers"""
        pass

    def _ensure_authenticated(self):
        """Ensure the DigitalOcean client is authenticated"""
        if not self._auto_authenticated:
            BaseDigitalOceanResource._auth_call_count += 1
            silent = BaseDigitalOceanResource._auth_call_count > 1
            
            DigitalOceanAuthenticationService.authenticate(silent=silent)
            self.do_client = DigitalOceanAuthenticationService.get_client()
            self._post_authentication_setup()
            self._auto_authenticated = True

    @abstractmethod
    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        pass

    @abstractmethod
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        pass

    @abstractmethod
    def create(self) -> Dict[str, Any]:
        """Create the resource"""
        pass

    @abstractmethod
    def destroy(self) -> Dict[str, Any]:
        """Destroy the resource"""
        pass
