import digitalocean
import time
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from .do_client import DoClient


class DropletConfig(BaseModel):
    name: str
    size: Optional[str] = None
    region: Optional[str] = None
    image: str = "ubuntu-22-04-x64"
    ssh_keys: Optional[List[str]] = None
    backups: bool = False
    ipv6: bool = False
    monitoring: bool = True
    tags: Optional[List[str]] = None
    user_data: Optional[str] = None
    service: Optional[str] = None
    service_variables: Optional[Dict[str, Any]] = None
    registry_image: Optional[str] = None  # Full registry image name (e.g., registry.digitalocean.com/myapp:latest)
    container_port: Optional[int] = None  # Port the container exposes
    container_env: Optional[Dict[str, str]] = None  # Environment variables for container


class DropletManager:
    """Manages droplet operations including creation and configuration"""
    
    def __init__(self, do_client: DoClient):
        self.do_client = do_client
    
    def create_droplet(self, config: DropletConfig) -> Tuple[int, str, str]:
        """Create a new droplet and return its ID, IP, and status"""
        # Create droplet parameters
        params = {
            "token": self.do_client.token,
            "name": config.name,
            "region": config.region,
            "image": config.image,
            "size_slug": config.size,
            "backups": config.backups,
            "ipv6": config.ipv6,
            "monitoring": config.monitoring,
            "tags": config.tags or [],
            "user_data": config.user_data
        }

        # Only add ssh_keys if they are provided
        if config.ssh_keys:
            params["ssh_keys"] = config.ssh_keys

        try:
            droplet = digitalocean.Droplet(**params)
            droplet.create()
            
            # Wait for the droplet to be active and get its IP
            for _ in range(10):  # Try for about 5 minutes
                droplet.load()
                if droplet.status == 'active':
                    return droplet.id, droplet.ip_address, droplet.status
                time.sleep(30)
            
            raise TimeoutError("Droplet creation timed out")
            
        except Exception as e:
            raise Exception(f"Failed to create droplet: {str(e)}")
    
    def get_droplet_info(self, droplet_id: int) -> Dict[str, Any]:
        """Get droplet information by ID"""
        try:
            droplets = self.do_client.client.get_all_droplets()
            for droplet in droplets:
                if droplet.id == droplet_id:
                    return {
                        'id': droplet.id,
                        'name': droplet.name,
                        'ip': droplet.ip_address,
                        'status': droplet.status,
                        'region': droplet.region['name'],
                        'size': droplet.size_slug
                    }
            return None
        except Exception as e:
            raise Exception(f"Failed to get droplet info: {str(e)}")
    
    def validate_droplet_config(self, config: DropletConfig) -> bool:
        """Validate that droplet configuration is complete"""
        if not all([config.size, config.region]):
            raise ValueError("Size and region are required. Use .size() and .region() to set them.")
        return True
    
    def generate_container_user_data(self, config: DropletConfig) -> str:
        """Generate user data script for container deployment"""
        if not config.registry_image or not config.container_port:
            raise ValueError("Registry image and container port are required for container deployment")
        
        # Create environment variables string
        env_vars = ""
        if config.container_env:
            for key, value in config.container_env.items():
                env_vars += f'export {key}="{value}"\n'
        
        # Check if this is a registry image or local image
        if config.registry_image.startswith("registry.digitalocean.com"):
            # Registry image - need to authenticate
            auth_script = """
# Authenticate with DigitalOcean registry
doctl registry login
"""
        else:
            # Local image - no authentication needed
            auth_script = ""
        
        user_data = f"""#!/bin/bash
# Update system
apt-get update
apt-get install -y docker.io

# Start Docker service
systemctl start docker
systemctl enable docker

{auth_script}
# Pull and run the container
{env_vars}
docker run -d \\
  --name {config.name} \\
  --restart unless-stopped \\
  -p {config.container_port}:{config.container_port} \\
  {config.registry_image}

# Wait for container to be ready
sleep 10

# Check if container is running
if docker ps | grep -q {config.name}; then
    echo "Container {config.name} is running successfully"
else
    echo "Failed to start container {config.name}"
    docker logs {config.name}
    exit 1
fi
"""
        return user_data 