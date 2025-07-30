"""
Firebase Storage Configuration Mixin

Configuration methods for Firebase Storage.
Provides Rails-like method chaining for fluent storage configuration.
"""

from typing import Dict, Any, List, Optional, Union


class FirebaseStorageConfigurationMixin:
    """
    Mixin for Firebase Storage configuration methods.
    
    This mixin provides:
    - Rails-like method chaining for fluent storage configuration
    - Common storage patterns (media, documents, backups, user uploads)
    - Security configuration (rules, public access, authentication)
    - Performance configuration (CDN, caching, compression)
    - Lifecycle management (retention, archiving, deletion)
    - Upload configuration (file types, size limits, transformations)
    - Monitoring and notifications
    """
    
    def project(self, firebase_project_id: str):
        """Set Firebase project ID"""
        self.firebase_project_id = firebase_project_id
        return self
        
    def bucket_name(self, bucket_name: str):
        """Set custom bucket name"""
        self.bucket_name = bucket_name
        return self
        
    def location(self, location: str):
        """Set storage location"""
        if not self._is_valid_location(location):
            raise ValueError(f"Invalid location: {location}")
        self.location = location
        return self
        
    def storage_class(self, storage_class: str):
        """Set storage class (STANDARD, NEARLINE, COLDLINE, ARCHIVE)"""
        if not self._is_valid_storage_class(storage_class):
            raise ValueError(f"Invalid storage class: {storage_class}")
        self.storage_class = storage_class
        return self
        
    def description(self, description: str):
        """Set storage description"""
        self.storage_description = description
        return self
    
    # Access Configuration Methods
    def public_access(self, enabled: bool = True):
        """Enable public access to files"""
        self.public_access = enabled
        return self
        
    def public_read(self, enabled: bool = True):
        """Enable public read access"""
        self.public_read = enabled
        return self
        
    def authenticated_read(self, enabled: bool = True):
        """Enable authenticated read access"""
        self.authenticated_read = enabled
        return self
        
    def uniform_bucket_level_access(self, enabled: bool = True):
        """Enable uniform bucket-level access"""
        self.uniform_bucket_level_access = enabled
        return self
    
    # Security Configuration Methods
    def security_rules(self, rules_file: Optional[str] = None, rules_content: Optional[str] = None):
        """Configure Firebase Security Rules"""
        if rules_file:
            self.security_rules_file = rules_file
        if rules_content:
            self.security_rules_content = rules_content
        self.default_security_rules = False
        return self
        
    def default_security_rules(self):
        """Use default security rules (authenticated users only)"""
        self.default_security_rules = True
        self.security_rules_file = None
        self.security_rules_content = None
        return self
        
    def strict_security_rules(self):
        """Apply strict security rules"""
        strict_rules = """
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Only authenticated users can read/write their own files
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Public read-only access to public folder
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // No access to other paths
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
"""
        return self.security_rules(rules_content=strict_rules)
        
    def permissive_security_rules(self):
        """Apply permissive security rules (authenticated users can read/write anything)"""
        permissive_rules = """
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
"""
        return self.security_rules(rules_content=permissive_rules)
    
    # CORS Configuration Methods
    def cors(self, enabled: bool = True, origins: List[str] = None, methods: List[str] = None, headers: List[str] = None, max_age: int = 3600):
        """Configure CORS for the bucket"""
        self.cors_enabled = enabled
        if enabled:
            self.cors_origins = origins or ["*"]
            self.cors_methods = methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            self.cors_headers = headers or ["Content-Type", "Authorization"]
            self.cors_max_age = max_age
        return self
        
    def cors_allow_all(self):
        """Allow CORS from all origins"""
        return self.cors(enabled=True, origins=["*"])
        
    def cors_restrict_origins(self, origins: List[str]):
        """Restrict CORS to specific origins"""
        return self.cors(enabled=True, origins=origins)
        
    def cors_disable(self):
        """Disable CORS"""
        self.cors_enabled = False
        return self
    
    # Lifecycle Configuration Methods
    def lifecycle_rule(self, action: str, condition: Dict[str, Any]):
        """Add lifecycle rule"""
        self.lifecycle_rules.append({
            "action": action,
            "condition": condition
        })
        return self
        
    def delete_after_days(self, days: int):
        """Delete files after specified days"""
        return self.lifecycle_rule("Delete", {"age": days})
        
    def archive_after_days(self, days: int):
        """Archive files to ARCHIVE storage class after specified days"""
        return self.lifecycle_rule("SetStorageClass", {
            "age": days,
            "storageClass": "ARCHIVE"
        })
        
    def coldline_after_days(self, days: int):
        """Move files to COLDLINE storage class after specified days"""
        return self.lifecycle_rule("SetStorageClass", {
            "age": days,
            "storageClass": "COLDLINE"
        })
        
    def nearline_after_days(self, days: int):
        """Move files to NEARLINE storage class after specified days"""
        return self.lifecycle_rule("SetStorageClass", {
            "age": days,
            "storageClass": "NEARLINE"
        })
        
    def retention_policy(self, retention_period_seconds: int):
        """Set retention policy (files cannot be deleted before this period)"""
        self.retention_policy = {
            "retentionPeriod": str(retention_period_seconds)
        }
        return self
        
    def versioning(self, enabled: bool = True):
        """Enable object versioning"""
        self.versioning_enabled = enabled
        return self
    
    # Performance Configuration Methods
    def cdn(self, enabled: bool = True):
        """Enable CDN for faster global access"""
        self.cdn_enabled = enabled
        return self
        
    def cache_control(self, pattern: str, max_age: int):
        """Set cache control for file patterns"""
        self.cache_control[pattern] = {
            "max_age": max_age,
            "cache_control": f"max-age={max_age}"
        }
        return self
        
    def cache_images(self, max_age: int = 86400):
        """Set cache control for images (default 1 day)"""
        return self.cache_control("**/*.@(jpg|jpeg|png|gif|webp|svg)", max_age)
        
    def cache_static_assets(self, max_age: int = 31536000):
        """Set cache control for static assets (default 1 year)"""
        return self.cache_control("**/*.@(css|js|woff|woff2|ttf|otf)", max_age)
        
    def cache_videos(self, max_age: int = 604800):
        """Set cache control for videos (default 1 week)"""
        return self.cache_control("**/*.@(mp4|webm|avi|mov)", max_age)
        
    def compression(self, enabled: bool = True):
        """Enable compression for file uploads"""
        self.compression_enabled = enabled
        return self
    
    # Upload Configuration Methods
    def max_upload_size(self, size_bytes: int):
        """Set maximum upload size in bytes"""
        self.max_upload_size = size_bytes
        return self
        
    def max_upload_size_mb(self, size_mb: int):
        """Set maximum upload size in MB"""
        return self.max_upload_size(size_mb * 1024 * 1024)
        
    def allowed_file_types(self, file_types: List[str]):
        """Set allowed file types (e.g., ['image/*', 'video/*'])"""
        self.allowed_file_types = file_types
        return self
        
    def allow_images(self):
        """Allow image file uploads"""
        if "image/*" not in self.allowed_file_types:
            self.allowed_file_types.append("image/*")
        return self
        
    def allow_videos(self):
        """Allow video file uploads"""
        if "video/*" not in self.allowed_file_types:
            self.allowed_file_types.append("video/*")
        return self
        
    def allow_documents(self):
        """Allow document file uploads"""
        document_types = ["application/pdf", "application/msword", 
                         "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        for doc_type in document_types:
            if doc_type not in self.allowed_file_types:
                self.allowed_file_types.append(doc_type)
        return self
    
    # Image Processing Methods
    def image_transformations(self, transformations: Dict[str, Any]):
        """Configure image transformations"""
        self.image_transformations = transformations
        return self
        
    def thumbnail_generation(self, enabled: bool = True, sizes: List[int] = None):
        """Enable automatic thumbnail generation"""
        self.thumbnail_generation = enabled
        if enabled and sizes:
            self.image_transformations["thumbnails"] = {
                "sizes": sizes or [150, 300, 500]
            }
        return self
        
    def image_optimization(self, enabled: bool = True):
        """Enable automatic image optimization"""
        if enabled:
            self.image_transformations["optimization"] = {
                "quality": 85,
                "format": "auto"
            }
        return self
    
    # Monitoring Configuration Methods
    def logging(self, enabled: bool = True):
        """Enable logging for storage operations"""
        self.logging_enabled = enabled
        return self
        
    def monitoring(self, enabled: bool = True):
        """Enable monitoring for storage usage"""
        self.monitoring_enabled = enabled
        return self
        
    def notifications(self, topic_name: str, event_types: List[str] = None):
        """Add Pub/Sub notification for storage events"""
        self.notifications.append({
            "topic": topic_name,
            "event_types": event_types or ["OBJECT_FINALIZE", "OBJECT_DELETE"]
        })
        return self
    
    # Storage Pattern Methods (High-level configurations)
    def media_storage(self):
        """Configure for media file storage (images, videos)"""
        self.storage_labels["purpose"] = "media"
        return (self
                .allow_images()
                .allow_videos()
                .thumbnail_generation()
                .image_optimization()
                .cache_images(86400)
                .cache_videos(604800)
                .compression()
                .cdn())
    
    def document_storage(self):
        """Configure for document storage"""
        self.storage_labels["purpose"] = "documents"
        return (self
                .allow_documents()
                .max_upload_size_mb(50)
                .cache_static_assets(3600)
                .strict_security_rules()
                .versioning())
    
    def backup_storage(self):
        """Configure for backup storage"""
        self.storage_labels["purpose"] = "backup"
        return (self
                .storage_class("COLDLINE")
                .retention_policy(2592000)  # 30 days
                .archive_after_days(90)
                .strict_security_rules()
                .logging())
    
    def user_uploads(self):
        """Configure for user file uploads"""
        self.storage_labels["purpose"] = "user_uploads"
        return (self
                .max_upload_size_mb(100)
                .strict_security_rules()
                .thumbnail_generation()
                .monitoring()
                .logging())
    
    def static_assets(self):
        """Configure for static asset hosting"""
        self.storage_labels["purpose"] = "static"
        return (self
                .public_read()
                .cache_static_assets()
                .compression()
                .cdn()
                .cors_allow_all())
    
    def archive_storage(self):
        """Configure for long-term archival"""
        self.storage_labels["purpose"] = "archive"
        return (self
                .storage_class("ARCHIVE")
                .retention_policy(31536000)  # 1 year
                .strict_security_rules()
                .logging())
    
    def cache_storage(self):
        """Configure for cache/temporary storage"""
        self.storage_labels["purpose"] = "cache"
        return (self
                .delete_after_days(7)
                .compression()
                .cache_control("**/*", 300))  # 5 minutes
    
    # Environment-specific configurations
    def development(self):
        """Configure for development environment"""
        self.storage_labels["environment"] = "development"
        return (self
                .permissive_security_rules()
                .cors_allow_all()
                .logging()
                .delete_after_days(30))
    
    def staging(self):
        """Configure for staging environment"""
        self.storage_labels["environment"] = "staging"
        return (self
                .authenticated_read()
                .cors_allow_all()
                .monitoring()
                .logging()
                .delete_after_days(90))
    
    def production(self):
        """Configure for production environment"""
        self.storage_labels["environment"] = "production"
        return (self
                .strict_security_rules()
                .cors_restrict_origins([])
                .monitoring()
                .logging()
                .cdn()
                .compression()
                .versioning())
    
    # Label and Metadata Methods
    def label(self, key: str, value: str):
        """Add label to storage bucket"""
        self.storage_labels[key] = value
        return self
        
    def labels(self, labels: Dict[str, str]):
        """Add multiple labels to storage bucket"""
        self.storage_labels.update(labels)
        return self
        
    def annotation(self, key: str, value: str):
        """Add annotation to storage bucket"""
        self.storage_annotations[key] = value
        return self
        
    def annotations(self, annotations: Dict[str, str]):
        """Add multiple annotations to storage bucket"""
        self.storage_annotations.update(annotations)
        return self
    
    # Helper Methods
    def get_bucket_name(self) -> str:
        """Get the bucket name (computed or custom)"""
        if self.bucket_name:
            return self.bucket_name
        elif self.firebase_project_id:
            return f"{self.firebase_project_id}.appspot.com"
        else:
            return f"{self.storage_name}.appspot.com"
    
    def has_security_rules(self) -> bool:
        """Check if custom security rules are configured"""
        return bool(self.security_rules_file or self.security_rules_content)
    
    def has_lifecycle_rules(self) -> bool:
        """Check if lifecycle rules are configured"""
        return len(self.lifecycle_rules) > 0
    
    def has_cors_configured(self) -> bool:
        """Check if CORS is configured"""
        return self.cors_enabled
    
    def has_caching_configured(self) -> bool:
        """Check if caching rules are configured"""
        return len(self.cache_control) > 0
    
    def has_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled"""
        return self.monitoring_enabled or self.logging_enabled
    
    def is_production_ready(self) -> bool:
        """Check if storage is configured for production use"""
        return (
            self.has_security_rules() and
            self.has_monitoring_enabled() and
            not self.public_access and
            self.cors_enabled and
            self.cors_origins != ["*"]
        )