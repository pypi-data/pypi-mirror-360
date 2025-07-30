from ..base_resource import BaseAwsResource

class S3Core(BaseAwsResource):
    """
    Core S3 class with main attributes and authentication logic.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Core attributes (to be filled in)
        self.bucket_name = None
        self.region_name = None
        self.storage_class = "STANDARD"
        self.public_access = False
        self.versioning_enabled = False
        self.encryption_enabled = True
        self.website_enabled = False
        self.cors_enabled = False
        self.lifecycle_rules = []
        self.bucket_tags = {}
        self._files_to_upload = []
        self._directories_to_upload = []
        self.bucket_exists = False
        self.bucket_url = None
        self.website_url = None
        self.bucket_arn = None
        self.s3_client = None
        self.s3_resource = None

    def _initialize_managers(self):
        """Initialize S3 managers"""
        # S3 doesn't need complex managers like EC2
        # Basic initialization is handled in __init__
        pass

    def _post_authentication_setup(self):
        """Setup after authentication"""
        # Initialize S3 client and resource after authentication
        if not self.s3_client:
            self.s3_client = self.get_s3_client(self.region_name)
            self.s3_resource = self.get_s3_resource(self.region_name)

    def create(self):
        """Create/update S3 bucket - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .s3_lifecycle import S3LifecycleMixin
        # Call the lifecycle mixin's create method
        return S3LifecycleMixin.create(self)

    def destroy(self):
        """Destroy S3 bucket - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .s3_lifecycle import S3LifecycleMixin
        # Call the lifecycle mixin's destroy method
        return S3LifecycleMixin.destroy(self)

    def preview(self):
        """Preview S3 bucket - delegates to lifecycle mixin"""
        # Import here to avoid circular imports
        from .s3_lifecycle import S3LifecycleMixin
        # Call the lifecycle mixin's preview method
        return S3LifecycleMixin.preview(self)
    
    def get_s3_client(self, region: str = None):
        """Get S3 client for this resource"""
        return self.get_client('s3', region)
    
    def get_s3_resource(self, region: str = None):
        """Get S3 resource for this resource"""
        import boto3
        from ..auth_service import AwsAuthenticationService
        session = AwsAuthenticationService.get_session()
        return session.resource('s3', region_name=region)
    
    def get_client(self, service_name: str, region: str = None):
        """Get AWS client for specified service"""
        from ..auth_service import AwsAuthenticationService
        return AwsAuthenticationService.get_client(service_name, region) 