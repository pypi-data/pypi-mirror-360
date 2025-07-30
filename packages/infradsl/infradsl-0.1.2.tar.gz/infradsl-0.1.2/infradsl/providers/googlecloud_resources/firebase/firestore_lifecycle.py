"""
Firestore Lifecycle Mixin

Lifecycle operations for Firebase Firestore.
Provides create, destroy, and preview operations with smart state management.
"""

import json
import os
import subprocess
from typing import Dict, Any, List, Optional, Union


class FirestoreLifecycleMixin:
    """
    Mixin for Firebase Firestore lifecycle operations.
    
    This mixin provides:
    - preview(): Preview what will be created/updated/deleted
    - create(): Create or update Firestore database configuration
    - destroy(): Clean up Firestore database configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    """
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        # Discover existing databases
        existing_databases = self._discover_existing_databases()
        
        # Categorize databases
        databases_to_create = []
        databases_to_keep = []
        databases_to_update = []
        
        # Check if our desired database exists
        desired_database_id = self.database_id
        database_exists = desired_database_id in existing_databases
        
        if not database_exists:
            if self.collections or self.firebase_project_id:
                databases_to_create.append({
                    'database_name': self.database_name,
                    'database_id': self.database_id,
                    'firebase_project_id': self.firebase_project_id,
                    'location_id': self.location_id,
                    'database_mode': self.database_mode,
                    'collection_count': len(self.collections),
                    'collections': self.collections[:10],  # Show first 10
                    'database_type': self._get_database_type_from_config(),
                    'has_security_rules': self.has_security_rules(),
                    'has_backup_enabled': self.has_backup_enabled(),
                    'index_count': self.get_index_count(),
                    'is_production_ready': self.is_production_ready(),
                    'labels': self.database_labels,
                    'label_count': len(self.database_labels),
                    'estimated_cost': self._estimate_firestore_cost()
                })
        else:
            existing_database = existing_databases[desired_database_id]
            existing_collections = existing_database.get('collections', [])
            
            # Check if update is needed
            if set(self.collections) != set(existing_collections):
                databases_to_update.append({
                    'database_name': self.database_name,
                    'database_id': self.database_id,
                    'current_collections': existing_collections,
                    'desired_collections': self.collections,
                    'collections_to_add': list(set(self.collections) - set(existing_collections)),
                    'collections_to_remove': list(set(existing_collections) - set(self.collections))
                })
            else:
                databases_to_keep.append(existing_database)

        print(f"\n🗄️  Firebase Firestore Preview")
        
        # Show databases to create
        if databases_to_create:
            print(f"╭─ 🗄️  Firestore Databases to CREATE: {len(databases_to_create)}")
            for db in databases_to_create:
                print(f"├─ 🆕 {db['database_name']} ({db['database_id']})")
                print(f"│  ├─ 📁 Firebase Project: {db['firebase_project_id']}")
                print(f"│  ├─ 🌍 Location: {db['location_id']}")
                print(f"│  ├─ 🎯 Database Type: {db['database_type'].replace('_', ' ').title()}")
                print(f"│  ├─ 🗃️  Mode: {db['database_mode']}")
                print(f"│  ├─ 📊 Collections: {db['collection_count']}")
                
                # Show collection details
                if db['collections']:
                    print(f"│  ├─ 📂 Collection Details:")
                    for i, collection in enumerate(db['collections'][:5]):
                        connector = "│  │  ├─" if i < min(len(db['collections']), 5) - 1 else "│  │  └─"
                        print(f"{connector} 📄 {collection}")
                    
                    if len(db['collections']) > 5:
                        print(f"│  │     └─ ... and {len(db['collections']) - 5} more collections")
                
                # Show indexes
                if db['index_count'] > 0:
                    print(f"│  ├─ 📊 Indexes: {db['index_count']}")
                
                # Show security and backup
                print(f"│  ├─ 🔒 Security & Backup:")
                print(f"│  │  ├─ 🔐 Security Rules: {'✅ Custom' if db['has_security_rules'] else '⚠️  Default'}")
                print(f"│  │  ├─ 💾 Backup: {'✅ Enabled' if db['has_backup_enabled'] else '❌ Disabled'}")
                print(f"│  │  └─ 🚀 Production Ready: {'✅ Yes' if db['is_production_ready'] else '⚠️  No'}")
                
                # Show labels
                if db['label_count'] > 0:
                    print(f"│  ├─ 🏷️  Labels: {db['label_count']}")
                
                # Show Firestore features
                print(f"│  ├─ 🚀 Firestore Features:")
                print(f"│  │  ├─ 🆓 Free tier available")
                print(f"│  │  ├─ 📱 Real-time synchronization")
                print(f"│  │  ├─ 🔐 Built-in security rules")
                print(f"│  │  ├─ 📊 Automatic scaling")
                print(f"│  │  └─ 🌐 Multi-region support")
                
                cost = db['estimated_cost']
                if cost > 1.0:
                    print(f"│  └─ 💰 Estimated Cost: ${cost:.2f}/month")
                else:
                    print(f"│  └─ 💰 Cost: Free tier")
            print(f"╰─")

        # Show databases to update
        if databases_to_update:
            print(f"\n╭─ 🗄️  Firestore Databases to UPDATE: {len(databases_to_update)}")
            for db in databases_to_update:
                print(f"├─ 🔄 {db['database_name']} ({db['database_id']})")
                
                if db['collections_to_add']:
                    print(f"│  ├─ ➕ Collections to Add:")
                    for collection in db['collections_to_add']:
                        print(f"│  │  ├─ 📄 {collection}")
                
                if db['collections_to_remove']:
                    print(f"│  ├─ ➖ Collections to Remove:")
                    for collection in db['collections_to_remove']:
                        print(f"│  │  ├─ 📄 {collection}")
                
                print(f"│  └─ 📊 Current: {len(db['current_collections'])} → Desired: {len(db['desired_collections'])}")
            print(f"╰─")

        # Show existing databases being kept
        if databases_to_keep:
            print(f"\n╭─ 🗄️  Existing Firestore Databases to KEEP: {len(databases_to_keep)}")
            for db in databases_to_keep:
                status_icon = "🟢" if db.get('state') == 'ACTIVE' else "🟡"
                print(f"├─ {status_icon} {db['database_id']}")
                print(f"│  ├─ 📁 Firebase Project: {db['firebase_project_id']}")
                print(f"│  ├─ 🌍 Location: {db['location_id']}")
                print(f"│  ├─ 📊 State: {db.get('state', 'unknown').title()}")
                
                collections = db.get('collections', [])
                if collections:
                    print(f"│  ├─ 📂 Collections: {len(collections)}")
                    for collection in collections[:3]:
                        print(f"│  │  ├─ 📄 {collection}")
                    if len(collections) > 3:
                        print(f"│  │  └─ ... and {len(collections) - 3} more")
                
                document_count = db.get('document_count', 0)
                if document_count > 0:
                    print(f"│  ├─ 📄 Documents: {document_count:,}")
                
                print(f"│  └─ 🌐 Console: https://console.firebase.google.com/project/{db['firebase_project_id']}/firestore/")
            print(f"╰─")

        # Show cost information
        print(f"\n💰 Firebase Firestore Costs:")
        if databases_to_create:
            db = databases_to_create[0]
            cost = db['estimated_cost']
            
            print(f"   ├─ 📖 Document reads: $0.036 per 100K operations")
            print(f"   ├─ ✍️  Document writes: $0.18 per 100K operations")
            print(f"   ├─ 🗑️  Document deletes: $0.002 per 100K operations")
            print(f"   ├─ 💾 Storage: $0.18 per GB/month")
            print(f"   ├─ 🌐 Network egress: $0.12 per GB")
            
            if cost > 1.0:
                print(f"   └─ 📊 Estimated: ${cost:.2f}/month")
            else:
                print(f"   └─ 📊 Total: Free tier (first 1 GB storage free)")
        else:
            print(f"   ├─ 🆓 First 50K reads/day: Free")
            print(f"   ├─ 🆓 First 20K writes/day: Free")
            print(f"   ├─ 🆓 First 20K deletes/day: Free")
            print(f"   ├─ 🆓 First 1 GB storage: Free")
            print(f"   └─ 📊 Most small apps: Free tier")

        return {
            'resource_type': 'firebase_firestore',
            'name': self.database_name,
            'databases_to_create': databases_to_create,
            'databases_to_update': databases_to_update,
            'databases_to_keep': databases_to_keep,
            'existing_databases': existing_databases,
            'firebase_project_id': self.firebase_project_id,
            'database_type': self._get_database_type_from_config(),
            'collection_count': len(self.collections),
            'estimated_cost': f"${self._estimate_firestore_cost():.2f}/month"
        }

    def create(self) -> Dict[str, Any]:
        """Create or update Firebase Firestore database"""
        if not self.firebase_project_id:
            raise ValueError("Firebase project ID is required. Use .project('your-project-id')")
        
        existing_database = self._find_existing_database()
        if existing_database and existing_database.get("exists", False):
            print(f"🔄 Firestore database '{self.database_name}' already exists")
            return self._update_existing_database(existing_database)
        
        print(f"🚀 Creating Firebase Firestore Database: {self.database_name}")
        return self._create_new_database()

    def destroy(self) -> Dict[str, Any]:
        """Destroy Firebase Firestore database"""
        print(f"🗑️  Destroying Firebase Firestore Database: {self.database_name}")

        try:
            print(f"⚠️  Firestore database cannot be automatically destroyed")
            print(f"🔧 To delete the database:")
            print(f"   1. Go to Firestore Console: https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/")
            print(f"   2. Click 'Settings' → 'General'")
            print(f"   3. Click 'Delete database'")
            print(f"   4. Type the database ID to confirm")
            
            # Remove local config files
            config_files = ["firestore-config.json", "firestore.rules", "firestore.indexes.json"]
            removed_files = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    os.remove(config_file)
                    removed_files.append(config_file)
            
            if removed_files:
                print(f"   🗑️  Removed local config files: {', '.join(removed_files)}")
            
            return {
                'success': True, 
                'database_name': self.database_name, 
                'status': 'manual_action_required',
                'removed_files': removed_files,
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/"
            }

        except Exception as e:
            print(f"❌ Failed to destroy Firestore database: {str(e)}")
            return {'success': False, 'error': str(e)}

    def optimize_for(self, optimization_target: str):
        """
        Cross-Cloud Magic: Optimize Firestore configuration for specific targets.
        
        Args:
            optimization_target: Target to optimize for ('cost', 'performance', 'security', 'user_experience')
        """
        if optimization_target.lower() == "cost":
            return self._optimize_for_cost()
        elif optimization_target.lower() == "performance":
            return self._optimize_for_performance()
        elif optimization_target.lower() == "security":
            return self._optimize_for_security()
        elif optimization_target.lower() == "user_experience":
            return self._optimize_for_user_experience()
        else:
            print(f"⚠️  Unknown optimization target: {optimization_target}")
            return self

    def _optimize_for_cost(self):
        """Optimize configuration for cost efficiency"""
        print("🏗️  Applying Cross-Cloud Magic: Cost Optimization")
        
        # Use free tier location
        self.location("us-central1")
        
        # Disable expensive features
        self.backup(False)
        self.point_in_time_recovery(False)
        
        # Use eventual consistency for better performance/cost
        self.eventual_consistency()
        
        # Add cost optimization labels
        self.database_labels.update({
            "optimization": "cost",
            "cost_management": "enabled",
            "tier": "free"
        })
        
        print("   ├─ 🌍 Set to us-central1 (free tier)")
        print("   ├─ 💾 Disabled backup (cost reduction)")
        print("   ├─ 🕐 Set eventual consistency")
        print("   └─ 🏷️  Added cost optimization labels")
        
        return self

    def _optimize_for_performance(self):
        """Optimize configuration for performance"""
        print("🏗️  Applying Cross-Cloud Magic: Performance Optimization")
        
        # Use strong consistency for best performance
        self.strong_consistency()
        
        # Use optimistic concurrency
        self.optimistic_concurrency()
        
        # Add performance indexes for common patterns
        if "users" in self.collections:
            self.composite_index("users", [
                {"field_path": "status", "order": "ASCENDING"},
                {"field_path": "created_at", "order": "DESCENDING"}
            ])
        
        # Add performance labels
        self.database_labels.update({
            "optimization": "performance",
            "consistency": "strong",
            "indexing": "optimized"
        })
        
        print("   ├─ 🎯 Set strong consistency")
        print("   ├─ ⚡ Set optimistic concurrency")
        print("   ├─ 📊 Added performance indexes")
        print("   └─ 🏷️  Added performance optimization labels")
        
        return self

    def _optimize_for_security(self):
        """Optimize configuration for security"""
        print("🏗️  Applying Cross-Cloud Magic: Security Optimization")
        
        # Enable all security features
        self.production_rules()
        self.daily_backup()
        self.point_in_time_recovery()
        self.delete_protection()
        
        # Use strong consistency for security
        self.strong_consistency()
        
        # Add security labels
        self.database_labels.update({
            "optimization": "security",
            "security_level": "maximum",
            "compliance": "enabled",
            "audit": "required"
        })
        
        print("   ├─ 🔐 Enabled production security rules")
        print("   ├─ 💾 Enabled daily backup")
        print("   ├─ 🕐 Enabled point-in-time recovery")
        print("   ├─ 🛡️  Enabled delete protection")
        print("   └─ 🏷️  Added security optimization labels")
        
        return self

    def _optimize_for_user_experience(self):
        """Optimize configuration for user experience"""
        print("🏗️  Applying Cross-Cloud Magic: User Experience Optimization")
        
        # Use location closest to users (assume US-based)
        self.location("us-central1")
        
        # Use strong consistency for predictable behavior
        self.strong_consistency()
        
        # Enable common collections for good UX
        self.users_collection()
        if "posts" not in self.collections:
            self.posts_collection()
        
        # Reasonable security (not too restrictive)
        self.secure_rules()
        
        # Add UX labels
        self.database_labels.update({
            "optimization": "user_experience",
            "ux_focused": "true",
            "location_optimized": "true"
        })
        
        print("   ├─ 🌍 Set optimal location")
        print("   ├─ 🎯 Set strong consistency")
        print("   ├─ 📂 Added common collections")
        print("   ├─ 🔐 Set balanced security")
        print("   └─ 🏷️  Added UX optimization labels")
        
        return self

    def _find_existing_database(self) -> Optional[Dict[str, Any]]:
        """Find existing Firestore database"""
        return self._fetch_current_firestore_state()

    def _create_new_database(self) -> Dict[str, Any]:
        """Create new Firebase Firestore database"""
        try:
            print(f"   📋 Project: {self.firebase_project_id}")
            print(f"   🗃️  Database ID: {self.database_id}")
            print(f"   🌍 Location: {self.location_id}")
            print(f"   📊 Collections: {len(self.collections)}")
            
            # Create database configuration
            firestore_config = {
                "firestore": {
                    "project_id": self.firebase_project_id,
                    "database_id": self.database_id,
                    "location_id": self.location_id,
                    "database_mode": self.database_mode,
                    "concurrency_mode": self.concurrency_mode,
                    "app_engine_integration_mode": self.app_engine_integration_mode,
                    "collections": self.collections,
                    "collection_configs": self.collection_configs,
                    "security": {
                        "rules_file": self.security_rules_file,
                        "rules_content": self.security_rules_content,
                        "default_rules": self.default_security_rules
                    },
                    "indexes": {
                        "composite_indexes": self.composite_indexes,
                        "single_field_indexes": self.single_field_indexes,
                        "field_overrides": self.field_overrides,
                        "ttl_policies": self.ttl_policies
                    },
                    "backup": {
                        "enabled": self.backup_enabled,
                        "schedule": self.backup_schedule,
                        "point_in_time_recovery": self.point_in_time_recovery,
                        "delete_protection": self.delete_protection
                    },
                    "performance": {
                        "read_time_consistency": self.read_time_consistency,
                        "transaction_options": self.transaction_options
                    },
                    "labels": self.database_labels,
                    "annotations": self.database_annotations,
                    "created_by": "infradsl"
                }
            }
            
            # Save configuration to file
            config_path = "firestore-config.json"
            with open(config_path, 'w') as f:
                json.dump(firestore_config, f, indent=2)
            
            print(f"   📄 Config saved to: {config_path}")
            
            # Create security rules file if custom rules provided
            if self.security_rules_content:
                rules_path = "firestore.rules"
                with open(rules_path, 'w') as f:
                    f.write(self.security_rules_content)
                print(f"   🔐 Security rules saved to: {rules_path}")
            
            # Create indexes file if indexes configured
            if self.composite_indexes or self.single_field_indexes:
                indexes_config = {
                    "indexes": self.composite_indexes,
                    "fieldOverrides": self.field_overrides
                }
                
                indexes_path = "firestore.indexes.json"
                with open(indexes_path, 'w') as f:
                    json.dump(indexes_config, f, indent=2)
                print(f"   📊 Indexes saved to: {indexes_path}")
            
            # Show collection details
            if self.collections:
                print(f"   📂 Configured Collections:")
                for collection in self.collections[:5]:
                    collection_icon = self._get_collection_icon(collection)
                    print(f"      {collection_icon} {collection}")
                if len(self.collections) > 5:
                    print(f"      ... and {len(self.collections) - 5} more")
            
            # Show features
            features = []
            if self.has_security_rules():
                features.append("Security Rules")
            if self.has_backup_enabled():
                features.append("Backup")
            if self.delete_protection:
                features.append("Delete Protection")
            if self.point_in_time_recovery:
                features.append("Point-in-Time Recovery")
            
            if features:
                print(f"   🚀 Features: {', '.join(features)}")
            
            console_url = f"https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/"
            print(f"✅ Firebase Firestore database configured successfully!")
            print(f"🌐 Console: {console_url}")
            
            return self._get_database_info()

        except Exception as e:
            print(f"❌ Failed to create Firestore database: {str(e)}")
            raise

    def _update_existing_database(self, existing_database: Dict[str, Any]):
        """Update existing Firestore database configuration"""
        print(f"   🔄 Updating existing configuration")
        # For Firestore, we typically recreate the config
        return self._create_new_database()

    def _get_collection_icon(self, collection_name: str) -> str:
        """Get icon for collection type"""
        icons = {
            "users": "👥",
            "posts": "📝",
            "products": "🛍️",
            "orders": "📦",
            "messages": "💬",
            "notifications": "🔔",
            "analytics": "📊",
            "sessions": "🔐",
            "comments": "💭",
            "reviews": "⭐",
            "categories": "📁",
            "tags": "🏷️",
            "media": "🖼️",
            "files": "📎"
        }
        return icons.get(collection_name.lower(), "📄")

    def _get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            return {
                'success': True,
                'database_name': self.database_name,
                'database_id': self.database_id,
                'firebase_project_id': self.firebase_project_id,
                'database_description': self.database_description,
                'location_id': self.location_id,
                'database_mode': self.database_mode,
                'collections': self.collections,
                'collection_count': len(self.collections),
                'database_type': self._get_database_type_from_config(),
                'has_security_rules': self.has_security_rules(),
                'has_backup_enabled': self.has_backup_enabled(),
                'is_production_ready': self.is_production_ready(),
                'index_count': self.get_index_count(),
                'composite_indexes': self.composite_indexes,
                'single_field_indexes': self.single_field_indexes,
                'backup_enabled': self.backup_enabled,
                'point_in_time_recovery': self.point_in_time_recovery,
                'delete_protection': self.delete_protection,
                'read_time_consistency': self.read_time_consistency,
                'concurrency_mode': self.concurrency_mode,
                'labels': self.database_labels,
                'estimated_monthly_cost': f"${self._estimate_firestore_cost():.2f}",
                'console_url': f"https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}