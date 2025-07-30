"""
InfraDSL Marketplace - Firestore Schema Design

This module defines the Firestore schema for the InfraDSL marketplace with:
- Workspace isolation (like Slack)
- User accounts (individual open-source users)
- Template sharing and access control
- Version management
- Usage analytics

Schema Overview:
/users/{user_id}
/workspaces/{workspace_id}
/templates/{template_id}
/template_versions/{version_id}
/access_controls/{access_id}
/usage_analytics/{analytics_id}
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid


class TemplateVisibility(Enum):
    """Template visibility levels"""
    PRIVATE = "private"           # Only workspace members
    WORKSPACE = "workspace"       # All workspace members
    PUBLIC = "public"             # Everyone can see and use
    MARKETPLACE = "marketplace"   # Featured in public marketplace


class UserRole(Enum):
    """User roles within workspaces"""
    OWNER = "owner"              # Can manage workspace, billing, members
    ADMIN = "admin"              # Can manage templates, members
    DEVELOPER = "developer"      # Can create/edit templates
    VIEWER = "viewer"            # Can only view and use templates


class TemplateType(Enum):
    """Types of templates"""
    RESOURCE = "resource"        # Single resource (e.g., VM, Database)
    PATTERN = "pattern"          # Multiple resources (e.g., WebApp stack)
    BLUEPRINT = "blueprint"      # Complete application architecture
    COMPONENT = "component"      # Reusable component


# Firestore Collection Schemas

USERS_SCHEMA = {
    "collection": "users",
    "document_id": "{user_id}",  # Firebase Auth UID
    "fields": {
        "email": str,
        "display_name": str,
        "avatar_url": Optional[str],
        "github_username": Optional[str],
        "created_at": datetime,
        "last_active": datetime,
        "subscription_tier": str,  # "free", "pro", "enterprise"
        "workspaces": List[str],   # List of workspace IDs user belongs to
        "personal_templates": List[str],  # Template IDs for individual users
        "preferences": {
            "default_providers": List[str],
            "notification_settings": Dict[str, bool],
            "theme": str,
            "timezone": str
        },
        "stats": {
            "templates_created": int,
            "templates_used": int,
            "public_templates": int,
            "total_downloads": int
        }
    }
}

WORKSPACES_SCHEMA = {
    "collection": "workspaces",
    "document_id": "{workspace_id}",  # Generated UUID
    "fields": {
        "name": str,                    # e.g., "nolimitcity", "acme-corp"
        "display_name": str,            # e.g., "Nolimit City", "ACME Corporation"
        "slug": str,                    # URL-safe identifier
        "description": Optional[str],
        "website": Optional[str],
        "logo_url": Optional[str],
        "created_at": datetime,
        "updated_at": datetime,
        "owner_id": str,                # User ID of workspace owner
        "subscription": {
            "tier": str,                # "startup", "business", "enterprise"
            "status": str,              # "active", "suspended", "cancelled"
            "expires_at": Optional[datetime],
            "max_members": int,
            "max_templates": int,
            "max_private_templates": int
        },
        "settings": {
            "allow_public_templates": bool,
            "require_approval": bool,     # Require approval for public templates
            "default_visibility": str,   # Default template visibility
            "compliance_mode": bool,      # Enable compliance features
            "cost_tracking": bool,
            "audit_logging": bool
        },
        "stats": {
            "total_members": int,
            "total_templates": int,
            "public_templates": int,
            "monthly_downloads": int
        },
        "integrations": {
            "slack_webhook": Optional[str],
            "discord_webhook": Optional[str],
            "github_org": Optional[str],
            "custom_domain": Optional[str]
        }
    }
}

WORKSPACE_MEMBERS_SCHEMA = {
    "collection": "workspace_members",
    "document_id": "{workspace_id}_{user_id}",
    "fields": {
        "workspace_id": str,
        "user_id": str,
        "role": str,                    # UserRole enum value
        "invited_by": str,              # User ID who sent invitation
        "joined_at": datetime,
        "last_active": datetime,
        "permissions": {
            "create_templates": bool,
            "edit_templates": bool,
            "delete_templates": bool,
            "manage_members": bool,
            "manage_billing": bool,
            "publish_public": bool
        },
        "teams": List[str],             # Team names within workspace
        "status": str                   # "active", "suspended", "pending"
    }
}

TEMPLATES_SCHEMA = {
    "collection": "templates",
    "document_id": "{template_id}",     # Generated UUID
    "fields": {
        "name": str,                    # e.g., "prod-vm", "web-application"
        "display_name": str,            # e.g., "Production VM", "Web Application"
        "slug": str,                    # URL-safe identifier
        "description": str,
        "readme": Optional[str],        # Markdown documentation
        "workspace_id": Optional[str],  # None for individual user templates
        "creator_id": str,              # User who created the template
        "created_at": datetime,
        "updated_at": datetime,
        "template_type": str,           # TemplateType enum value
        "visibility": str,              # TemplateVisibility enum value
        "category": str,                # "compute", "database", "networking", etc.
        "providers": List[str],         # ["aws", "gcp", "azure", "digitalocean"]
        "tags": List[str],              # ["production", "web", "postgresql", etc.]
        "version_info": {
            "latest_version": str,      # Semantic version (e.g., "1.2.3")
            "total_versions": int,
            "stable_version": str,
            "beta_version": Optional[str]
        },
        "usage_stats": {
            "total_downloads": int,
            "weekly_downloads": int,
            "monthly_downloads": int,
            "unique_users": int,
            "average_rating": float,
            "total_ratings": int
        },
        "requirements": {
            "min_infradsl_version": str,
            "python_version": str,
            "dependencies": List[str]
        },
        "pricing": {
            "type": str,                # "free", "paid", "enterprise"
            "price": Optional[float],
            "currency": Optional[str],
            "billing_period": Optional[str]
        },
        "compliance": {
            "security_scan": bool,
            "license": str,
            "certifications": List[str],  # ["SOC2", "HIPAA", "PCI", etc.]
            "last_scanned": Optional[datetime]
        },
        "metadata": {
            "github_url": Optional[str],
            "documentation_url": Optional[str],
            "support_url": Optional[str],
            "changelog_url": Optional[str],
            "license_url": Optional[str]
        }
    }
}

TEMPLATE_VERSIONS_SCHEMA = {
    "collection": "template_versions",
    "document_id": "{template_id}_{version}",
    "fields": {
        "template_id": str,
        "version": str,                 # Semantic version
        "created_at": datetime,
        "created_by": str,              # User ID
        "changelog": str,               # What changed in this version
        "is_stable": bool,
        "is_beta": bool,
        "is_deprecated": bool,
        "source_code": {
            "python_class": str,        # The actual Python class code
            "dependencies": List[str],  # Required imports
            "examples": List[Dict[str, Any]],  # Usage examples
            "tests": Optional[str],     # Test code
            "validation_schema": Optional[Dict]  # JSON schema for validation
        },
        "compatibility": {
            "infradsl_versions": List[str],
            "python_versions": List[str],
            "provider_versions": Dict[str, str]
        },
        "security": {
            "scan_results": Optional[Dict],
            "vulnerabilities": List[Dict],
            "security_score": Optional[int]
        },
        "performance": {
            "deployment_time": Optional[float],
            "resource_efficiency": Optional[float],
            "cost_optimization": Optional[float]
        }
    }
}

ACCESS_CONTROLS_SCHEMA = {
    "collection": "access_controls",
    "document_id": "{access_id}",
    "fields": {
        "template_id": str,
        "workspace_id": Optional[str],
        "user_id": Optional[str],
        "access_type": str,             # "read", "write", "admin"
        "granted_by": str,              # User ID who granted access
        "granted_at": datetime,
        "expires_at": Optional[datetime],
        "conditions": {
            "ip_restrictions": List[str],
            "time_restrictions": Optional[Dict],
            "usage_limits": Optional[Dict]
        }
    }
}

USAGE_ANALYTICS_SCHEMA = {
    "collection": "usage_analytics",
    "document_id": "{analytics_id}",
    "fields": {
        "template_id": str,
        "version": str,
        "user_id": str,
        "workspace_id": Optional[str],
        "action": str,                  # "download", "deploy", "star", "rate"
        "timestamp": datetime,
        "metadata": {
            "provider": Optional[str],
            "region": Optional[str],
            "resource_count": Optional[int],
            "deployment_success": Optional[bool],
            "error_message": Optional[str],
            "user_agent": Optional[str],
            "ip_address": Optional[str]
        },
        "performance": {
            "download_time": Optional[float],
            "deployment_time": Optional[float],
            "resource_cost": Optional[float]
        }
    }
}

TEMPLATE_RATINGS_SCHEMA = {
    "collection": "template_ratings",
    "document_id": "{template_id}_{user_id}",
    "fields": {
        "template_id": str,
        "user_id": str,
        "workspace_id": Optional[str],
        "rating": int,                  # 1-5 stars
        "review": Optional[str],
        "created_at": datetime,
        "updated_at": datetime,
        "verified_usage": bool,         # User actually deployed the template
        "helpful_votes": int,
        "reported": bool
    }
}

# Firestore Security Rules Template
FIRESTORE_SECURITY_RULES = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Workspace access control
    match /workspaces/{workspaceId} {
      allow read: if request.auth != null && 
        (isWorkspaceMember(workspaceId, request.auth.uid) || 
         resource.data.settings.allow_public_templates == true);
      allow write: if request.auth != null && 
        isWorkspaceAdmin(workspaceId, request.auth.uid);
    }
    
    // Workspace members
    match /workspace_members/{memberId} {
      allow read: if request.auth != null && 
        (request.auth.uid == resource.data.user_id ||
         isWorkspaceAdmin(resource.data.workspace_id, request.auth.uid));
      allow write: if request.auth != null && 
        isWorkspaceAdmin(resource.data.workspace_id, request.auth.uid);
    }
    
    // Templates access control
    match /templates/{templateId} {
      allow read: if request.auth != null && canReadTemplate(templateId, request.auth.uid);
      allow write: if request.auth != null && canWriteTemplate(templateId, request.auth.uid);
    }
    
    // Template versions
    match /template_versions/{versionId} {
      allow read: if request.auth != null && canReadTemplate(getTemplateId(versionId), request.auth.uid);
      allow write: if request.auth != null && canWriteTemplate(getTemplateId(versionId), request.auth.uid);
    }
    
    // Helper functions
    function isWorkspaceMember(workspaceId, userId) {
      return exists(/databases/$(database)/documents/workspace_members/$(workspaceId + '_' + userId));
    }
    
    function isWorkspaceAdmin(workspaceId, userId) {
      let membership = get(/databases/$(database)/documents/workspace_members/$(workspaceId + '_' + userId));
      return membership.data.role in ['owner', 'admin'];
    }
    
    function canReadTemplate(templateId, userId) {
      let template = get(/databases/$(database)/documents/templates/$(templateId));
      return template.data.visibility == 'public' ||
             template.data.creator_id == userId ||
             (template.data.workspace_id != null && 
              isWorkspaceMember(template.data.workspace_id, userId));
    }
    
    function canWriteTemplate(templateId, userId) {
      let template = get(/databases/$(database)/documents/templates/$(templateId));
      return template.data.creator_id == userId ||
             (template.data.workspace_id != null && 
              isWorkspaceAdmin(template.data.workspace_id, userId));
    }
    
    function getTemplateId(versionId) {
      return versionId.split('_')[0];
    }
  }
}
"""


class FirestoreCollections:
    """Firestore collection names as constants"""
    USERS = "users"
    WORKSPACES = "workspaces"
    WORKSPACE_MEMBERS = "workspace_members"
    TEMPLATES = "templates"
    TEMPLATE_VERSIONS = "template_versions"
    ACCESS_CONTROLS = "access_controls"
    USAGE_ANALYTICS = "usage_analytics"
    TEMPLATE_RATINGS = "template_ratings"


# Index requirements for efficient queries
FIRESTORE_INDEXES = [
    {
        "collection": "templates",
        "fields": [
            {"field": "workspace_id", "order": "ASCENDING"},
            {"field": "visibility", "order": "ASCENDING"},
            {"field": "created_at", "order": "DESCENDING"}
        ]
    },
    {
        "collection": "templates", 
        "fields": [
            {"field": "category", "order": "ASCENDING"},
            {"field": "visibility", "order": "ASCENDING"},
            {"field": "usage_stats.weekly_downloads", "order": "DESCENDING"}
        ]
    },
    {
        "collection": "template_versions",
        "fields": [
            {"field": "template_id", "order": "ASCENDING"},
            {"field": "created_at", "order": "DESCENDING"}
        ]
    },
    {
        "collection": "workspace_members",
        "fields": [
            {"field": "workspace_id", "order": "ASCENDING"},
            {"field": "role", "order": "ASCENDING"},
            {"field": "status", "order": "ASCENDING"}
        ]
    },
    {
        "collection": "usage_analytics",
        "fields": [
            {"field": "template_id", "order": "ASCENDING"},
            {"field": "timestamp", "order": "DESCENDING"}
        ]
    }
]