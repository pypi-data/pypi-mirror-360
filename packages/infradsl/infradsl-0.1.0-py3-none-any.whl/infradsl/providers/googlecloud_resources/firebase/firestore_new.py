"""
Firestore Complete Implementation

Complete Firebase Firestore implementation combining core functionality, 
configuration methods, and lifecycle operations into a single modular class.
Rails-like API with Cross-Cloud Magic optimization.
"""

from typing import Dict, Any, List, Optional, Union
from .firestore_core import FirestoreCore
from .firestore_configuration import FirestoreConfigurationMixin
from .firestore_lifecycle import FirestoreLifecycleMixin


class Firestore(FirestoreCore, FirestoreConfigurationMixin, FirestoreLifecycleMixin):
    """
    Complete Firebase Firestore implementation.
    
    This class combines:
    - FirestoreCore: Basic database attributes and authentication
    - FirestoreConfigurationMixin: Chainable configuration methods
    - FirestoreLifecycleMixin: Lifecycle operations (create, destroy, preview)
    
    Features:
    - Rails-like method chaining for fluent database configuration
    - Smart state management and drift detection
    - Cross-Cloud Magic optimization
    - Complete NoSQL database support (collections, documents, indexes)
    - Security features (rules, backup, delete protection)
    - Performance optimization (consistency, concurrency, indexing)
    - Common database patterns (content, analytics, real-time, e-commerce)
    - Application-specific configurations (mobile, web, gaming, SaaS)
    - Environment-specific settings (development, staging, production)
    
    Example:
        # Simple database
        db = Firestore("my-app-db")
        db.project("my-firebase-project").simple_app_db()
        db.create()
        
        # Content management database
        db = Firestore("cms-db")
        db.project("my-project").content_management_db()
        db.create()
        
        # E-commerce database
        db = Firestore("ecommerce-db")
        db.project("shop-project").ecommerce_db()
        db.create()
        
        # Real-time database
        db = Firestore("realtime-db")
        db.project("chat-project").real_time_db()
        db.create()
        
        # Custom configuration
        db = Firestore("custom-db")
        db.project("my-project")
        db.users_collection().posts_collection().products_collection()
        db.production_rules().daily_backup().point_in_time_recovery()
        db.strong_consistency().delete_protection()
        db.label("environment", "production")
        db.create()
        
        # Gaming database
        db = Firestore("game-db")
        db.project("game-project").gaming_db()
        db.create()
        
        # Development database
        db = Firestore("dev-db")
        db.project("dev-project").development_db()
        db.create()
        
        # Cross-Cloud Magic optimization
        db = Firestore("optimized-db")
        db.project("my-project").content_management_db()
        db.optimize_for("security")
        db.create()
    """
    
    def __init__(self, name: str):
        """
        Initialize Firebase Firestore with database name.
        
        Args:
            name: Database name
        """
        # Initialize all parent classes
        FirestoreCore.__init__(self, name)
        
        # Ensure proper initialization order
        self._initialize_managers()
        
    def __repr__(self) -> str:
        """String representation of Firestore instance"""
        database_type = self._get_database_type_from_config()
        collection_count = len(self.collections)
        security_level = "high" if self.is_production_ready() else "medium" if self.has_security_rules() else "basic"
        status = "configured" if collection_count > 0 or self.firebase_project_id else "unconfigured"
        
        return (f"Firestore(name='{self.database_name}', "
                f"type='{database_type}', "
                f"collections={collection_count}, "
                f"project='{self.firebase_project_id}', "
                f"security='{security_level}', "
                f"status='{status}')")
    
    def summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of Firestore configuration.
        
        Returns:
            Dict containing all configuration details
        """
        # Analyze database configuration
        collection_types = []
        for collection in self.collections:
            if collection.lower() in ["users", "user", "accounts"]:
                collection_types.append("user_management")
            elif collection.lower() in ["posts", "articles", "content"]:
                collection_types.append("content_management")
            elif collection.lower() in ["products", "items", "catalog"]:
                collection_types.append("ecommerce")
            elif collection.lower() in ["messages", "chat", "conversations"]:
                collection_types.append("messaging")
            elif collection.lower() in ["analytics", "events", "metrics"]:
                collection_types.append("analytics")
        
        # Security features analysis
        security_features = []
        if self.has_security_rules():
            security_features.append("security_rules")
        if self.backup_enabled:
            security_features.append("backup")
        if self.point_in_time_recovery:
            security_features.append("point_in_time_recovery")
        if self.delete_protection:
            security_features.append("delete_protection")
        
        # Performance features analysis
        performance_features = []
        if self.read_time_consistency == "STRONG":
            performance_features.append("strong_consistency")
        if self.concurrency_mode == "OPTIMISTIC":
            performance_features.append("optimistic_concurrency")
        if self.composite_indexes:
            performance_features.append("composite_indexes")
        if self.single_field_indexes:
            performance_features.append("single_field_indexes")
        
        summary = {
            "database_name": self.database_name,
            "database_id": self.database_id,
            "firebase_project_id": self.firebase_project_id,
            "database_description": self.database_description,
            "database_type": self._get_database_type_from_config(),
            "collection_types": list(set(collection_types)),
            
            # Database configuration
            "location_id": self.location_id,
            "database_mode": self.database_mode,
            "concurrency_mode": self.concurrency_mode,
            "app_engine_integration_mode": self.app_engine_integration_mode,
            
            # Collections
            "collections": self.collections,
            "collection_count": len(self.collections),
            "collection_configs": self.collection_configs,
            
            # Security
            "security_features": security_features,
            "has_security_rules": self.has_security_rules(),
            "default_security_rules": self.default_security_rules,
            "security_rules_file": self.security_rules_file,
            
            # Backup and recovery
            "backup_enabled": self.backup_enabled,
            "backup_schedule": self.backup_schedule,
            "point_in_time_recovery": self.point_in_time_recovery,
            "delete_protection": self.delete_protection,
            
            # Performance
            "performance_features": performance_features,
            "read_time_consistency": self.read_time_consistency,
            "transaction_options": self.transaction_options,
            
            # Indexing
            "index_count": self.get_index_count(),
            "composite_indexes": self.composite_indexes,
            "single_field_indexes": self.single_field_indexes,
            "field_overrides": self.field_overrides,
            "ttl_policies": self.ttl_policies,
            
            # Production readiness
            "is_production_ready": self.is_production_ready(),
            "production_checklist": self._get_production_checklist(),
            
            # Labels and metadata
            "labels": self.database_labels,
            "label_count": len(self.database_labels),
            "annotations": self.database_annotations,
            
            # State
            "state": {
                "exists": self.database_exists,
                "created": self.database_created,
                "status": self.database_state,
                "deployment_status": self.deployment_status
            },
            
            # Cost
            "estimated_monthly_cost": f"${self._estimate_firestore_cost():.2f}",
            "is_free_tier": self._estimate_firestore_cost() <= 1.0
        }
        
        return summary
    
    def display_config(self):
        """Display current configuration in human-readable format"""
        print(f"\n🗄️  Firebase Firestore Configuration: {self.database_name}")
        print(f"   📁 Firebase Project: {self.firebase_project_id}")
        print(f"   🗃️  Database ID: {self.database_id}")
        print(f"   📝 Description: {self.database_description}")
        print(f"   🎯 Database Type: {self._get_database_type_from_config().replace('_', ' ').title()}")
        print(f"   🌍 Location: {self.location_id}")
        print(f"   🗃️  Mode: {self.database_mode}")
        
        # Collections
        if self.collections:
            print(f"\n📂 Collections ({len(self.collections)}):")
            for collection in self.collections:
                collection_icon = self._get_collection_icon(collection)
                print(f"   {collection_icon} {collection}")
                
                # Show collection config if available
                if collection in self.collection_configs:
                    config = self.collection_configs[collection]
                    if isinstance(config, dict):
                        for key, value in config.items():
                            if key == "indexes":
                                print(f"      └─ Indexes: {len(value) if isinstance(value, list) else 1}")
                            else:
                                print(f"      └─ {key}: {value}")
        else:
            print(f"\n📂 Collections: None configured")
        
        # Security configuration
        print(f"\n🔒 Security Configuration:")
        print(f"   🔐 Security Rules: {'✅ Custom' if self.has_security_rules() else '⚠️  Default'}")
        if self.security_rules_file:
            print(f"      └─ Rules File: {self.security_rules_file}")
        elif self.security_rules_content:
            print(f"      └─ Custom Rules: {len(self.security_rules_content)} characters")
        
        # Backup and recovery
        print(f"\n💾 Backup & Recovery:")
        print(f"   📦 Backup: {'✅ Enabled' if self.backup_enabled else '❌ Disabled'}")
        if self.backup_enabled and self.backup_schedule:
            print(f"      └─ Schedule: {self.backup_schedule}")
        print(f"   🕐 Point-in-Time Recovery: {'✅ Enabled' if self.point_in_time_recovery else '❌ Disabled'}")
        print(f"   🛡️  Delete Protection: {'✅ Enabled' if self.delete_protection else '❌ Disabled'}")
        
        # Performance configuration
        print(f"\n⚡ Performance Configuration:")
        print(f"   🎯 Consistency: {self.read_time_consistency}")
        print(f"   🔄 Concurrency: {self.concurrency_mode}")
        print(f"   🔗 App Engine Integration: {self.app_engine_integration_mode}")
        
        # Indexing
        index_count = self.get_index_count()
        if index_count > 0:
            print(f"\n📊 Indexing ({index_count} total):")
            if self.composite_indexes:
                print(f"   🔗 Composite Indexes: {len(self.composite_indexes)}")
                for i, index in enumerate(self.composite_indexes[:3]):
                    collection_group = index.get("collection_group", "unknown")
                    field_count = len(index.get("fields", []))
                    print(f"      ├─ {collection_group}: {field_count} fields")
                if len(self.composite_indexes) > 3:
                    print(f"      └─ ... and {len(self.composite_indexes) - 3} more")
            
            if self.single_field_indexes:
                print(f"   📄 Single Field Indexes: {len(self.single_field_indexes)}")
            
            if self.ttl_policies:
                print(f"   ⏰ TTL Policies: {len(self.ttl_policies)}")
        
        # Labels
        if self.database_labels:
            print(f"\n🏷️  Labels ({len(self.database_labels)}):")
            for key, value in list(self.database_labels.items())[:5]:
                print(f"   • {key}: {value}")
            if len(self.database_labels) > 5:
                print(f"   • ... and {len(self.database_labels) - 5} more")
        
        # Production readiness
        production_ready = self.is_production_ready()
        print(f"\n🚀 Production Readiness: {'✅ Ready' if production_ready else '⚠️  Needs attention'}")
        if not production_ready:
            checklist = self._get_production_checklist()
            missing = [item for item, status in checklist.items() if not status]
            for item in missing[:3]:
                print(f"   ⚠️  Missing: {item.replace('_', ' ').title()}")
        
        # Cost
        cost = self._estimate_firestore_cost()
        if cost > 1.0:
            print(f"\n💰 Estimated Cost: ${cost:.2f}/month")
        else:
            print(f"\n💰 Cost: Free tier")
        
        # Console link
        if self.firebase_project_id:
            print(f"\n🌐 Firebase Console:")
            print(f"   🔗 https://console.firebase.google.com/project/{self.firebase_project_id}/firestore/")
    
    def analyze_security(self) -> Dict[str, Any]:
        """
        Analyze Firestore security configuration and provide recommendations.
        
        Returns:
            Dict containing security analysis and recommendations
        """
        analysis = {
            "security_score": 0,
            "max_score": 100,
            "recommendations": [],
            "security_features": [],
            "risk_factors": []
        }
        
        # Security rules analysis
        if self.has_security_rules():
            analysis["security_score"] += 30
            analysis["security_features"].append("Custom security rules")
        else:
            analysis["risk_factors"].append("Using default security rules")
            analysis["recommendations"].append("Implement custom security rules")
        
        # Backup analysis
        if self.backup_enabled:
            analysis["security_score"] += 20
            analysis["security_features"].append("Backup enabled")
        else:
            analysis["recommendations"].append("Enable regular backups")
        
        # Point-in-time recovery
        if self.point_in_time_recovery:
            analysis["security_score"] += 15
            analysis["security_features"].append("Point-in-time recovery")
        else:
            analysis["recommendations"].append("Enable point-in-time recovery")
        
        # Delete protection
        if self.delete_protection:
            analysis["security_score"] += 15
            analysis["security_features"].append("Delete protection")
        else:
            analysis["recommendations"].append("Enable delete protection")
        
        # Location analysis
        if self.location_id in ["us-central1", "europe-west1"]:
            analysis["security_score"] += 10
            analysis["security_features"].append("Secure region selected")
        
        # Consistency level
        if self.read_time_consistency == "STRONG":
            analysis["security_score"] += 10
            analysis["security_features"].append("Strong consistency for data integrity")
        
        return analysis
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze Firestore performance configuration and provide recommendations.
        
        Returns:
            Dict containing performance analysis and recommendations
        """
        analysis = {
            "performance_score": 0,
            "max_score": 100,
            "recommendations": [],
            "performance_features": [],
            "bottlenecks": []
        }
        
        # Indexing analysis
        index_count = self.get_index_count()
        collection_count = len(self.collections)
        
        if collection_count > 0:
            index_ratio = index_count / collection_count
            if index_ratio >= 2:
                analysis["performance_score"] += 25
                analysis["performance_features"].append("Well-indexed collections")
            elif index_ratio >= 1:
                analysis["performance_score"] += 15
                analysis["performance_features"].append("Basic indexing")
            else:
                analysis["bottlenecks"].append("Insufficient indexing")
                analysis["recommendations"].append("Add more indexes for query performance")
        
        # Consistency analysis
        if self.read_time_consistency == "STRONG":
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Strong consistency")
        else:
            analysis["performance_score"] += 25
            analysis["performance_features"].append("Eventual consistency for better performance")
        
        # Concurrency analysis
        if self.concurrency_mode == "OPTIMISTIC":
            analysis["performance_score"] += 20
            analysis["performance_features"].append("Optimistic concurrency")
        
        # Location analysis
        if self.location_id in ["us-central1", "us-east1"]:
            analysis["performance_score"] += 15
            analysis["performance_features"].append("Low-latency region")
        
        # TTL policies for cleanup
        if self.ttl_policies:
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Automatic data cleanup with TTL")
        
        # Collection count analysis
        if collection_count <= 10:
            analysis["performance_score"] += 10
            analysis["performance_features"].append("Simple schema")
        elif collection_count > 50:
            analysis["bottlenecks"].append("Complex schema with many collections")
        
        return analysis
    
    def _get_production_checklist(self) -> Dict[str, bool]:
        """Get production readiness checklist"""
        return {
            "security_rules": self.has_security_rules(),
            "backup_enabled": self.backup_enabled,
            "point_in_time_recovery": self.point_in_time_recovery,
            "delete_protection": self.delete_protection,
            "strong_consistency": self.read_time_consistency == "STRONG",
            "proper_indexing": self.get_index_count() >= len(self.collections),
            "location_configured": bool(self.location_id),
            "project_configured": bool(self.firebase_project_id)
        }
    
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
            "files": "📎",
            "players": "🎮",
            "games": "🎯",
            "scores": "🏆",
            "achievements": "🏅",
            "leaderboards": "📈"
        }
        return icons.get(collection_name.lower(), "📄")
    
    # Utility methods for backwards compatibility
    def get_status(self) -> Dict[str, Any]:
        """Get database status for backwards compatibility"""
        return {
            "database_name": self.database_name,
            "database_id": self.database_id,
            "firebase_project_id": self.firebase_project_id,
            "database_type": self._get_database_type_from_config(),
            "collections": self.collections,
            "collection_count": len(self.collections),
            "has_security_rules": self.has_security_rules(),
            "has_backup_enabled": self.has_backup_enabled(),
            "is_production_ready": self.is_production_ready(),
            "estimated_cost": f"${self._estimate_firestore_cost():.2f}/month"
        }


# Convenience function for creating Firestore instances
def create_firestore(name: str) -> Firestore:
    """
    Create a new Firestore instance.
    
    Args:
        name: Database name
        
    Returns:
        Firestore instance
    """
    return Firestore(name)


# Export the class for easy importing
__all__ = ['Firestore', 'create_firestore']