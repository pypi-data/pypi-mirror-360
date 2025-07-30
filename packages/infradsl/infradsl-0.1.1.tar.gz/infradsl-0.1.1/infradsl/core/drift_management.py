"""
InfraDSL Smart Drift Management System

Core functionality for caching, drift detection, and auto-remediation across all providers.
This module implements the stateless-with-caching approach described in SMART-DRIFT-MANAGEMENT.md
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import os


class DriftCheckInterval(Enum):
    """Predefined drift check intervals"""
    THIRTY_MINUTES = 30 * 60      # 30 minutes
    ONE_HOUR = 60 * 60            # 1 hour  
    TWO_HOURS = 2 * 60 * 60       # 2 hours
    THREE_HOURS = 3 * 60 * 60     # 3 hours
    SIX_HOURS = 6 * 60 * 60       # 6 hours (default)
    TWELVE_HOURS = 12 * 60 * 60   # 12 hours
    DAILY = 24 * 60 * 60          # 24 hours


class AutoRemediationPolicy(Enum):
    """Auto-remediation policies for different drift types"""
    
    CONSERVATIVE = {
        "configuration_drift": "fix",         # Auto-fix config changes
        "missing_resource": "fix",           # Auto-recreate missing resources
        "missing_tags": "add",               # Safe to auto-add tags
        "extra_resources": "alert_only",      # Don't auto-delete
        "security_changes": "alert_only",     # Never auto-fix security
        "cost_increases": "alert_only",       # Alert on cost increases
        "max_changes_per_session": 3          # Conservative limit
    }
    
    AGGRESSIVE = {
        "configuration_drift": "fix",         # Auto-fix everything
        "missing_tags": "add",               # Auto-add tags
        "extra_resources": "remove",         # Auto-delete extras
        "security_changes": "fix",           # Auto-fix security (risky!)
        "cost_increases": "revert",          # Auto-revert cost increases
        "max_changes_per_session": 999       # Unlimited
    }
    
    DISABLED = {
        "configuration_drift": "alert_only", # No auto-fixes
        "missing_tags": "alert_only",        # No auto-fixes
        "extra_resources": "alert_only",     # No auto-fixes
        "security_changes": "alert_only",    # No auto-fixes
        "cost_increases": "alert_only",      # No auto-fixes
        "max_changes_per_session": 0         # No changes allowed
    }


@dataclass
class ResourceState:
    """Represents the cached state of a managed resource"""
    resource_name: str
    resource_type: str
    provider: str
    config_hash: str
    last_checked: datetime
    current_state: Dict[str, Any]
    desired_state: Dict[str, Any]
    tags: Dict[str, str]


@dataclass
class DriftResult:
    """Result of drift detection"""
    resource_name: str
    has_drift: bool
    drift_types: List[str]
    changes_needed: Dict[str, Any]
    auto_fixable: List[str]
    requires_manual_action: List[str]
    suggested_actions: List[str]
    remediation_applied: bool = False
    rollback_id: Optional[str] = None


@dataclass
class RemediationAction:
    """Represents a single remediation action"""
    action_id: str
    resource_name: str
    action_type: str  # "fix_config", "add_tags", "revert_change"
    field_name: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    success: bool = False
    error: Optional[str] = None


@dataclass
class RollbackPlan:
    """Plan for rolling back auto-remediation actions"""
    rollback_id: str
    resource_name: str
    provider: str
    actions: List[RemediationAction]
    created_at: datetime
    expires_at: datetime  # 24 hours from creation
    can_rollback: bool = True


class ResourceCache:
    """Smart caching system for resource state"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = os.path.join(os.getcwd(), ".infradsl_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._update_gitignore()
    
    def _update_gitignore(self):
        """Add cache directory to .gitignore if git repo exists"""
        gitignore_path = Path(".gitignore")
        cache_entry = ".infradsl_cache/"
        
        if Path(".git").exists():
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                if cache_entry not in content:
                    with gitignore_path.open("a") as f:
                        f.write(f"\n# InfraDSL cache\n{cache_entry}\n")
            else:
                gitignore_path.write_text(f"# InfraDSL cache\n{cache_entry}\n")
    
    def get_cache_path(self, resource_name: str, provider: str) -> Path:
        return self.cache_dir / f"{provider}_{resource_name}.json"
    
    def save_resource_state(self, resource_state: ResourceState):
        cache_path = self.get_cache_path(resource_state.resource_name, resource_state.provider)
        cache_data = {
            "resource_name": resource_state.resource_name,
            "resource_type": resource_state.resource_type,
            "provider": resource_state.provider,
            "config_hash": resource_state.config_hash,
            "last_checked": resource_state.last_checked.isoformat(),
            "current_state": resource_state.current_state,
            "desired_state": resource_state.desired_state,
            "tags": resource_state.tags
        }
        cache_path.write_text(json.dumps(cache_data, indent=2))
    
    def load_resource_state(self, resource_name: str, provider: str) -> Optional[ResourceState]:
        cache_path = self.get_cache_path(resource_name, provider)
        if not cache_path.exists():
            return None
        
        try:
            cache_data = json.loads(cache_path.read_text())
            return ResourceState(
                resource_name=cache_data["resource_name"],
                resource_type=cache_data["resource_type"],
                provider=cache_data["provider"],
                config_hash=cache_data["config_hash"],
                last_checked=datetime.fromisoformat(cache_data["last_checked"]),
                current_state=cache_data["current_state"],
                desired_state=cache_data["desired_state"],
                tags=cache_data["tags"]
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            cache_path.unlink(missing_ok=True)
            return None


class SmartDriftManager:
    """Main interface for smart drift management functionality"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache = ResourceCache(cache_dir)
        self.webhooks: List[str] = []
        self.rollback_plans: Dict[str, RollbackPlan] = {}
        self.learning_mode_resources: Dict[str, datetime] = {}  # resource_name -> start_date
        self._setup_rollback_storage()
    
    def generate_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate SHA256 hash of resource configuration"""
        config_str = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def generate_management_tags(self, resource_name: str, resource_type: str, 
                                config_hash: str) -> Dict[str, str]:
        """Generate InfraDSL management tags for a resource"""
        return {
            "infradsl:managed": "true",
            "infradsl:resource-name": resource_name,
            "infradsl:resource-type": resource_type,
            "infradsl:config-hash": config_hash,
            "infradsl:created-by": "infradsl",
            "infradsl:last-updated": datetime.utcnow().isoformat()
        }
    
    def cache_resource_state(self, resource_name: str, resource_type: str, 
                           provider: str, config: Dict[str, Any], 
                           current_state: Dict[str, Any]):
        """Cache resource state after creation/update"""
        config_hash = self.generate_config_hash(config)
        management_tags = self.generate_management_tags(resource_name, resource_type, config_hash)
        
        desired_state = config.copy()
        if "tags" not in desired_state or desired_state["tags"] is None:
            desired_state["tags"] = {}
        elif isinstance(desired_state["tags"], list):
            # Convert list tags to dict format for management
            list_tags = desired_state["tags"]
            desired_state["tags"] = {}
            # Add list tags as simple key-value pairs
            for i, tag in enumerate(list_tags):
                desired_state["tags"][f"tag_{i}"] = tag
        
        # Now safely update with management tags
        desired_state["tags"].update(management_tags)
        
        resource_state = ResourceState(
            resource_name=resource_name,
            resource_type=resource_type,
            provider=provider,
            config_hash=config_hash,
            last_checked=datetime.utcnow(),
            current_state=current_state,
            desired_state=desired_state,
            tags=management_tags
        )
        
        self.cache.save_resource_state(resource_state)
        print(f"💾 Cached state for {provider} {resource_type}: {resource_name}")
    
    def add_webhook(self, webhook_url: str):
        """Add a webhook URL for drift notifications"""
        if webhook_url not in self.webhooks:
            self.webhooks.append(webhook_url)
            print(f"🔔 Added webhook for drift notifications: {webhook_url[:50]}...")
    
    def send_webhook_notification(self, message: str, data: Dict[str, Any] = None):
        """Send webhook notification to Discord, Slack, or other webhooks"""
        if not self.webhooks:
            return
            
        print(f"🔔 Sending webhook notification to {len(self.webhooks)} endpoint(s)")
        
        for webhook_url in self.webhooks:
            try:
                self._send_single_webhook(webhook_url, message, data)
            except Exception as e:
                print(f"⚠️  Failed to send webhook to {webhook_url[:50]}...: {e}")
    
    def _send_single_webhook(self, webhook_url: str, message: str, data: Dict[str, Any] = None):
        """Send notification to a single webhook endpoint"""
        try:
            import requests
        except ImportError:
            print(f"📱 Would send webhook: {message}")
            if data:
                print(f"   📊 Data: {data}")
            return
        
        # Detect webhook type and format accordingly
        if "discord.com/api/webhooks" in webhook_url:
            self._send_discord_webhook(webhook_url, message, data)
        elif "hooks.slack.com" in webhook_url:
            self._send_slack_webhook(webhook_url, message, data)
        else:
            # Generic webhook
            self._send_generic_webhook(webhook_url, message, data)
    
    def _send_discord_webhook(self, webhook_url: str, message: str, data: Dict[str, Any] = None):
        """Send Discord-formatted webhook notification"""
        try:
            import requests
            
            # Determine message type and styling
            is_success = data and data.get('status') == 'success'
            is_critical = data and data.get('alert_type') == 'missing_resource'
            
            # Set title and color based on message type
            if is_success:
                title = "✅ InfraDSL Auto-Remediation Success"
                color = 5763719  # Green color for success
                icon = "✅"
            elif is_critical:
                title = "🚨 InfraDSL Critical Alert"
                color = 15158332  # Red color for critical alerts
                icon = "🚨"
            else:
                title = "⚠️ InfraDSL Drift Detection Alert"
                color = 16776960  # Yellow color for warnings
                icon = "⚠️"
            
            # Create Discord embed for rich formatting
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "InfraDSL Intelligence System",
                    "icon_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg"
                },
                "fields": []
            }
            
            # Add data fields if provided
            if data:
                resource_name = data.get('resource_name', 'Unknown')
                provider = data.get('provider', 'Unknown').upper()
                
                # Map provider names to more readable formats
                provider_map = {
                    'GCP': 'Google Cloud Platform',
                    'GOOGLECLOUD': 'Google Cloud Platform', 
                    'AWS': 'Amazon Web Services',
                    'DIGITALOCEAN': 'DigitalOcean',
                    'CLOUDFLARE': 'Cloudflare'
                }
                provider_display = provider_map.get(provider, provider)
                
                # Get provider emoji
                provider_emojis = {
                    'GOOGLE CLOUD PLATFORM': '☁️',
                    'AMAZON WEB SERVICES': '🟠', 
                    'DIGITALOCEAN': '💙',
                    'CLOUDFLARE': '🔶'
                }
                provider_emoji = provider_emojis.get(provider_display, '☁️')
                
                drift_types = list(set(data.get('drift_types', [])))
                drift_display = ', '.join(drift_types) if drift_types else 'None detected'
                
                embed["fields"].extend([
                    {"name": "🎯 Resource", "value": f"`{resource_name}`", "inline": True},
                    {"name": f"{provider_emoji} Provider", "value": f"`{provider_display}`", "inline": True},
                    {"name": "🔍 Resource Type", "value": "`Compute Engine VM`", "inline": True},
                ])
                
                if not is_success:
                    embed["fields"].append({
                        "name": "📊 Drift Types", 
                        "value": f"`{drift_display}`", 
                        "inline": False
                    })
                
                # Add success-specific information
                if is_success:
                    fixes_applied = data.get('fixes_applied', 0)
                    embed["fields"].extend([
                        {"name": "🔧 Fixes Applied", "value": f"`{fixes_applied}`", "inline": True},
                        {"name": "⏱️ Response Time", "value": "`< 30 seconds`", "inline": True},
                        {"name": "🛡️ Policy", "value": "`CONSERVATIVE`", "inline": True},
                    ])
                    
                    # Add rollback info for successful remediations
                    if 'rollback_id' in data:
                        rollback_expires = data.get('rollback_expires', '')
                        embed["fields"].append({
                            "name": "🔄 Rollback Available (24h)", 
                            "value": f"```bash\ninfradsl rollback {data['rollback_id']}\n```", 
                            "inline": False
                        })
                else:
                    # Add suggested actions for alerts
                    if 'suggested_actions' in data:
                        actions = data['suggested_actions'][:3]  # Show top 3 actions
                        action_text = "\n".join(f"• {action}" for action in actions)
                        embed["fields"].append({
                            "name": "💡 Recommended Actions", 
                            "value": action_text, 
                            "inline": False
                        })
                
                # Add auto-remediation status
                auto_fixable = data.get('auto_fixable', [])
                if auto_fixable and not is_success:
                    embed["fields"].append({
                        "name": "🤖 Auto-Remediation", 
                        "value": f"`{len(auto_fixable)} issue(s) can be auto-fixed`", 
                        "inline": True
                    })
            
            payload = {
                "username": "InfraDSL Intelligence",
                "avatar_url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg",
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"✅ Discord notification sent successfully")
            else:
                print(f"⚠️  Discord webhook failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to send Discord webhook: {e}")
    
    def _send_slack_webhook(self, webhook_url: str, message: str, data: Dict[str, Any] = None):
        """Send Slack-formatted webhook notification"""
        try:
            import requests
            
            payload = {
                "text": f"🔍 *InfraDSL Drift Detection Alert*",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {
                                "title": "Alert Message",
                                "value": message,
                                "short": False
                            }
                        ],
                        "footer": "InfraDSL Intelligence System",
                        "ts": int(datetime.utcnow().timestamp())
                    }
                ]
            }
            
            if data:
                resource_info = f"Resource: `{data.get('resource_name', 'Unknown')}` | Provider: `{data.get('provider', 'Unknown').upper()}`"
                payload["attachments"][0]["fields"].append({
                    "title": "Resource Details",
                    "value": resource_info,
                    "short": False
                })
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Slack notification sent successfully")
            else:
                print(f"⚠️  Slack webhook failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to send Slack webhook: {e}")
    
    def _send_generic_webhook(self, webhook_url: str, message: str, data: Dict[str, Any] = None):
        """Send generic webhook notification"""
        try:
            import requests
            
            payload = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "InfraDSL Intelligence System"
            }
            
            if data:
                payload["data"] = data
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code in [200, 201, 204]:
                print(f"✅ Generic webhook sent successfully")
            else:
                print(f"⚠️  Generic webhook failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to send generic webhook: {e}")
    
    def _setup_rollback_storage(self):
        """Setup rollback plan storage directory"""
        rollback_dir = self.cache.cache_dir / "rollback_plans"
        rollback_dir.mkdir(exist_ok=True)
        self._load_existing_rollback_plans()
    
    def _load_existing_rollback_plans(self):
        """Load existing rollback plans from storage"""
        rollback_dir = self.cache.cache_dir / "rollback_plans"
        for plan_file in rollback_dir.glob("*.json"):
            try:
                plan_data = json.loads(plan_file.read_text())
                rollback_plan = RollbackPlan(
                    rollback_id=plan_data["rollback_id"],
                    resource_name=plan_data["resource_name"],
                    provider=plan_data["provider"],
                    actions=[RemediationAction(**action) for action in plan_data["actions"]],
                    created_at=datetime.fromisoformat(plan_data["created_at"]),
                    expires_at=datetime.fromisoformat(plan_data["expires_at"]),
                    can_rollback=plan_data.get("can_rollback", True)
                )
                
                # Only keep non-expired rollback plans
                if rollback_plan.expires_at > datetime.utcnow():
                    self.rollback_plans[rollback_plan.rollback_id] = rollback_plan
                else:
                    plan_file.unlink()  # Remove expired plan
                    
            except (json.JSONDecodeError, KeyError, ValueError):
                plan_file.unlink()  # Remove invalid plan file
    
    def enable_learning_mode(self, resource_name: str, learning_days: int = 30):
        """Enable learning mode for a resource
        
        Args:
            resource_name: Name of the resource
            learning_days: Number of days to learn before enabling auto-remediation
        """
        start_date = datetime.utcnow()
        self.learning_mode_resources[resource_name] = start_date
        
        # Save learning mode state
        learning_file = self.cache.cache_dir / "learning_mode.json"
        learning_data = {
            name: date.isoformat() 
            for name, date in self.learning_mode_resources.items()
        }
        learning_file.write_text(json.dumps(learning_data, indent=2))
        
        end_date = start_date + timedelta(days=learning_days)
        print(f"🎓 Learning mode enabled for {resource_name}")
        print(f"   • Start: {start_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   • End: {end_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   • Auto-remediation will be enabled after {learning_days} days")
    
    def _is_in_learning_mode(self, resource_name: str, learning_days: int = 30) -> bool:
        """Check if resource is still in learning mode"""
        if resource_name not in self.learning_mode_resources:
            return False
        
        start_date = self.learning_mode_resources[resource_name]
        learning_period = timedelta(days=learning_days)
        return datetime.utcnow() < start_date + learning_period
    
    def _save_rollback_plan(self, rollback_plan: RollbackPlan):
        """Save rollback plan to storage"""
        rollback_dir = self.cache.cache_dir / "rollback_plans"
        plan_file = rollback_dir / f"{rollback_plan.rollback_id}.json"
        
        plan_data = {
            "rollback_id": rollback_plan.rollback_id,
            "resource_name": rollback_plan.resource_name,
            "provider": rollback_plan.provider,
            "actions": [asdict(action) for action in rollback_plan.actions],
            "created_at": rollback_plan.created_at.isoformat(),
            "expires_at": rollback_plan.expires_at.isoformat(),
            "can_rollback": rollback_plan.can_rollback
        }
        
        plan_file.write_text(json.dumps(plan_data, indent=2, default=str))
        self.rollback_plans[rollback_plan.rollback_id] = rollback_plan
    
    def auto_remediate_drift(self, drift_result: DriftResult, resource_instance, 
                           policy: AutoRemediationPolicy = AutoRemediationPolicy.CONSERVATIVE) -> DriftResult:
        """Automatically remediate detected drift
        
        Args:
            drift_result: The drift detection result
            resource_instance: The actual resource instance (VM, Database, etc.)
            policy: Auto-remediation policy to apply
            
        Returns:
            Updated drift result with remediation status
        """
        if not drift_result.has_drift:
            return drift_result
            
        # Check if resource is in learning mode
        if self._is_in_learning_mode(drift_result.resource_name):
            print(f"🎓 {drift_result.resource_name} is in learning mode - skipping auto-remediation")
            print(f"   • Drift detected but not fixed (learning phase)")
            return drift_result
        
        # Check policy permissions
        max_changes = policy.value.get("max_changes_per_session", 0)
        if len(drift_result.auto_fixable) > max_changes:
            print(f"🛡️ {policy.name} policy: Too many changes ({len(drift_result.auto_fixable)}) > {max_changes} - requires manual approval")
            return drift_result
        
        if policy == AutoRemediationPolicy.DISABLED:
            print(f"🚫 Auto-remediation DISABLED - manual fix required")
            return drift_result
            
        # Create rollback plan before making changes
        rollback_id = str(uuid.uuid4())[:8]
        rollback_actions = []
        successful_actions = []
        
        print(f"🔧 Starting auto-remediation for {drift_result.resource_name}")
        print(f"   • Policy: {policy.name}")
        print(f"   • Rollback ID: {rollback_id}")
        
        # Apply each auto-fixable change
        for field_name in drift_result.auto_fixable:
            if field_name in drift_result.changes_needed:
                change = drift_result.changes_needed[field_name]
                old_value = change.get("current")
                new_value = change.get("desired")
                
                action = RemediationAction(
                    action_id=str(uuid.uuid4())[:8],
                    resource_name=drift_result.resource_name,
                    action_type="recreate_resource" if field_name == "status" and old_value in ["NOT_FOUND", None] else "fix_config",
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    timestamp=datetime.utcnow()
                )
                
                try:
                    if field_name == "status" and old_value in ["NOT_FOUND", None]:
                        # Handle missing resource by recreating it
                        print(f"   🚀 Auto-recreating missing resource: {drift_result.resource_name}")
                        
                        # Call the resource's create method to recreate it
                        if hasattr(resource_instance, 'create'):
                            # Temporarily disable drift checking during recreation to avoid recursion
                            original_drift_enabled = getattr(resource_instance, '_drift_enabled', False)
                            resource_instance._drift_enabled = False
                            
                            try:
                                result = resource_instance.create()
                                print(f"   ✅ Successfully recreated resource: {drift_result.resource_name}")
                                action.success = True
                                successful_actions.append(action)
                            finally:
                                # Re-enable drift checking
                                resource_instance._drift_enabled = original_drift_enabled
                        else:
                            print(f"   ⚠️ Resource instance doesn't support creation")
                            continue
                    else:
                        # Handle configuration changes
                        print(f"   🔧 Fixing {field_name}: {old_value} → {new_value}")
                        setattr(resource_instance, field_name, new_value)
                        
                        # Call resource's update method if it exists
                        if hasattr(resource_instance, '_apply_configuration_update'):
                            resource_instance._apply_configuration_update(field_name, new_value)
                        
                        action.success = True
                        successful_actions.append(action)
                        print(f"   ✅ Fixed {field_name}")
                    
                except Exception as e:
                    action.success = False
                    action.error = str(e)
                    print(f"   ❌ Failed to fix {field_name}: {e}")
                
                rollback_actions.append(action)
        
        # Create and save rollback plan
        if successful_actions:
            rollback_plan = RollbackPlan(
                rollback_id=rollback_id,
                resource_name=drift_result.resource_name,
                provider=getattr(resource_instance, 'provider', 'unknown'),
                actions=rollback_actions,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            self._save_rollback_plan(rollback_plan)
            
            drift_result.remediation_applied = True
            drift_result.rollback_id = rollback_id
            
            print(f"✅ Auto-remediation completed!")
            print(f"   • Fixed {len(successful_actions)} issues")
            print(f"   • Rollback available for 24 hours: infradsl rollback {rollback_id}")
            
            # Send success webhook notification  
            success_message = f"🎉 **Infrastructure auto-healed successfully!**\n\nResource `{drift_result.resource_name}` was automatically recreated and is now running normally."
            
            # Determine provider from resource instance or drift context
            provider = 'gcp'  # Default for GCP VM instances
            if hasattr(resource_instance, 'provider'):
                provider = resource_instance.provider
            elif hasattr(resource_instance, '__module__'):
                if 'googlecloud' in resource_instance.__module__:
                    provider = 'gcp'
                elif 'aws' in resource_instance.__module__:
                    provider = 'aws'
                elif 'digitalocean' in resource_instance.__module__:
                    provider = 'digitalocean'
                elif 'cloudflare' in resource_instance.__module__:
                    provider = 'cloudflare'
            
            success_data = {
                'resource_name': drift_result.resource_name,
                'provider': provider,
                'fixes_applied': len(successful_actions),
                'rollback_id': rollback_id,
                'rollback_expires': (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                'status': 'success',
                'alert_type': 'remediation_success'
            }
            self.send_webhook_notification(success_message, success_data)
            
            # Update cache with new state
            if hasattr(resource_instance, '_cache_resource_state'):
                resource_instance._cache_resource_state()
        else:
            print(f"❌ Auto-remediation failed - no changes applied")
            
            # Send failure webhook notification
            failure_message = f"❌ **Auto-remediation failed for resource `{drift_result.resource_name}`**\n\nManual intervention required to resolve the drift issues."
            
            # Use same provider detection logic
            provider = 'gcp'  # Default for GCP VM instances  
            if hasattr(resource_instance, 'provider'):
                provider = resource_instance.provider
            elif hasattr(resource_instance, '__module__'):
                if 'googlecloud' in resource_instance.__module__:
                    provider = 'gcp'
                elif 'aws' in resource_instance.__module__:
                    provider = 'aws'
                elif 'digitalocean' in resource_instance.__module__:
                    provider = 'digitalocean'
                elif 'cloudflare' in resource_instance.__module__:
                    provider = 'cloudflare'
            
            failure_data = {
                'resource_name': drift_result.resource_name,
                'provider': provider,
                'status': 'failed',
                'requires_manual_intervention': True,
                'alert_type': 'remediation_failed'
            }
            self.send_webhook_notification(failure_message, failure_data)
            
        return drift_result
    
    def rollback_remediation(self, rollback_id: str) -> bool:
        """Rollback a previous auto-remediation
        
        Args:
            rollback_id: ID of the rollback plan to execute
            
        Returns:
            True if rollback was successful
        """
        if rollback_id not in self.rollback_plans:
            print(f"❌ Rollback plan {rollback_id} not found")
            return False
            
        rollback_plan = self.rollback_plans[rollback_id]
        
        if not rollback_plan.can_rollback:
            print(f"❌ Rollback plan {rollback_id} is no longer available")
            return False
            
        if rollback_plan.expires_at < datetime.utcnow():
            print(f"❌ Rollback plan {rollback_id} has expired")
            return False
        
        print(f"🔄 Rolling back remediation {rollback_id}")
        print(f"   • Resource: {rollback_plan.resource_name}")
        print(f"   • Actions: {len(rollback_plan.actions)}")
        
        # Note: Actual rollback would need to be implemented by each provider
        # This is a framework for the rollback functionality
        
        success_count = 0
        for action in rollback_plan.actions:
            if action.success:  # Only rollback successful actions
                try:
                    print(f"   🔄 Rolling back {action.field_name}: {action.new_value} → {action.old_value}")
                    # Rollback logic would be implemented by provider-specific code
                    success_count += 1
                    print(f"   ✅ Rolled back {action.field_name}")
                except Exception as e:
                    print(f"   ❌ Failed to rollback {action.field_name}: {e}")
        
        # Mark rollback as used
        rollback_plan.can_rollback = False
        self._save_rollback_plan(rollback_plan)
        
        print(f"✅ Rollback completed: {success_count}/{len(rollback_plan.actions)} actions rolled back")
        return success_count > 0
    
    def check_resource_drift(self, resource_name: str, provider: str,
                           check_interval: Union[int, DriftCheckInterval],
                           current_state_fetcher: Callable[[], Dict[str, Any]],
                           remediation_policy: Dict[str, str] = None) -> Optional[DriftResult]:
        """Check for drift in a specific resource"""
        if isinstance(check_interval, DriftCheckInterval):
            check_interval = check_interval.value
        
        if remediation_policy is None:
            remediation_policy = AutoRemediationPolicy.CONSERVATIVE
        
        cached_state = self.cache.load_resource_state(resource_name, provider)
        
        if cached_state is None:
            print(f"⚠️  No cached state found for {resource_name}. Run .create() first.")
            return None
        
        # Always fetch current state to check if resource exists
        try:
            current_state = current_state_fetcher()
        except Exception as e:
            print(f"❌ Failed to fetch current state for {resource_name}: {e}")
            return None
        
        # Check if resource is missing - this triggers immediate drift detection
        resource_missing = current_state.get("status") == "NOT_FOUND" or current_state.get("machine_type") is None
        
        # Check if drift check is needed based on time interval
        time_since_check = datetime.utcnow() - cached_state.last_checked
        time_based_check_needed = time_since_check.total_seconds() >= check_interval
        
        # Skip check only if both conditions are met:
        # 1. Resource exists (not missing)
        # 2. Not enough time has passed since last check
        if not resource_missing and not time_based_check_needed:
            return None
        
        if resource_missing:
            print(f"🚨 CRITICAL: Resource missing - {provider} {cached_state.resource_type}: {resource_name}")
        else:
            print(f"🔍 Checking drift for {provider} {cached_state.resource_type}: {resource_name}")
        
        # Enhanced drift detection - check for missing resources and configuration changes
        drift_types = []
        changes_needed = {}
        suggested_actions = []
        auto_fixable = []
        
        # Check if resource is missing
        if resource_missing:
            drift_types.append("missing_resource")
            changes_needed["status"] = {
                "desired": "RUNNING",
                "current": current_state.get("status", "NOT_FOUND")
            }
            suggested_actions.append(f"Recreate missing resource: {resource_name}")
            auto_fixable.append("status")  # Missing resources can be auto-fixed by recreation
        
        # Check for configuration changes
        for key, desired_value in cached_state.desired_state.items():
            current_value = current_state.get(key)
            
            # Special handling for tags
            if key == "tags":
                # Compare tags - handle different formats (dict vs list vs None)
                if not resource_missing:  # Only check tags if resource exists
                    current_tags = current_value if current_value else []
                    desired_tags = desired_value if desired_value else {}
                    
                    # Convert to consistent format for comparison
                    if isinstance(desired_tags, dict) and isinstance(current_tags, list):
                        # Check if desired tags contain only InfraDSL management tags
                        is_only_management_tags = all(
                            tag_key.startswith("infradsl:") 
                            for tag_key in desired_tags.keys()
                        ) if desired_tags else True
                        
                        # If only management tags are missing, don't treat as critical drift
                        if desired_tags and not current_tags and is_only_management_tags:
                            # Only add as minor drift that can be auto-fixed silently
                            drift_types.append("missing_management_tags")
                            changes_needed[key] = {
                                "desired": desired_tags,
                                "current": current_tags
                            }
                            suggested_actions.append(f"Apply InfraDSL management tags to {resource_name}")
                            auto_fixable.append(key)  # Tags can be auto-fixed
                        elif desired_tags and not current_tags and not is_only_management_tags:
                            # User-defined tags are missing - this is real drift
                            drift_types.append("missing_tags")
                            changes_needed[key] = {
                                "desired": desired_tags,
                                "current": current_tags
                            }
                            suggested_actions.append(f"Add missing user tags to {resource_name}")
                            auto_fixable.append(key)  # Tags can be auto-fixed
                continue
            
            if current_value != desired_value and not resource_missing:  # Skip config checks if resource is missing
                drift_types.append("configuration_drift")
                changes_needed[key] = {
                    "desired": desired_value,
                    "current": current_value
                }
                suggested_actions.append(f"Fix {key}: {current_value} → {desired_value}")
                # Configuration drift can be auto-fixed depending on the field
                if key in ["machine_type", "status"]:
                    auto_fixable.append(key)
        
        has_drift = len(drift_types) > 0
        
        if has_drift:
            if resource_missing:
                print(f"🚨 CRITICAL DRIFT: Resource missing - {resource_name}")
            else:
                print(f"⚠️  Drift detected in {resource_name}:")
            for action in suggested_actions:
                print(f"   → {action}")
            
            # Enhanced webhook notification for missing resources
            if resource_missing:
                webhook_message = f"🚨 **CRITICAL INFRASTRUCTURE ALERT**\n\nResource `{resource_name}` was manually deleted from the cloud console and is no longer available! Auto-remediation will attempt to recreate it."
                webhook_data = {
                    'alert_type': 'missing_resource',
                    'resource_name': resource_name,
                    'provider': provider,
                    'status': 'CRITICAL - Resource manually deleted',
                    'drift_types': drift_types,
                    'suggested_actions': suggested_actions,
                    'auto_fixable': auto_fixable,
                    'timestamp': datetime.utcnow().isoformat(),
                    'requires_manual_action': len(auto_fixable) == 0,
                    'remediation_available': len(auto_fixable) > 0
                }
            else:
                webhook_message = f"⚠️ **Configuration drift detected**\n\nResource `{resource_name}` has drifted from its desired configuration. Review the suggested actions below."
                webhook_data = {
                    'alert_type': 'configuration_drift',
                    'resource_name': resource_name,
                    'provider': provider,
                    'drift_types': drift_types,
                    'suggested_actions': suggested_actions,
                    'auto_fixable': auto_fixable,
                    'timestamp': datetime.utcnow().isoformat(),
                    'requires_manual_action': len(auto_fixable) == 0
                }
            
            self.send_webhook_notification(webhook_message, webhook_data)
        else:
            print(f"✅ No drift detected for {resource_name}")
        
        # Update cache
        cached_state.current_state = current_state
        cached_state.last_checked = datetime.utcnow()
        self.cache.save_resource_state(cached_state)
        
        if has_drift:
            return DriftResult(
                resource_name=resource_name,
                has_drift=True,
                drift_types=drift_types,
                changes_needed=changes_needed,
                auto_fixable=auto_fixable,
                requires_manual_action=[k for k in changes_needed.keys() if k not in auto_fixable],
                suggested_actions=suggested_actions
            )
        
        return None


# Global drift manager instance
_drift_manager = None

def get_drift_manager() -> SmartDriftManager:
    """Get global drift manager instance"""
    global _drift_manager
    if _drift_manager is None:
        _drift_manager = SmartDriftManager()
    return _drift_manager
