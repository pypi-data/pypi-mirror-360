import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any, Optional
from .do_client import DoClient

class ContainerRegistryManager:
    """Manages DigitalOcean container registry operations"""
    
    def __init__(self, do_client: DoClient):
        self.do_client = do_client
    
    def build_and_push_image(self, service_name: str, image_tag: str, template_path: str) -> Dict[str, Any]:
        """Build a Docker image from a template and push it to DigitalOcean registry"""
        if not self.do_client.is_authenticated():
            raise ValueError("Authentication token not set. Use .authenticate() first.")
        
        print(f"🐳 Building and pushing Docker image: {image_tag}")
        
        # For now, we'll use a simple approach - build locally and use a public registry
        # or create a registry using doctl if available
        registry_info = self._get_or_create_registry()
        
        if not registry_info:
            # Fallback: use a simple local build without registry
            print(f"⚠️  Registry not available, building image locally only")
            full_image_name = f"{service_name}:latest"
            build_success = self._build_docker_image(template_path, full_image_name)
            
            if not build_success:
                raise Exception("Failed to build Docker image")
            
            return {
                "registry_url": "local",
                "image_name": image_tag,
                "full_image_name": full_image_name,
                "registry_id": "local"
            }
        
        registry_url = registry_info['registry_url']
        full_image_name = f"{registry_url}/{image_tag}"
        
        # Build the Docker image
        print(f"🔨 Building Docker image from template: {template_path}")
        build_success = self._build_docker_image(template_path, full_image_name)
        
        if not build_success:
            raise Exception("Failed to build Docker image")
        
        # Push the image to registry
        print(f"📤 Pushing image to registry: {full_image_name}")
        push_success = self._push_docker_image(full_image_name)
        
        if not push_success:
            raise Exception("Failed to push Docker image to registry")
        
        print(f"✅ Image successfully pushed to registry: {full_image_name}")
        
        return {
            "registry_url": registry_url,
            "image_name": image_tag,
            "full_image_name": full_image_name,
            "registry_id": registry_info['id']
        }
    
    def _get_or_create_registry(self) -> Optional[Dict[str, Any]]:
        """Get information about existing registry or create one using doctl"""
        try:
            # Try to get existing registry using doctl
            cmd = ["doctl", "registry", "list", "--format", "Name,RegistryURL"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse the output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    parts = lines[1].split('\t')
                    if len(parts) >= 2:
                        return {
                            'id': parts[0],
                            'registry_url': parts[1],
                            'name': parts[0]
                        }
            
            # Try to create a registry using doctl
            print("📦 Creating container registry using doctl...")
            create_cmd = ["doctl", "registry", "create", "infradsl-registry", "--subscription-tier-slug", "basic"]
            create_result = subprocess.run(create_cmd, capture_output=True, text=True)
            
            if create_result.returncode == 0:
                # Get the registry info after creation
                return self._get_or_create_registry()
            else:
                print(f"⚠️  Could not create registry: {create_result.stderr}")
                return None
                
        except Exception as e:
            print(f"⚠️  Warning: Could not manage registry: {e}")
            return None
    
    def _build_docker_image(self, template_path: str, image_name: str) -> bool:
        """Build a Docker image from a template directory"""
        try:
            # Check if template directory exists
            if not os.path.exists(template_path):
                raise Exception(f"Template directory not found: {template_path}")
            
            # Check if Dockerfile exists
            dockerfile_path = os.path.join(template_path, "Dockerfile")
            if not os.path.exists(dockerfile_path):
                raise Exception(f"Dockerfile not found in template: {dockerfile_path}")
            
            # Build the Docker image
            cmd = ["docker", "build", "-t", image_name, template_path]
            print(f"   Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Docker build failed:")
                print(f"   Error: {result.stderr}")
                return False
            
            print(f"✅ Docker image built successfully: {image_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to build Docker image: {e}")
            return False
    
    def _push_docker_image(self, image_name: str) -> bool:
        """Push a Docker image to DigitalOcean registry"""
        try:
            # First, authenticate with the registry
            auth_cmd = ["doctl", "registry", "login"]
            auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
            
            if auth_result.returncode != 0:
                print(f"❌ Failed to authenticate with registry:")
                print(f"   Error: {auth_result.stderr}")
                return False
            
            # Push the image
            push_cmd = ["docker", "push", image_name]
            print(f"   Running: {' '.join(push_cmd)}")
            
            result = subprocess.run(push_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Docker push failed:")
                print(f"   Error: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to push Docker image: {e}")
            return False
    
    def delete_image(self, image_name: str) -> bool:
        """Delete an image from the registry"""
        try:
            # Try to delete using doctl
            cmd = ["doctl", "registry", "delete-manifest", image_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Image deleted from registry: {image_name}")
                return True
            else:
                print(f"⚠️  Warning: Failed to delete image: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete image: {e}")
            return False 