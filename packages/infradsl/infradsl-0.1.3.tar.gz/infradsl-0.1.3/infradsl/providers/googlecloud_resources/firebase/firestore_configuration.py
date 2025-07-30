"""
Firestore Configuration Mixin

Configuration methods for Firebase Firestore.
Provides Rails-like method chaining for fluent database configuration.
"""

from typing import Dict, Any, List, Optional, Union


class FirestoreConfigurationMixin:
    """
    Configuration mixin for Firebase Firestore.
    
    This mixin provides:
    - Chainable configuration methods for database setup
    - Collection and document management methods
    - Security rules configuration
    - Index management and optimization
    - Backup and recovery configuration
    - Common database patterns (content, analytics, real-time, e-commerce)
    - Application-specific configurations (mobile, web, gaming, SaaS)
    - Environment-specific settings (development, staging, production)
    """
    
    # ========== Project and Database Configuration ==========
    
    def project(self, project_id: str):
        """Set Firebase project ID"""
        self.firebase_project_id = project_id
        self.label("project", project_id)
        return self
    
    def database_id(self, database_id: str):
        """Set database ID (default is '(default)')"""
        self.database_id = database_id
        self.label("database_id", database_id)
        return self
    
    def location(self, location_id: str):
        """Set database location"""
        if not self._is_valid_location(location_id):
            raise ValueError(f"Invalid location: {location_id}")
        self.location_id = location_id
        self.label("location", location_id)
        return self
    
    def mode(self, mode: str):
        """Set database mode (FIRESTORE_NATIVE or DATASTORE_MODE)"""
        if mode.lower() == "native" or mode == "FIRESTORE_NATIVE":
            self.database_mode = "FIRESTORE_NATIVE"
        elif mode.lower() == "datastore" or mode == "DATASTORE_MODE":
            self.database_mode = "DATASTORE_MODE"
        else:
            raise ValueError("Mode must be 'native', 'datastore', 'FIRESTORE_NATIVE', or 'DATASTORE_MODE'")
        self.label("mode", self.database_mode)
        return self
    
    def native_mode(self):
        """Set database to Firestore Native mode"""
        return self.mode("FIRESTORE_NATIVE")
    
    def datastore_mode(self):
        """Set database to Datastore compatibility mode"""
        return self.mode("DATASTORE_MODE")
    
    def description(self, description: str):
        """Set database description"""
        self.database_description = description
        return self
    
    # ========== Collection Configuration ==========
    
    def collections(self, collection_names: List[str]):
        """Define collections to create"""
        for name in collection_names:
            if not self._is_valid_collection_name(name):
                raise ValueError(f"Invalid collection name: {name}")
        self.collections = collection_names
        self.label("collection_count", str(len(collection_names)))
        return self
    
    def collection(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Add a single collection with optional configuration"""
        if not self._is_valid_collection_name(name):
            raise ValueError(f"Invalid collection name: {name}")
        
        if name not in self.collections:
            self.collections.append(name)
        
        if config:
            self.collection_configs[name] = config
        
        self.label("collection_count", str(len(self.collections)))
        return self
    
    def users_collection(self, name: str = "users"):
        """Add users collection with common configuration"""
        return self.collection(name, {
            "type": "users",
            "indexes": [
                {"fields": ["email"], "unique": True},
                {"fields": ["created_at"], "order": "desc"},
                {"fields": ["status", "created_at"]}
            ],
            "security_level": "high"
        })
    
    def products_collection(self, name: str = "products"):
        """Add products collection for e-commerce"""
        return self.collection(name, {
            "type": "products",
            "indexes": [
                {"fields": ["category", "price"]},
                {"fields": ["featured", "created_at"]},
                {"fields": ["status", "category", "price"]}
            ],
            "security_level": "medium"
        })
    
    def posts_collection(self, name: str = "posts"):
        """Add posts collection for content management"""
        return self.collection(name, {
            "type": "posts",
            "indexes": [
                {"fields": ["published", "created_at"]},
                {"fields": ["author_id", "created_at"]},
                {"fields": ["category", "published", "created_at"]}
            ],
            "security_level": "medium"
        })
    
    def messages_collection(self, name: str = "messages"):
        """Add messages collection for chat/messaging"""
        return self.collection(name, {
            "type": "messages",
            "indexes": [
                {"fields": ["room_id", "timestamp"]},
                {"fields": ["sender_id", "timestamp"]},
                {"fields": ["room_id", "read", "timestamp"]}
            ],
            "security_level": "high",
            "real_time": True
        })
    
    # ========== Security Rules Configuration ==========
    
    def security_rules(self, rules_content: str):
        """Set security rules content"""
        self.security_rules_content = rules_content
        self.default_security_rules = False
        self.label("security", "custom_rules")
        return self
    
    def security_rules_file(self, file_path: str):
        """Set security rules file path"""
        self.security_rules_file = file_path
        self.default_security_rules = False
        self.label("security", "rules_file")
        return self
    
    def default_rules(self):
        """Use default security rules (allow read/write if authenticated)"""
        self.default_security_rules = True
        self.security_rules_content = None
        self.security_rules_file = None
        self.label("security", "default")
        return self
    
    def open_rules(self):
        """Use open security rules (allow all read/write) - DEVELOPMENT ONLY"""
        self.security_rules_content = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
"""
        self.default_security_rules = False
        self.label("security", "open")
        self.label("environment", "development")
        return self
    
    def secure_rules(self):
        """Use secure security rules (authenticated users only)"""
        self.security_rules_content = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
"""
        self.default_security_rules = False
        self.label("security", "authenticated")
        return self
    
    def production_rules(self):
        """Use production-ready security rules with granular permissions"""
        self.security_rules_content = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Public read, authenticated write for posts
    match /posts/{postId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // Private messages - users involved only
    match /messages/{messageId} {
      allow read, write: if request.auth != null && 
        (request.auth.uid in resource.data.participants ||
         request.auth.uid == resource.data.sender_id);
    }
  }
}
"""
        self.default_security_rules = False
        self.label("security", "production")
        return self
    
    # ========== Index Configuration ==========
    
    def composite_index(self, collection: str, fields: List[Dict[str, str]], query_scope: str = "COLLECTION"):
        """Add a composite index"""
        index_config = {
            "collection_group": collection,
            "query_scope": query_scope,
            "fields": fields
        }
        self.composite_indexes.append(index_config)
        return self
    
    def single_field_index(self, collection: str, field: str, order: str = "ASCENDING"):
        """Add a single field index"""
        index_config = {
            "collection_group": collection,
            "field_path": field,
            "order": order
        }
        self.single_field_indexes.append(index_config)
        return self
    
    def ttl_policy(self, collection: str, field: str, retention_days: int = 30):
        """Add TTL (Time To Live) policy for automatic document deletion"""
        ttl_config = {
            "collection_group": collection,
            "field_path": field,
            "retention_seconds": retention_days * 24 * 60 * 60
        }
        self.ttl_policies.append(ttl_config)
        return self
    
    # ========== Backup and Recovery Configuration ==========
    
    def backup(self, enabled: bool = True, schedule: Optional[str] = None):
        """Enable backup with optional schedule"""
        self.backup_enabled = enabled
        if schedule:
            self.backup_schedule = schedule
        self.label("backup", "enabled" if enabled else "disabled")
        return self
    
    def daily_backup(self):
        """Enable daily backups"""
        return self.backup(True, "0 2 * * *")  # Daily at 2 AM
    
    def weekly_backup(self):
        """Enable weekly backups"""
        return self.backup(True, "0 2 * * 0")  # Weekly on Sunday at 2 AM
    
    def point_in_time_recovery(self, enabled: bool = True):
        """Enable point-in-time recovery"""
        self.point_in_time_recovery = enabled
        self.label("recovery", "pitr" if enabled else "backup_only")
        return self
    
    def delete_protection(self, enabled: bool = True):
        """Enable delete protection"""
        self.delete_protection = enabled
        self.label("protection", "enabled" if enabled else "disabled")
        return self
    
    # ========== Performance Configuration ==========
    
    def consistency(self, level: str):
        """Set read consistency level (STRONG or EVENTUAL)"""
        if level.upper() not in ["STRONG", "EVENTUAL"]:
            raise ValueError("Consistency level must be 'STRONG' or 'EVENTUAL'")
        self.read_time_consistency = level.upper()
        self.label("consistency", level.lower())
        return self
    
    def strong_consistency(self):
        """Use strong consistency (default)"""
        return self.consistency("STRONG")
    
    def eventual_consistency(self):
        """Use eventual consistency for better performance"""
        return self.consistency("EVENTUAL")
    
    def concurrency_mode(self, mode: str):
        """Set concurrency mode (OPTIMISTIC or PESSIMISTIC)"""
        if mode.upper() not in ["OPTIMISTIC", "PESSIMISTIC"]:
            raise ValueError("Concurrency mode must be 'OPTIMISTIC' or 'PESSIMISTIC'")
        self.concurrency_mode = mode.upper()
        self.label("concurrency", mode.lower())
        return self
    
    def optimistic_concurrency(self):
        """Use optimistic concurrency control (default)"""
        return self.concurrency_mode("OPTIMISTIC")
    
    def pessimistic_concurrency(self):
        """Use pessimistic concurrency control"""
        return self.concurrency_mode("PESSIMISTIC")
    
    # ========== App Engine Integration ==========
    
    def app_engine_integration(self, enabled: bool = True):
        """Enable App Engine integration"""
        self.app_engine_integration_mode = "ENABLED" if enabled else "DISABLED"
        self.label("app_engine", "enabled" if enabled else "disabled")
        return self
    
    # ========== Common Patterns ==========
    
    def simple_app_db(self):
        """Rails convenience: Simple app database with basic collections"""
        return (self.native_mode()
                .users_collection()
                .posts_collection()
                .secure_rules()
                .daily_backup()
                .label("type", "simple_app")
                .label("complexity", "basic"))
    
    def content_management_db(self):
        """Rails convenience: Content management database"""
        return (self.native_mode()
                .users_collection()
                .posts_collection()
                .collection("categories")
                .collection("comments")
                .collection("media")
                .production_rules()
                .daily_backup()
                .point_in_time_recovery()
                .label("type", "content_management")
                .label("complexity", "medium"))
    
    def ecommerce_db(self):
        """Rails convenience: E-commerce database"""
        return (self.native_mode()
                .users_collection()
                .products_collection()
                .collection("orders")
                .collection("cart_items")
                .collection("reviews")
                .collection("inventory")
                .production_rules()
                .daily_backup()
                .point_in_time_recovery()
                .delete_protection()
                .label("type", "ecommerce")
                .label("complexity", "high"))
    
    def real_time_db(self):
        """Rails convenience: Real-time application database"""
        return (self.native_mode()
                .users_collection()
                .messages_collection()
                .collection("rooms")
                .collection("notifications")
                .production_rules()
                .strong_consistency()
                .daily_backup()
                .label("type", "realtime")
                .label("complexity", "medium"))
    
    def analytics_db(self):
        """Rails convenience: Analytics and reporting database"""
        return (self.native_mode()
                .collection("events")
                .collection("sessions")
                .collection("users")
                .collection("reports")
                .ttl_policy("events", "timestamp", 90)  # 90 days retention
                .eventual_consistency()
                .weekly_backup()
                .label("type", "analytics")
                .label("complexity", "medium"))
    
    def gaming_db(self):
        """Rails convenience: Gaming application database"""
        return (self.native_mode()
                .users_collection("players")
                .collection("games")
                .collection("scores")
                .collection("achievements")
                .collection("leaderboards")
                .strong_consistency()
                .daily_backup()
                .label("type", "gaming")
                .label("complexity", "medium"))
    
    # ========== Application-Specific Configurations ==========
    
    def mobile_app_db(self):
        """Rails convenience: Mobile application database"""
        return (self.simple_app_db()
                .collection("devices")
                .collection("push_notifications")
                .label("platform", "mobile")
                .label("offline_support", "true"))
    
    def web_app_db(self):
        """Rails convenience: Web application database"""
        return (self.simple_app_db()
                .collection("sessions")
                .collection("analytics")
                .label("platform", "web")
                .label("realtime_updates", "true"))
    
    def saas_db(self):
        """Rails convenience: SaaS application database"""
        return (self.content_management_db()
                .collection("organizations")
                .collection("subscriptions")
                .collection("usage_metrics")
                .collection("billing")
                .delete_protection()
                .label("type", "saas")
                .label("multi_tenant", "true"))
    
    # ========== Environment-Specific Configurations ==========
    
    def development_db(self):
        """Rails convenience: Development environment database"""
        return (self.native_mode()
                .location("us-central1")
                .open_rules()
                .backup(False)
                .label("environment", "development")
                .label("cost_optimized", "true"))
    
    def staging_db(self):
        """Rails convenience: Staging environment database"""
        return (self.native_mode()
                .location("us-central1")
                .secure_rules()
                .weekly_backup()
                .label("environment", "staging")
                .label("testing", "true"))
    
    def production_db(self):
        """Rails convenience: Production environment database"""
        return (self.native_mode()
                .production_rules()
                .daily_backup()
                .point_in_time_recovery()
                .delete_protection()
                .strong_consistency()
                .label("environment", "production")
                .label("high_availability", "true"))
    
    # ========== Labels and Metadata ==========
    
    def label(self, key: str, value: str):
        """Add a label to the database"""
        self.database_labels[key] = value
        return self
    
    def labels(self, labels_dict: Dict[str, str]):
        """Add multiple labels to the database"""
        self.database_labels.update(labels_dict)
        return self
    
    def annotation(self, key: str, value: str):
        """Add an annotation to the database"""
        self.database_annotations[key] = value
        return self
    
    def annotations(self, annotations_dict: Dict[str, str]):
        """Add multiple annotations to the database"""
        self.database_annotations.update(annotations_dict)
        return self
    
    # ========== Utility Methods ==========
    
    def get_collection_count(self) -> int:
        """Get the number of configured collections"""
        return len(self.collections)
    
    def get_index_count(self) -> int:
        """Get the total number of configured indexes"""
        return len(self.composite_indexes) + len(self.single_field_indexes)
    
    def has_backup_enabled(self) -> bool:
        """Check if backup is enabled"""
        return self.backup_enabled
    
    def has_security_rules(self) -> bool:
        """Check if custom security rules are configured"""
        return not self.default_security_rules
    
    def is_production_ready(self) -> bool:
        """Check if database is configured for production"""
        return (self.has_security_rules() and 
                self.has_backup_enabled() and 
                self.delete_protection and
                self.read_time_consistency == "STRONG")
    
    def get_database_type(self) -> str:
        """Get database type from configuration"""
        return self._get_database_type_from_config()