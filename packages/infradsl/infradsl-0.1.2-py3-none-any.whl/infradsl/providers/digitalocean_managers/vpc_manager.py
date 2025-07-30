"""
DigitalOcean VPC Manager

Handles creation, management, and monitoring of DigitalOcean VPCs (Virtual Private Clouds).
"""

import ipaddress
from typing import Dict, Any, List, Optional


class VPCManager:
    """Manager for DigitalOcean VPCs"""

    def __init__(self, do_client):
        self.do_client = do_client
        self.client = do_client.client

    def preview_vpc(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview VPC configuration without creating it"""
        # Check if VPC already exists
        existing_vpc = self._find_vpc_by_name(config["name"])
        
        # Calculate network information
        network_info = self._calculate_network_info(config["ip_range"])
        
        preview = {
            "action": "UPDATE" if existing_vpc else "CREATE",
            "name": config["name"],
            "region": config["region"],
            "ip_range": config["ip_range"],
            "description": config["description"],
            "tags": config.get("tags", []),
            "existing": bool(existing_vpc),
            "network_info": network_info
        }

        if existing_vpc:
            preview["current_ip_range"] = existing_vpc.ip_range
            preview["current_region"] = existing_vpc.region
            preview["vpc_id"] = existing_vpc.id

        self._print_vpc_preview(preview)
        return preview

    def create_vpc(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update VPC"""
        try:
            # Check if VPC already exists
            existing_vpc = self._find_vpc_by_name(config["name"])
            
            if existing_vpc:
                print(f"🔄 VPC '{config['name']}' already exists, checking configuration...")
                return self._handle_existing_vpc(existing_vpc, config)
            
            # Create new VPC
            print(f"🚀 Creating new VPC...")
            
            vpc_params = {
                "name": config["name"],
                "region": config["region"],
                "ip_range": config["ip_range"],
                "description": config["description"]
            }
            
            # Add tags if provided
            if config.get("tags"):
                vpc_params["tags"] = config["tags"]
            
            # Create VPC using DigitalOcean API
            vpc_data = {
                "name": vpc_params["name"],
                "region": vpc_params["region"],
                "ip_range": vpc_params["ip_range"],
                "description": vpc_params.get("description", ""),
                "tags": vpc_params.get("tags", [])
            }
            
            response = self.client._perform_request("POST", "/v2/vpcs", {"vpc": vpc_data})
            vpc_info = response["vpc"]
            
            # Calculate network information
            network_info = self._calculate_network_info(config["ip_range"])
            
            result = {
                "id": vpc_info["id"],
                "name": vpc_info["name"],
                "region": vpc_info["region"],
                "ip_range": vpc_info["ip_range"],
                "description": vpc_info.get("description", ""),
                "urn": vpc_info["urn"],
                "default": vpc_info.get("default", False),
                "created_at": vpc_info["created_at"],
                "tags": vpc_info.get("tags", []),
                "network_info": network_info,
                "created": True
            }
            
            self._print_vpc_result(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to create VPC: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}

    def destroy_vpc(self, name: str) -> Dict[str, Any]:
        """Destroy VPC"""
        try:
            vpc = self._find_vpc_by_name(name)
            
            if not vpc:
                return {"error": f"VPC '{name}' not found", "success": False}
            
            # Check if VPC has resources attached
            resources = self._list_vpc_resources(vpc.id)
            if resources:
                print(f"⚠️  VPC contains {len(resources)} resources that must be removed first:")
                for resource in resources[:5]:  # Show first 5
                    print(f"   • {resource.get('type', 'Unknown')}: {resource.get('name', 'Unknown')}")
                if len(resources) > 5:
                    print(f"   • ... and {len(resources) - 5} more")
                
                return {
                    "error": f"VPC contains {len(resources)} resources. Remove them first before destroying VPC.",
                    "success": False,
                    "resources": resources
                }
            
            # Delete the VPC
            vpc.destroy()
            
            print(f"🗑️  VPC '{name}' destruction initiated...")
            
            return {
                "success": True,
                "name": name,
                "id": vpc.id,
                "message": "VPC destruction initiated"
            }
            
        except Exception as e:
            error_msg = f"Failed to destroy VPC: {str(e)}"
            return {"error": error_msg, "success": False}

    def get_vpc_ip_info(self, name: str) -> Dict[str, Any]:
        """Get IP address information for VPC"""
        try:
            vpc = self._find_vpc_by_name(name)
            
            if not vpc:
                return {"error": f"VPC '{name}' not found", "success": False}
            
            network_info = self._calculate_network_info(vpc.ip_range)
            
            # Get current resource count
            resources = self._list_vpc_resources(vpc.id)
            resource_count = len(resources) if resources else 0
            
            return {
                "success": True,
                "vpc_id": vpc.id,
                "vpc_name": vpc.name,
                "ip_range": vpc.ip_range,
                "network_info": network_info,
                "resources_count": resource_count,
                "available_ips": network_info["total_hosts"] - resource_count
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}

    def list_vpc_resources(self, name: str) -> Dict[str, Any]:
        """List all resources in VPC"""
        try:
            vpc = self._find_vpc_by_name(name)
            
            if not vpc:
                return {"error": f"VPC '{name}' not found", "success": False}
            
            resources = self._list_vpc_resources(vpc.id)
            
            return {
                "success": True,
                "vpc_id": vpc.id,
                "vpc_name": vpc.name,
                "resources": resources,
                "count": len(resources) if resources else 0
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}

    def _find_vpc_by_name(self, name: str):
        """Find VPC by name"""
        try:
            vpcs = self.client.get_all_vpcs()
            for vpc in vpcs:
                if vpc.name == name:
                    return vpc
            return None
        except Exception:
            return None

    def _handle_existing_vpc(self, vpc, config: Dict[str, Any]) -> Dict[str, Any]:
        """Handle existing VPC - check for necessary updates"""
        updates_needed = []
        
        # Check if IP range is different
        if vpc.ip_range != config["ip_range"]:
            updates_needed.append(f"IP Range: {vpc.ip_range} → {config['ip_range']}")
        
        # Check if description is different
        current_desc = getattr(vpc, 'description', '') or ''
        if current_desc != config["description"]:
            updates_needed.append(f"Description: '{current_desc}' → '{config['description']}'")
        
        if updates_needed:
            print(f"🔄 Updates needed:")
            for update in updates_needed:
                print(f"   • {update}")
            print(f"⚠️  VPC updates require manual intervention via DigitalOcean console")
        else:
            print(f"✅ VPC configuration is up to date")
        
        # Calculate network information
        network_info = self._calculate_network_info(vpc.ip_range)
        
        # Return current VPC information
        result = {
            "id": vpc.id,
            "name": vpc.name,
            "region": vpc.region,
            "ip_range": vpc.ip_range,
            "description": getattr(vpc, 'description', ''),
            "urn": vpc.urn,
            "default": getattr(vpc, 'default', False),
            "created_at": vpc.created_at,
            "tags": getattr(vpc, 'tags', []),
            "network_info": network_info,
            "was_existing": True,
            "updates_needed": updates_needed
        }
        
        self._print_vpc_result(result)
        return result

    def _list_vpc_resources(self, vpc_id: str) -> List[Dict[str, Any]]:
        """List resources in VPC"""
        try:
            resources = []
            
            # Check droplets
            try:
                droplets = self.client.get_all_droplets()
                for droplet in droplets:
                    if hasattr(droplet, 'vpc_uuid') and droplet.vpc_uuid == vpc_id:
                        resources.append({
                            "type": "droplet",
                            "id": droplet.id,
                            "name": droplet.name,
                            "status": droplet.status
                        })
            except Exception:
                pass
            
            # Check load balancers
            try:
                load_balancers = self.client.get_all_load_balancers()
                for lb in load_balancers:
                    if hasattr(lb, 'vpc_uuid') and lb.vpc_uuid == vpc_id:
                        resources.append({
                            "type": "load_balancer",
                            "id": lb.id,
                            "name": lb.name,
                            "status": lb.status
                        })
            except Exception:
                pass
            
            # Check databases
            try:
                databases = self.client.get_all_databases()
                for db in databases:
                    if hasattr(db, 'private_network_uuid') and db.private_network_uuid == vpc_id:
                        resources.append({
                            "type": "database",
                            "id": db.id,
                            "name": db.name,
                            "status": db.status
                        })
            except Exception:
                pass
            
            return resources
            
        except Exception:
            return []

    def _calculate_network_info(self, ip_range: str) -> Dict[str, Any]:
        """Calculate network information from CIDR"""
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            
            return {
                "network_address": str(network.network_address),
                "broadcast_address": str(network.broadcast_address),
                "netmask": str(network.netmask),
                "prefix_length": network.prefixlen,
                "total_addresses": network.num_addresses,
                "total_hosts": network.num_addresses - 2,  # Subtract network and broadcast
                "first_host": str(network.network_address + 1),
                "last_host": str(network.broadcast_address - 1),
                "is_private": network.is_private
            }
        except Exception as e:
            return {"error": f"Invalid IP range: {e}"}

    def _print_vpc_preview(self, preview: Dict[str, Any]):
        """Print formatted VPC preview"""
        print(f"\n╭─ 🌐 VPC Preview: {preview['name']}")
        print(f"├─ 🔧 Action: {preview['action']}")
        print(f"├─ 📍 Region: {preview['region']}")
        print(f"├─ 🔢 IP Range: {preview['ip_range']}")
        print(f"├─ 📝 Description: {preview['description']}")
        
        if preview.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(preview['tags'])}")
        
        # Network information
        if preview.get('network_info') and not preview['network_info'].get('error'):
            net_info = preview['network_info']
            print(f"├─ 🌐 Network: {net_info['network_address']}")
            print(f"├─ 📡 Broadcast: {net_info['broadcast_address']}")
            print(f"├─ 🎭 Netmask: {net_info['netmask']}")
            print(f"├─ 🏠 Available Hosts: {net_info['total_hosts']:,}")
            print(f"├─ 🔒 Private Network: {'Yes' if net_info['is_private'] else 'No'}")
        
        if preview['existing']:
            print(f"├─ 📊 Current IP Range: {preview.get('current_ip_range', 'Unknown')}")
            print(f"├─ 🆔 VPC ID: {preview.get('vpc_id', 'Unknown')}")
        
        print(f"╰─ 🎯 Action: {'Update existing VPC' if preview['existing'] else 'Create new VPC'}")

    def _print_vpc_result(self, result: Dict[str, Any]):
        """Print formatted VPC creation result"""
        print(f"\n╭─ 🌐 VPC: {result['name']}")
        print(f"├─ 🆔 ID: {result['id']}")
        print(f"├─ 📍 Region: {result['region']}")
        print(f"├─ 🔢 IP Range: {result['ip_range']}")
        print(f"├─ 📝 Description: {result.get('description', 'None')}")
        print(f"├─ 🏷️  URN: {result['urn']}")
        
        if result.get('tags'):
            print(f"├─ 🏷️  Tags: {', '.join(result['tags'])}")
        
        # Network information
        if result.get('network_info') and not result['network_info'].get('error'):
            net_info = result['network_info']
            print(f"├─ 🌐 Network: {net_info['network_address']}")
            print(f"├─ 📡 Broadcast: {net_info['broadcast_address']}")
            print(f"├─ 🎭 Netmask: {net_info['netmask']} (/{net_info['prefix_length']})")
            print(f"├─ 🏠 Available Hosts: {net_info['total_hosts']:,}")
            print(f"├─ 🔐 Host Range: {net_info['first_host']} - {net_info['last_host']}")
            print(f"├─ 🔒 Private Network: {'Yes' if net_info['is_private'] else 'No'}")
        
        if result.get('default'):
            print(f"├─ ⭐ Default VPC: Yes")
        
        if result.get('was_existing'):
            print(f"├─ ♻️  Action: Updated existing VPC")
            if result.get('updates_needed'):
                print(f"├─ ⚠️  Manual Updates Needed: {len(result['updates_needed'])}")
        else:
            print(f"├─ ✨ Action: Created new VPC")
        
        print(f"╰─ 📅 Created: {result.get('created_at', 'Recently')}")