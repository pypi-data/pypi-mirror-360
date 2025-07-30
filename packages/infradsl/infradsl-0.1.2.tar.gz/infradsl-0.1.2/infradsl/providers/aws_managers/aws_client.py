"""
AWS Client

AWS client for managing authentication and API access.
Provides centralized authentication and service client management.
"""

import os
from typing import Optional
from dotenv import load_dotenv

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    # Fallback classes for type checking
    class ClientError(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__("boto3 not available")
            self.response = {'Error': {'Code': 'ImportError', 'Message': 'boto3 not available'}}
    class NoCredentialsError(Exception):
        pass
    class ProfileNotFound(Exception):
        pass


class AwsClient:
    """AWS client for managing authentication and API access"""

    # Singleton authentication state - shared across all instances
    _shared_auth_state = {
        'session': None,
        'region': None,
        'profile': None,
        'is_authenticated': False,
        'auth_displayed': False,  # Track if we've shown auth messages
        'account_id': None,
        'user_arn': None
    }

    def __init__(self):
        self.session = None
        self.region = None
        self.is_authenticated = False

    def authenticate(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        silent: bool = False
    ) -> None:
        """
        Authenticate with AWS using various credential sources.
        Priority order:
        1. Explicit parameters
        2. .env file
        3. Environment variables
        4. AWS credentials file (~/.aws/credentials)
        5. IAM roles

        Args:
            access_key_id: AWS Access Key ID (optional)
            secret_access_key: AWS Secret Access Key (optional)
            region: AWS region (optional, defaults to us-east-1)
            profile: AWS profile name (optional)
            silent: Whether to suppress output messages
        """
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for AWS operations. Install with: pip install boto3")

        # Check if we already have shared authentication
        if self._shared_auth_state['is_authenticated']:
            self._handle_cached_auth(silent)
            return

        # Load .env file first
        self._load_env_file(silent)

        try:
            self._perform_authentication(access_key_id, secret_access_key, region, profile, silent)
        except (ProfileNotFound, NoCredentialsError, ClientError, Exception) as e:
            self._handle_auth_error(e, profile, silent)
            raise

    def _handle_cached_auth(self, silent: bool):
        """Handle cached authentication state"""
        if not self._shared_auth_state['auth_displayed'] and not silent:
            region = self._shared_auth_state['region']
            profile = self._shared_auth_state['profile']
            if profile:
                print(f"✅ Using cached AWS authentication (profile: {profile}, region: {region})")
            else:
                print(f"✅ Using cached AWS authentication (region: {region})")
            self._shared_auth_state['auth_displayed'] = True

        # Update instance state
        self.session = self._shared_auth_state['session']
        self.region = self._shared_auth_state['region']
        self.is_authenticated = True

    def _load_env_file(self, silent: bool):
        """Load environment variables from .env file"""
        try:
            # Look for .env file in current directory and parent directories
            env_paths = ['.env', '../.env', '../../.env']
            env_loaded = False

            for env_path in env_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    # Silent by default - only show if explicitly requested
                    env_loaded = True
                    break

            # Don't show missing .env message unless explicitly requested
            if not env_loaded and not silent:
                pass  # Keep it quiet like GCP

        except Exception as e:
            if not silent:
                print(f"⚠️  Warning: Could not load .env file: {str(e)}")

    def _perform_authentication(self, access_key_id: Optional[str], secret_access_key: Optional[str],
                              region: Optional[str], profile: Optional[str], silent: bool):
        """Perform the actual authentication process"""
        # Keep it quiet during authentication process - only show final result

        # Determine region - prioritize .env file
        target_region = (
            region or
            os.getenv('AWS_REGION') or
            os.getenv('AWS_DEFAULT_REGION') or
            'us-east-1'
        )
        session_kwargs = self._build_session_kwargs(access_key_id, secret_access_key, profile, target_region, silent)

        if not boto3:
            raise ImportError("boto3 is required for AWS operations")
        session = boto3.Session(**session_kwargs)
        self._test_and_store_auth(session, target_region, profile, silent)

    def _build_session_kwargs(self, access_key_id: Optional[str], secret_access_key: Optional[str],
                            profile: Optional[str], target_region: str, silent: bool) -> dict:
        """Build session kwargs for boto3.Session"""
        session_kwargs = {'region_name': target_region}

        # Priority 1: Explicit parameters
        if access_key_id and secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': access_key_id,
                'aws_secret_access_key': secret_access_key
            })
        # Priority 2: .env file credentials
        elif os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            session_kwargs.update({
                'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY')
            })
            # Add session token if available (for temporary credentials)
            if os.getenv('AWS_SESSION_TOKEN'):
                session_kwargs['aws_session_token'] = os.getenv('AWS_SESSION_TOKEN')
        # Priority 3: AWS profile (from parameter or .env)
        elif profile or os.getenv('AWS_PROFILE'):
            profile_name = profile or os.getenv('AWS_PROFILE')
            session_kwargs['profile_name'] = profile_name
        # Priority 4: Default credential chain
        else:
            pass  # Use default AWS credential chain silently

        return session_kwargs

    def _test_and_store_auth(self, session, target_region: str, profile: Optional[str], silent: bool):
        """Test authentication and store session"""
        account_id = 'unknown'
        user_arn = 'unknown'

        if not self._shared_auth_state['is_authenticated']:
            # Test with STS to get caller identity (silently)
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            account_id = identity.get('Account', 'unknown')
            user_arn = identity.get('Arn', 'unknown')

            # Show simple success message like GCP (only once)
            if not silent and not self._shared_auth_state['auth_displayed']:
                print("✅ Authentication successful.")

        # Store in shared state
        self._shared_auth_state.update({
            'session': session,
            'region': target_region,
            'profile': profile,
            'is_authenticated': True,
            'account_id': account_id,
            'user_arn': user_arn
        })

        # Update instance state
        self.session = session
        self.region = target_region
        self.is_authenticated = True

        if not silent and not self._shared_auth_state['auth_displayed']:
            self._shared_auth_state['auth_displayed'] = True

    def _handle_auth_error(self, error: Exception, profile: Optional[str], silent: bool):
        """Handle authentication errors"""
        if isinstance(error, ProfileNotFound):
            if not silent:
                print(f"❌ AWS profile '{profile}' not found")
                print(f"💡 Available profiles: {self._get_available_profiles()}")
        elif isinstance(error, NoCredentialsError):
            if not silent:
                print("❌ No AWS credentials found")
                print("💡 To fix authentication:")
                print("   1. Create a .env file with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
                print("   2. Run: aws configure")
                print("   3. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
                print("   4. Use IAM roles (recommended for EC2/Lambda)")
                print("   5. Configure ~/.aws/credentials file")
        elif isinstance(error, ClientError):
            error_code = getattr(error, 'response', {}).get('Error', {}).get('Code', 'Unknown')
            if not silent:
                print(f"❌ AWS authentication failed: {error_code}")
                if error_code == 'InvalidUserID.NotFound':
                    print("💡 Check your AWS Access Key ID")
                elif error_code == 'SignatureDoesNotMatch':
                    print("💡 Check your AWS Secret Access Key")
                else:
                    print("💡 Check your AWS credentials and permissions")
        else:
            if not silent:
                print(f"❌ AWS authentication failed: {str(error)}")

    def get_session(self):
        """Get the authenticated AWS session"""
        if not self.is_authenticated:
            # Try to use shared state
            if self._shared_auth_state['is_authenticated']:
                self.session = self._shared_auth_state['session']
                self.region = self._shared_auth_state['region']
                self.is_authenticated = True
            else:
                # Try to authenticate with defaults
                self.authenticate(silent=True)

        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for AWS operations")

        if not self.is_authenticated or not self.session:
            raise Exception("Not authenticated with AWS. Call authenticate() first.")

        return self.session

    def get_region(self) -> str:
        """Get the current AWS region"""
        if not self.is_authenticated:
            if self._shared_auth_state['is_authenticated']:
                return self._shared_auth_state['region'] or 'us-east-1'
            else:
                self.authenticate(silent=True)
        return self.region or 'us-east-1'

    def get_client(self, service_name: str, region: Optional[str] = None):
        """
        Get an AWS service client.

        Args:
            service_name: Name of the AWS service (e.g., 'ec2', 's3', 'rds')
            region: Optional region override

        Returns:
            AWS service client
        """
        session = self.get_session()
        client_region = region or self.get_region()
        if not session:
            raise Exception("No authenticated session available")
        return session.client(service_name, region_name=client_region)

    def get_resource(self, service_name: str, region: Optional[str] = None):
        """
        Get an AWS service resource.

        Args:
            service_name: Name of the AWS service (e.g., 'ec2', 's3', 'rds')
            region: Optional region override

        Returns:
            AWS service resource
        """
        session = self.get_session()
        resource_region = region or self.get_region()
        if not session:
            raise Exception("No authenticated session available")
        return session.resource(service_name, region_name=resource_region)

    def get_account_id(self) -> str:
        """Get the current AWS account ID"""
        if not self.is_authenticated:
            self.authenticate(silent=True)
        return self._shared_auth_state.get('account_id', 'unknown')

    def get_user_arn(self) -> str:
        """Get the current user/role ARN"""
        if not self.is_authenticated:
            self.authenticate(silent=True)
        return self._shared_auth_state.get('user_arn', 'unknown')

    def _get_available_profiles(self) -> str:
        """Get list of available AWS profiles"""
        try:
            if not boto3:
                return 'boto3 not available'
            session = boto3.Session()
            profiles = session.available_profiles
            return ', '.join(profiles) if profiles else 'None found'
        except Exception:
            return 'Unable to list profiles'

    @classmethod
    def reset_authentication(cls):
        """Reset authentication state (useful for testing)"""
        cls._shared_auth_state = {
            'session': None,
            'region': None,
            'profile': None,
            'is_authenticated': False,
            'auth_displayed': False,
            'account_id': None,
            'user_arn': None
        }
