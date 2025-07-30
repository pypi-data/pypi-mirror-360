"""
DigitalOcean Spaces & CDN Resource

Provides Rails-like interface for creating and managing DigitalOcean Spaces 
(object storage) with CDN capabilities.
"""

from typing import Dict, Any, List, Optional
from .base_resource import BaseDigitalOceanResource


class SpacesCDN(BaseDigitalOceanResource):
    """DigitalOcean Spaces with CDN integration"""

    def __init__(self, name: str):
        super().__init__(name)
        self.config = {
            "name": name,
            "region": "nyc3",  # Default region
            "acl": "private",  # Default to private
            "cors_rules": [],
            "lifecycle_rules": [],
            "versioning_enabled": False,
            "cdn_enabled": False,
            "cdn_domain": None,
            "cdn_certificate_id": None,
            "cdn_ttl": 3600,  # 1 hour default TTL
            "tags": []
        }

    def _initialize_managers(self):
        """Initialize Spaces-specific managers"""
        from ..digitalocean_managers.spaces_manager import SpacesManager
        self.spaces_manager = None  # Will be initialized after authentication

    def _post_authentication_setup(self):
        """Setup managers after authentication"""
        from ..digitalocean_managers.spaces_manager import SpacesManager
        self.spaces_manager = SpacesManager(self.do_client)

    # Region and basic configuration
    def region(self, region: str) -> 'SpacesCDN':
        """Set the region (e.g., 'nyc3', 'ams3', 'sgp1')"""
        self.config["region"] = region
        return self

    def public(self) -> 'SpacesCDN':
        """Make the Space publicly readable"""
        self.config["acl"] = "public-read"
        return self

    def private(self) -> 'SpacesCDN':
        """Make the Space private (default)"""
        self.config["acl"] = "private"
        return self

    def versioning(self, enabled: bool = True) -> 'SpacesCDN':
        """Enable or disable versioning"""
        self.config["versioning_enabled"] = enabled
        return self

    def tags(self, tags: List[str]) -> 'SpacesCDN':
        """Add tags to the Space"""
        self.config["tags"] = tags
        return self

    # CDN configuration
    def cdn(self, enabled: bool = True, domain: Optional[str] = None, ttl: int = 3600) -> 'SpacesCDN':
        """Enable CDN with optional custom domain"""
        self.config["cdn_enabled"] = enabled
        if domain:
            self.config["cdn_domain"] = domain
        self.config["cdn_ttl"] = ttl
        return self

    def cdn_certificate(self, certificate_id: str) -> 'SpacesCDN':
        """Use custom SSL certificate for CDN"""
        self.config["cdn_certificate_id"] = certificate_id
        return self

    # CORS configuration
    def cors_rule(self, allowed_origins: List[str], allowed_methods: List[str], 
                  allowed_headers: Optional[List[str]] = None, max_age_seconds: int = 3000) -> 'SpacesCDN':
        """Add CORS rule"""
        rule = {
            "allowed_origins": allowed_origins,
            "allowed_methods": allowed_methods,
            "allowed_headers": allowed_headers or ["*"],
            "max_age_seconds": max_age_seconds
        }
        self.config["cors_rules"].append(rule)
        return self

    # Lifecycle configuration
    def lifecycle_rule(self, rule_id: str, prefix: str = "", 
                      expiration_days: Optional[int] = None,
                      noncurrent_expiration_days: Optional[int] = None,
                      abort_incomplete_uploads_days: Optional[int] = None) -> 'SpacesCDN':
        """Add lifecycle rule for automatic object management"""
        rule = {
            "id": rule_id,
            "prefix": prefix,
            "status": "Enabled"
        }
        
        if expiration_days:
            rule["expiration"] = {"days": expiration_days}
        
        if noncurrent_expiration_days:
            rule["noncurrent_version_expiration"] = {"noncurrent_days": noncurrent_expiration_days}
        
        if abort_incomplete_uploads_days:
            rule["abort_incomplete_multipart_upload"] = {"days_after_initiation": abort_incomplete_uploads_days}
        
        self.config["lifecycle_rules"].append(rule)
        return self

    # Rails-like convenience methods
    def website(self, index_document: str = "index.html", error_document: str = "error.html") -> 'SpacesCDN':
        """Configure for static website hosting with CDN"""
        return self.public().cdn(enabled=True).cors_rule(
            allowed_origins=["*"],
            allowed_methods=["GET", "HEAD"],
            allowed_headers=["*"]
        )

    def media_storage(self) -> 'SpacesCDN':
        """Configure for media file storage with CDN"""
        return self.public().cdn(enabled=True, ttl=86400).cors_rule(
            allowed_origins=["*"],
            allowed_methods=["GET", "HEAD", "POST"],
            allowed_headers=["*"]
        ).lifecycle_rule(
            rule_id="cleanup-uploads",
            abort_incomplete_uploads_days=7
        )

    def backup_storage(self) -> 'SpacesCDN':
        """Configure for backup storage (private, no CDN)"""
        return self.private().versioning(True).lifecycle_rule(
            rule_id="backup-retention",
            expiration_days=90,
            noncurrent_expiration_days=30
        )

    def development(self) -> 'SpacesCDN':
        """Configure for development environment"""
        return self.private().cdn(enabled=False)

    def production(self) -> 'SpacesCDN':
        """Configure for production environment"""
        return self.public().cdn(enabled=True, ttl=3600).versioning(True)

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        self._ensure_authenticated()
        return self.spaces_manager.preview_spaces_cdn(self.config)

    def create(self) -> Dict[str, Any]:
        """Create the Spaces bucket with CDN configuration"""
        self._ensure_authenticated()
        
        self._print_resource_header("Spaces CDN", "Creating")
        
        # Print configuration summary
        print(f"🪣 Space Name: {self.config['name']}")
        print(f"📍 Region: {self.config['region']}")
        print(f"🔒 Access: {self.config['acl']}")
        print(f"📦 Versioning: {'Enabled' if self.config['versioning_enabled'] else 'Disabled'}")
        print(f"🌐 CDN: {'Enabled' if self.config['cdn_enabled'] else 'Disabled'}")
        
        if self.config["cdn_enabled"]:
            if self.config["cdn_domain"]:
                print(f"🌍 Custom Domain: {self.config['cdn_domain']}")
            print(f"⏱️  TTL: {self.config['cdn_ttl']} seconds")
        
        if self.config["cors_rules"]:
            print(f"🔄 CORS Rules: {len(self.config['cors_rules'])}")
        
        if self.config["lifecycle_rules"]:
            print(f"♻️  Lifecycle Rules: {len(self.config['lifecycle_rules'])}")
        
        result = self.spaces_manager.create_spaces_cdn(self.config)
        
        self._print_resource_footer("create Spaces CDN")
        return result

    def destroy(self) -> Dict[str, Any]:
        """Destroy the Spaces bucket and CDN configuration"""
        self._ensure_authenticated()
        
        print(f"\n🗑️  Destroying Spaces CDN: {self.name}")
        result = self.spaces_manager.destroy_spaces_cdn(self.name)
        
        if result.get("success"):
            print(f"✅ Spaces CDN '{self.name}' destroyed successfully")
        else:
            print(f"❌ Failed to destroy Spaces CDN: {result.get('error', 'Unknown error')}")
        
        return result

    # File upload utilities
    def upload_file(self, file_path: str, key: Optional[str] = None, 
                   content_type: Optional[str] = None, public: bool = None) -> Dict[str, Any]:
        """Upload file to the Space"""
        self._ensure_authenticated()
        return self.spaces_manager.upload_file(
            space_name=self.name,
            file_path=file_path,
            key=key,
            content_type=content_type,
            public=public if public is not None else (self.config["acl"] == "public-read")
        )

    def upload_directory(self, directory_path: str, prefix: str = "", 
                        public: bool = None) -> Dict[str, Any]:
        """Upload entire directory to the Space"""
        self._ensure_authenticated()
        return self.spaces_manager.upload_directory(
            space_name=self.name,
            directory_path=directory_path,
            prefix=prefix,
            public=public if public is not None else (self.config["acl"] == "public-read")
        )