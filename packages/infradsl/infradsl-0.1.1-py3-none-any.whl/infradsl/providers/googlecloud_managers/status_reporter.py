from typing import Dict, Any, Optional
from .vm_manager import VmConfig

class GcpStatusReporter:
    """Handles output formatting and status display for Google Cloud resources"""

    def __init__(self):
        pass

    def print_vm_status(self, result: Dict[str, Any], was_existing: bool = False):
        """Print the final VM status"""
        if was_existing:
            print("\n✨ VM instance updated successfully!")
        else:
            print("\n✨ VM instance created successfully!")

        print("=" * 40)
        print(f"🔷 Name:     {result['name']}")
        print(f"🔷 Zone:     {result['zone']}")
        print(f"🔷 Type:     {result['machine_type']}")
        print(f"🔷 Status:   {result['status']}")
        print(f"🔷 IP:       {result['ip_address']}")

        if result.get('tags'):
            print(f"🔷 Tags:     {', '.join(result['tags'])}")

        if result.get('startup_script'):
            print(f"🔷 Service:  Configured")

        if result.get('health_check'):
            print(f"🔷 Health Check: {result['health_check']}")

        if result.get('load_balancer'):
            lb_info = result['load_balancer']
            print(f"🔷 Load Balancer: {lb_info['ip_address']} (Port: {lb_info['port']})")

        print("=" * 40)

        # Service-specific messages
        if result.get('startup_script'):
            print(f"\n🛠️  Service configured")
            print("   Note: It might take a few minutes for the service to finish setting up.")

        if result.get('load_balancer'):
            print(f"\n⚖️  Load balancer configured")
            print("   Note: Traffic will be distributed across backend instances.")

    def print_vm_preview(self, config: VmConfig, load_balancer_config: Optional[Any] = None) -> Dict[str, Any]:
        """Print VM preview without actually creating it"""
        # Create preview result
        preview_result = {
            "name": config.name,
            "zone": config.zone,
            "machine_type": config.machine_type,
            "image_family": config.image_family,
            "image_project": config.image_project,
            "network": config.network,
            "disk_size_gb": config.disk_size_gb,
            "tags": config.tags or [],
            "metadata": config.metadata or {},
            "startup_script": config.startup_script,
            "health_check": config.health_check,
            "load_balancer": load_balancer_config
        }

        # Print preview output
        print("\n🔍 Google Cloud VM Preview")
        print("=" * 40)
        print(f"📋 What will be created:")
        print(f"   • Google Cloud Compute Engine VM")
        print(f"🔷 Name:         {preview_result['name']}")
        print(f"🔷 Zone:         {preview_result['zone']}")
        print(f"🔷 Machine Type: {preview_result['machine_type']}")
        print(f"🔷 Image:        {preview_result['image_family']} ({preview_result['image_project']})")
        print(f"🔷 Disk Size:    {preview_result['disk_size_gb']} GB")
        print(f"🔷 Network:      {preview_result['network']}")

        if preview_result['tags']:
            print(f"🔷 Tags:         {', '.join(preview_result['tags'])}")

        if preview_result['metadata']:
            print(f"\n📝 Metadata:")
            for key, value in preview_result['metadata'].items():
                print(f"   • {key}: {value}")

        if preview_result['startup_script']:
            print(f"\n🛠️  Service: Configured")
            print(f"   • Startup script will be executed")

        if preview_result['health_check']:
            print(f"\n🏥 Health Check: Configured")
            print(f"   • Protocol: {preview_result['health_check']['protocol'].upper()}")
            print(f"   • Port: {preview_result['health_check']['port']}")
            print(f"   • Path: {preview_result['health_check']['path']}")

        if preview_result['load_balancer']:
            print(f"\n⚖️  Load Balancer: Configured")
            print(f"   • Name: {preview_result['load_balancer'].name}")
            print(f"   • Backends: {len(preview_result['load_balancer'].backends)}")
            for backend in preview_result['load_balancer'].backends:
                print(f"     - {backend.vm_name} ({backend.zone}:{backend.port})")

        print("=" * 40)
        print("💡 Run with 'infra apply' to create this VM")

        return preview_result

    def info(self, message: str):
        """Print info message"""
        print(message)

    def success(self, message: str):
        """Print success message"""
        print(message)

    def error(self, message: str):
        """Print error message"""
        print(message)

    def warning(self, message: str):
        """Print warning message"""
        print(message)
