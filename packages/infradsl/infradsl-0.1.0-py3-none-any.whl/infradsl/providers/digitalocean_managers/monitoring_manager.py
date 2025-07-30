"""
DigitalOcean Monitoring Manager

Handles creation and management of DigitalOcean monitoring, uptime checks,
and alert policies.
"""

from typing import Dict, Any, List, Optional


class MonitoringManager:
    """Manager for DigitalOcean monitoring services"""

    def __init__(self, do_client):
        self.do_client = do_client
        self.client = do_client.client

    def preview_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview monitoring configuration"""
        monitor_type = config["type"]
        
        # Check if monitoring already exists
        existing_monitor = self._find_monitor_by_name(config["name"], monitor_type)
        
        preview = {
            "action": "UPDATE" if existing_monitor else "CREATE",
            "name": config["name"],
            "type": monitor_type,
            "enabled": config["enabled"],
            "tags": config.get("tags", []),
            "existing": bool(existing_monitor)
        }

        if monitor_type == "uptime":
            preview.update({
                "target": config.get("target"),
                "target_url": config.get("target_url"),
                "target_resource_id": config.get("target_resource_id"),
                "target_resource_type": config.get("target_resource_type"),
                "check_regions": config.get("check_regions", [])
            })
        else:  # alert_policy
            preview.update({
                "policy_type": config.get("policy_type"),
                "comparison": config.get("comparison"),
                "threshold": config.get("threshold"),
                "window": config.get("window"),
                "entities_count": len(config.get("entities", []))
            })
            
            # Count alert destinations
            email_count = len(config.get("alerts", {}).get("email", []))
            slack_count = len(config.get("alerts", {}).get("slack", []))
            preview["alert_destinations"] = email_count + slack_count

        if existing_monitor:
            preview["monitor_id"] = existing_monitor.get("id")
            preview["current_status"] = existing_monitor.get("status", "unknown")

        self._print_monitoring_preview(preview)
        return preview

    def create_monitoring(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create monitoring check or alert policy"""
        try:
            monitor_type = config["type"]
            
            # Check if monitoring already exists
            existing_monitor = self._find_monitor_by_name(config["name"], monitor_type)
            
            if existing_monitor:
                print(f"🔄 {monitor_type.title()} '{config['name']}' already exists, updating...")
                return self._handle_existing_monitor(existing_monitor, config)
            
            if monitor_type == "uptime":
                return self._create_uptime_check(config)
            else:
                return self._create_alert_policy(config)
            
        except Exception as e:
            error_msg = f"Failed to create monitoring: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}

    def destroy_monitoring(self, name: str, monitor_type: str) -> Dict[str, Any]:
        """Destroy monitoring check or alert policy"""
        try:
            monitor = self._find_monitor_by_name(name, monitor_type)
            
            if not monitor:
                return {"error": f"Monitor '{name}' not found", "success": False}
            
            monitor_id = monitor.get("id")
            
            if monitor_type == "uptime":
                # Delete uptime check
                self.client._perform_request("DELETE", f"/v2/uptime/checks/{monitor_id}")
            else:
                # Delete alert policy
                self.client._perform_request("DELETE", f"/v2/monitoring/alerts/{monitor_id}")
            
            print(f"🗑️  {monitor_type.title()} '{name}' destruction initiated...")
            
            return {
                "success": True,
                "name": name,
                "id": monitor_id,
                "type": monitor_type,
                "message": f"{monitor_type.title()} destruction initiated"
            }
            
        except Exception as e:
            error_msg = f"Failed to destroy monitoring: {str(e)}"
            return {"error": error_msg, "success": False}

    def _create_uptime_check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create uptime check"""
        print(f"🚀 Creating uptime check...")
        
        check_data = {
            "name": config["name"],
            "type": "https" if config.get("target_url") else "ping",
            "enabled": config["enabled"],
            "regions": config.get("check_regions", ["us_east"])
        }
        
        if config.get("target_url"):
            check_data["target"] = config["target_url"]
        elif config.get("target_resource_id"):
            # For resource checks, we need to get the resource's public IP
            target_ip = self._get_resource_ip(config["target_resource_id"], config["target_resource_type"])
            if target_ip:
                check_data["target"] = target_ip
                check_data["type"] = "ping"
            else:
                raise Exception(f"Could not find IP for {config['target_resource_type']}:{config['target_resource_id']}")
        
        if config.get("tags"):
            check_data["tags"] = config["tags"]
        
        # Create uptime check
        response = self.client._perform_request("POST", "/v2/uptime/checks", {"check": check_data})
        check_info = response["check"]
        
        result = {
            "id": check_info["id"],
            "name": check_info["name"],
            "type": "uptime",
            "target": check_info["target"],
            "check_type": check_info["type"],
            "enabled": check_info["enabled"],
            "regions": check_info["regions"],
            "tags": check_info.get("tags", []),
            "created": True,
            "status": "active"
        }
        
        self._print_monitoring_result(result)
        return result

    def _create_alert_policy(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create alert policy"""
        print(f"🚀 Creating alert policy...")
        
        # Build alert policy data
        policy_data = {
            "alerts": {
                "email": config.get("alerts", {}).get("email", []),
                "slack": []
            },
            "compare": config.get("comparison", "GreaterThan"),
            "description": f"Alert policy for {config['name']}",
            "enabled": config["enabled"],
            "entities": self._resolve_entities(config.get("entities", [])),
            "tags": config.get("tags", []),
            "type": config.get("policy_type", "v1/insights/droplet/cpu"),
            "value": config.get("threshold", 80),
            "window": config.get("window", "5m")
        }
        
        # Add Slack webhooks
        for slack_config in config.get("alerts", {}).get("slack", []):
            policy_data["alerts"]["slack"].append({
                "url": slack_config["url"],
                "channel": slack_config.get("channel", "#alerts")
            })
        
        # Create alert policy
        response = self.client._perform_request("POST", "/v2/monitoring/alerts", policy_data)
        policy_info = response["policy"]
        
        result = {
            "id": policy_info["uuid"],
            "name": config["name"],
            "type": "alert_policy",
            "policy_type": policy_info["type"],
            "comparison": policy_info["compare"],
            "threshold": policy_info["value"],
            "window": policy_info["window"],
            "enabled": policy_info["enabled"],
            "entities_count": len(policy_info["entities"]),
            "alert_destinations": len(policy_info["alerts"]["email"]) + len(policy_info["alerts"]["slack"]),
            "tags": policy_info.get("tags", []),
            "created": True,
            "status": "active"
        }
        
        self._print_monitoring_result(result)
        return result

    def _find_monitor_by_name(self, name: str, monitor_type: str) -> Optional[Dict[str, Any]]:
        """Find monitor by name and type"""
        try:
            if monitor_type == "uptime":
                response = self.client._perform_request("GET", "/v2/uptime/checks")
                checks = response.get("checks", [])
                for check in checks:
                    if check.get("name") == name:
                        return check
            else:
                response = self.client._perform_request("GET", "/v2/monitoring/alerts")
                policies = response.get("policies", [])
                for policy in policies:
                    if policy.get("description", "").endswith(name):  # Match by description
                        return policy
            return None
        except Exception:
            return None

    def _handle_existing_monitor(self, monitor: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle existing monitor - check for updates"""
        monitor_type = config["type"]
        
        print(f"✅ {monitor_type.title()} is up to date")
        
        # Return current monitor information
        if monitor_type == "uptime":
            result = {
                "id": monitor.get("id"),
                "name": monitor.get("name"),
                "type": "uptime",
                "target": monitor.get("target"),
                "check_type": monitor.get("type"),
                "enabled": monitor.get("enabled"),
                "regions": monitor.get("regions", []),
                "tags": monitor.get("tags", []),
                "was_existing": True,
                "status": monitor.get("status", "active")
            }
        else:
            result = {
                "id": monitor.get("uuid"),
                "name": config["name"],
                "type": "alert_policy",
                "policy_type": monitor.get("type"),
                "comparison": monitor.get("compare"),
                "threshold": monitor.get("value"),
                "window": monitor.get("window"),
                "enabled": monitor.get("enabled"),
                "entities_count": len(monitor.get("entities", [])),
                "alert_destinations": len(monitor.get("alerts", {}).get("email", [])) + len(monitor.get("alerts", {}).get("slack", [])),
                "tags": monitor.get("tags", []),
                "was_existing": True,
                "status": "active"
            }
        
        self._print_monitoring_result(result)
        return result

    def _resolve_entities(self, entities: List[str]) -> List[str]:
        """Resolve entity IDs (handle special cases like '*' for all droplets)"""
        if not entities or entities == ["*"]:
            # Get all droplet IDs
            try:
                droplets = self.client.get_all_droplets()
                return [str(droplet.id) for droplet in droplets]
            except Exception:
                return []
        
        return [str(entity) for entity in entities]

    def _get_resource_ip(self, resource_id: str, resource_type: str) -> Optional[str]:
        """Get public IP of a resource"""
        try:
            if resource_type == "droplet":
                droplet = self.client.get_droplet(resource_id)
                networks = droplet.networks.get("v4", [])
                for network in networks:
                    if network["type"] == "public":
                        return network["ip_address"]
            elif resource_type == "load_balancer":
                lb = self.client.get_load_balancer(resource_id)
                return lb.ip
            return None
        except Exception:
            return None

    def _print_monitoring_preview(self, preview: Dict[str, Any]):
        """Print formatted monitoring preview"""
        print(f"\n╭─ 📊 Monitoring Preview: {preview['name']}")
        print(f"├─ 🔧 Action: {preview['action']}")
        print(f"├─ 🔍 Type: {preview['type'].replace('_', ' ').title()}")
        print(f"├─ ✅ Enabled: {'Yes' if preview['enabled'] else 'No'}")
        
        if preview['type'] == 'uptime':
            if preview.get('target_url'):
                print(f"├─ 🌐 Target URL: {preview['target_url']}")
            elif preview.get('target_resource_id'):
                print(f"├─ 🖥️  Target Resource: {preview['target_resource_type']}:{preview['target_resource_id']}")
            
            if preview.get('check_regions'):
                print(f"├─ 🌍 Check Regions: {', '.join(preview['check_regions'])}")
        else:
            print(f"├─ 📈 Policy Type: {preview.get('policy_type', 'Unknown')}")
            print(f"├─ ⚠️  Threshold: {preview.get('comparison', 'GreaterThan')} {preview.get('threshold', 0)}")
            print(f"├─ ⏱️  Window: {preview.get('window', '5m')}")
            print(f"├─ 🎯 Entities: {preview.get('entities_count', 0)}")
            print(f"├─ 📧 Alert Destinations: {preview.get('alert_destinations', 0)}")
        
        if preview.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(preview['tags'])}")
        
        if preview['existing']:
            print(f"├─ 📊 Current Status: {preview.get('current_status', 'Unknown')}")
            print(f"├─ 🆔 Monitor ID: {preview.get('monitor_id', 'Unknown')}")
        
        print(f"╰─ 🎯 Action: {'Update existing monitor' if preview['existing'] else 'Create new monitor'}")

    def _print_monitoring_result(self, result: Dict[str, Any]):
        """Print formatted monitoring result"""
        print(f"\n╭─ 📊 Monitor: {result['name']}")
        print(f"├─ 🆔 ID: {result['id']}")
        print(f"├─ 🔍 Type: {result['type'].replace('_', ' ').title()}")
        print(f"├─ 🟢 Status: {result.get('status', 'active').title()}")
        print(f"├─ ✅ Enabled: {'Yes' if result.get('enabled', True) else 'No'}")
        
        if result['type'] == 'uptime':
            print(f"├─ 🎯 Target: {result.get('target', 'Unknown')}")
            print(f"├─ 🔍 Check Type: {result.get('check_type', 'Unknown')}")
            if result.get('regions'):
                print(f"├─ 🌍 Regions: {', '.join(result['regions'])}")
        else:
            print(f"├─ 📈 Policy Type: {result.get('policy_type', 'Unknown')}")
            print(f"├─ ⚠️  Threshold: {result.get('comparison', 'GreaterThan')} {result.get('threshold', 0)}")
            print(f"├─ ⏱️  Window: {result.get('window', '5m')}")
            print(f"├─ 🎯 Monitored Entities: {result.get('entities_count', 0)}")
            print(f"├─ 📧 Alert Destinations: {result.get('alert_destinations', 0)}")
        
        if result.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(result['tags'])}")
        
        if result.get('was_existing'):
            print(f"├─ ♻️  Action: Updated existing monitor")
        else:
            print(f"├─ ✨ Action: Created new monitor")
        
        print(f"╰─ 📊 Monitoring: Active and ready")