from typing import Dict, Any, List, Optional
from .infrastructure_planner import FirewallRule, LoadBalancerConfig
from .droplet_manager import DropletConfig


class StatusReporter:
    """Handles all output formatting, status display, and preview functionality"""
    
    def __init__(self):
        pass
    
    def print_infrastructure_status(self, result: Dict[str, Any], existing_resources: Dict[str, Any]):
        """Print the final infrastructure status"""
        was_existing = result['was_existing']
        
        if was_existing:
            print("\n✨ Infrastructure updated successfully!")
        else:
            print("\n✨ Infrastructure created successfully!")
            
        print("=" * 40)
        print(f"🔷 Name:     {result['name']}")
        print(f"🔷 Region:   {result['region']}")
        print(f"🔷 Size:     {result['size']}")
        print(f"🔷 Status:   {result['status']}")
        print(f"🔷 IP:       {result['ip_address']}")
        
        if result.get('registry_image'):
            print(f"🐳 Container: {result['registry_image']}")
            print(f"🐳 Port:     {result.get('container_port', 'N/A')}")
        
        if result['services']:
            print(f"🔷 Services: {', '.join(result['services'])}")
            
        if result['firewall_id']:
            if existing_resources['firewall']:
                print(f"🔥 Firewall: Using existing ({result['firewall_id']})")
            else:
                print(f"🔥 Firewall: Created ({result['firewall_id']})")
                
        if result['load_balancer_id']:
            if existing_resources['load_balancer']:
                print(f"⚖️  Load Balancer: Using existing ({result['load_balancer_ip']})")
            else:
                print(f"⚖️  Load Balancer: Created ({result['load_balancer_ip']})")
                
        print("=" * 40)
        
        # Service-specific messages
        access_ip = result['load_balancer_ip'] or result['ip_address']
        if result.get('registry_image'):
            print(f"\n🌎 You can access your container at: http://{access_ip}:{result.get('container_port', 8080)}")
            if not was_existing:
                print("   Note: It might take a few minutes for the container to finish setting up.")
        elif "nginx" in result['services']:
            print(f"\n🌎 You can access your nginx server at: http://{access_ip}")
            if not was_existing:
                print("   Note: It might take a few minutes for the server to finish setting up.")
    
    def print_preview(self, config: DropletConfig, firewall_rules: Optional[List[FirewallRule]] = None, load_balancer_config: Optional[LoadBalancerConfig] = None) -> Dict[str, Any]:
        """Print infrastructure preview without actually creating it"""
        # Create preview result
        preview_result = {
            "name": config.name,
            "region": config.region,
            "size": config.size,
            "image": config.image,
            "backups": config.backups,
            "monitoring": config.monitoring,
            "tags": config.tags or [],
            "services": [config.service] if config.service else [],
            "service_variables": config.service_variables or {},
            "registry_image": config.registry_image,
            "container_port": config.container_port
        }
        
        # Print preview output
        print("\n🔍 Infrastructure Preview")
        print("=" * 40)
        print(f"📋 What will be created:")
        print(f"   • DigitalOcean Droplet")
        print(f"🔷 Name:       {preview_result['name']}")
        print(f"🔷 Region:     {preview_result['region']}")
        print(f"🔷 Size:       {preview_result['size']}")
        print(f"🔷 Image:      {preview_result['image']}")
        print(f"🔷 Backups:    {'Enabled' if preview_result['backups'] else 'Disabled'}")
        print(f"🔷 Monitoring: {'Enabled' if preview_result['monitoring'] else 'Disabled'}")
        if preview_result['tags']:
            print(f"🔷 Tags:       {', '.join(preview_result['tags'])}")
        
        # Show container registry information
        if preview_result['registry_image']:
            print(f"\n🐳 Container Deployment:")
            print(f"   • Registry Image: {preview_result['registry_image']}")
            print(f"   • Container Port: {preview_result['container_port']}")
            if config.container_env:
                print(f"   • Environment Variables:")
                for key, value in config.container_env.items():
                    print(f"     - {key}: {value}")
        
        # Show service information
        if preview_result['services']:
            print(f"\n🛠️  Services to be installed:")
            for service in preview_result['services']:
                print(f"   • {service}")
                if service == 'nginx' and preview_result['service_variables']:
                    print(f"     Configuration:")
                    for key, value in preview_result['service_variables'].items():
                        print(f"       - {key}: {value}")
        
        # Show firewall rules
        if firewall_rules:
            print(f"\n🔥 Firewall Rules:")
            for rule in firewall_rules:
                sources = ', '.join(rule.source_addresses[:2]) + ('...' if len(rule.source_addresses) > 2 else '')
                print(f"   • {rule.name}: {rule.protocol.upper()}/{rule.port} from {sources}")
        
        # Show load balancer
        if load_balancer_config:
            print(f"\n⚖️  Load Balancer:")
            print(f"   • Name: {load_balancer_config.name}")
            print(f"   • Algorithm: {load_balancer_config.algorithm}")
            print(f"   • Forwarding: HTTP:80 → HTTP:80, HTTPS:443 → HTTP:80")
            print(f"   • Health Check: HTTP on port 80")
        
        print("=" * 40)
        print("💡 Run with 'infra apply' to create these resources")
        
        return preview_result 