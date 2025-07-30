from infradsl.providers.digitalocean_managers.do_client import DoClient
from typing import Optional

class DigitalOceanAuthenticationService:
    """Centralized authentication service for DigitalOcean resources"""

    _shared_auth_state = {
        'client': None,
        'is_authenticated': False,
        'auth_displayed': False
    }

    @staticmethod
    def authenticate(token: Optional[str] = None, silent: bool = False) -> bool:
        if DigitalOceanAuthenticationService._shared_auth_state['is_authenticated']:
            if not DigitalOceanAuthenticationService._shared_auth_state['auth_displayed'] and not silent:
                print("✅ Using cached DigitalOcean authentication")
                DigitalOceanAuthenticationService._shared_auth_state['auth_displayed'] = True
            return True

        try:
            client = DoClient(token=token)
            if client.is_authenticated():
                DigitalOceanAuthenticationService._shared_auth_state['client'] = client
                DigitalOceanAuthenticationService._shared_auth_state['is_authenticated'] = True
                if not silent:
                    print("✅ Authenticated with DigitalOcean")
                    DigitalOceanAuthenticationService._shared_auth_state['auth_displayed'] = True
                return True
            return False
        except Exception as e:
            if not silent:
                print(f"❌ DigitalOcean authentication failed: {e}")
            return False

    @staticmethod
    def get_client() -> DoClient:
        if not DigitalOceanAuthenticationService._shared_auth_state['is_authenticated']:
            # Try to authenticate with defaults
            DigitalOceanAuthenticationService.authenticate(silent=True)

        if not DigitalOceanAuthenticationService._shared_auth_state['is_authenticated']:
            raise Exception("Not authenticated with DigitalOcean. Call .authenticate() or set DO_TOKEN.")

        return DigitalOceanAuthenticationService._shared_auth_state['client']
