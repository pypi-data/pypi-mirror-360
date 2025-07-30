"""
Container Engine Implementations

Abstract interface and concrete implementations for Docker, Podman, and other
OCI-compatible container engines. Follows Rails philosophy with consistent
APIs and intelligent defaults.
"""

import subprocess
import os
import platform
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .exceptions import (
    ContainerBuildError,
    ContainerPushError,
)


class ContainerEngine(ABC):
    """
    Abstract base class for all container engines.

    Provides a Rails-like consistent interface across Docker, Podman, etc.
    """

    def __init__(self, engine_info: Dict[str, Any]):
        self.name = engine_info.get('name', 'unknown')
        self.version = engine_info.get('version', 'unknown')
        self.available = engine_info.get('available', False)
        self.features = engine_info.get('features', {})
        self.platform = engine_info.get('platform', platform.system().lower())
        self.engine_info = engine_info

    @abstractmethod
    def build(self, image_name: str, context_path: str, **kwargs) -> bool:
        """Build a container image"""
        pass

    @abstractmethod
    def push(self, image_name: str, registry_url: Optional[str] = None) -> bool:
        """Push image to registry"""
        pass

    @abstractmethod
    def pull(self, image_name: str) -> bool:
        """Pull image from registry"""
        pass

    @abstractmethod
    def run(self, image_name: str, **kwargs) -> subprocess.Popen:
        """Run a container"""
        pass

    @abstractmethod
    def tag(self, source_image: str, target_image: str) -> bool:
        """Tag an image"""
        pass

    @abstractmethod
    def remove_image(self, image_name: str) -> bool:
        """Remove an image"""
        pass

    @abstractmethod
    def list_images(self) -> List[Dict[str, Any]]:
        """List available images"""
        pass

    def supports_multi_platform(self) -> bool:
        """Check if engine supports multi-platform builds"""
        return self.features.get('multi_platform', False)

    def is_rootless(self) -> bool:
        """Check if engine runs in rootless mode"""
        return self.features.get('rootless', False)

    def get_default_registry(self) -> str:
        """Get default registry for this engine"""
        if 'docker' in self.name.lower():
            return 'docker.io'
        elif 'podman' in self.name.lower():
            return 'docker.io'  # Podman is compatible with Docker Hub
        else:
            return 'docker.io'


class DockerEngine(ContainerEngine):
    """
    Docker container engine implementation.

    Supports Docker Desktop and Docker CE with intelligent feature detection.
    """

    def __init__(self, engine_info: Dict[str, Any]):
        super().__init__(engine_info)
        self.buildx_available = engine_info.get('buildx_available', False)

    def build(self, image_name: str, context_path: str, **kwargs) -> bool:
        """
        Build container image using Docker.

        Args:
            image_name: Name/tag for the built image
            context_path: Path to build context
            **kwargs: Additional options
                - dockerfile: Path to Dockerfile (default: Dockerfile)
                - target_platform: Target platform for multi-arch builds
                - build_args: Dictionary of build arguments
                - no_cache: Disable build cache

        Returns:
            bool: True if build successful

        Raises:
            ContainerBuildError: If build fails
        """
        dockerfile = kwargs.get('dockerfile', 'Dockerfile')
        target_platform = kwargs.get('target_platform')
        build_args = kwargs.get('build_args', {})
        no_cache = kwargs.get('no_cache', False)

        # Check if Dockerfile exists
        dockerfile_path = os.path.join(context_path, dockerfile)
        if not os.path.exists(dockerfile_path):
            raise ContainerBuildError(
                self.name,
                1,
                f"Dockerfile not found at {dockerfile_path}"
            )

        cmd = ['docker']

        # Use buildx for multi-platform builds
        if target_platform and self.buildx_available:
            cmd.extend(['buildx', 'build', '--platform', target_platform])
        else:
            cmd.extend(['build'])

        # Add build arguments
        for key, value in build_args.items():
            cmd.extend(['--build-arg', f'{key}={value}'])

        # Add other options
        if no_cache:
            cmd.append('--no-cache')

        cmd.extend(['-t', image_name, '-f', dockerfile, context_path])

        print(f"🔨 Building container image: {image_name}")
        print(f"   Context: {context_path}")
        print("   Engine: Docker")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=context_path
            )

            if result.returncode != 0:
                print("❌ Build failed:")
                print(result.stderr)
                raise ContainerBuildError(self.name, result.returncode, result.stderr)

            print(f"✅ Build successful: {image_name}")
            return True

        except subprocess.CalledProcessError as e:
            raise ContainerBuildError(self.name, e.returncode, str(e))

    def push(self, image_name: str, registry_url: Optional[str] = None) -> bool:
        """Push image to registry"""
        target_image = f"{registry_url}/{image_name}" if registry_url else image_name

        print(f"📤 Pushing image: {target_image}")

        try:
            result = subprocess.run(
                ['docker', 'push', target_image],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = result.stderr.lower()
                
                # Provide better error messages for common issues
                if "authentication failed" in error_msg or "unauthorized" in error_msg:
                    print(f"❌ Authentication failed when pushing to {registry_url}")
                    print(f"💡 To fix authentication:")
                    print(f"   1. Run: gcloud auth configure-docker {registry_url}")
                    print(f"   2. Or run: docker login {registry_url}")
                    print(f"   3. Make sure you have push permissions to the registry")
                elif "permission denied" in error_msg:
                    print(f"❌ Permission denied - insufficient registry permissions")
                    print(f"💡 Make sure you have push access to {registry_url}")
                elif "network" in error_msg or "timeout" in error_msg:
                    print(f"❌ Network error - check internet connection")
                    print(f"💡 Try again in a moment or check network connectivity")
                elif "daemon" in error_msg and "connect" in error_msg:
                    print(f"❌ Cannot connect to Docker daemon")
                    print(f"💡 Make sure Docker Desktop is running")
                else:
                    print(f"❌ Push failed: {result.stderr}")

                raise ContainerPushError(
                    registry_url or self.get_default_registry(),
                    image_name,
                    result.stderr
                )

            print(f"✅ Push successful: {target_image}")
            return True

        except subprocess.CalledProcessError as e:
            raise ContainerPushError(
                registry_url or self.get_default_registry(),
                image_name,
                str(e)
            )

    def pull(self, image_name: str) -> bool:
        """Pull image from registry"""
        print(f"📥 Pulling image: {image_name}")

        try:
            result = subprocess.run(
                ['docker', 'pull', image_name],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"❌ Pull failed: {result.stderr}")
                return False

            print(f"✅ Pull successful: {image_name}")
            return True

        except subprocess.CalledProcessError:
            return False

    def run(self, image_name: str, **kwargs) -> subprocess.Popen:
        """Run a container"""
        port_mapping = kwargs.get('ports', {})
        environment = kwargs.get('environment', {})
        volumes = kwargs.get('volumes', {})
        detach = kwargs.get('detach', True)
        name = kwargs.get('name')

        cmd = ['docker', 'run']

        if detach:
            cmd.append('-d')

        if name:
            cmd.extend(['--name', name])

        # Add port mappings
        for host_port, container_port in port_mapping.items():
            cmd.extend(['-p', f'{host_port}:{container_port}'])

        # Add environment variables
        for key, value in environment.items():
            cmd.extend(['-e', f'{key}={value}'])

        # Add volume mounts
        for host_path, container_path in volumes.items():
            cmd.extend(['-v', f'{host_path}:{container_path}'])

        cmd.append(image_name)

        return subprocess.Popen(cmd)

    def tag(self, source_image: str, target_image: str) -> bool:
        """Tag an image"""
        try:
            result = subprocess.run(
                ['docker', 'tag', source_image, target_image],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def remove_image(self, image_name: str) -> bool:
        """Remove an image"""
        try:
            result = subprocess.run(
                ['docker', 'rmi', image_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def list_images(self) -> List[Dict[str, Any]]:
        """List available images"""
        try:
            result = subprocess.run(
                ['docker', 'images', '--format', 'json'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            images = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    images.append(json.loads(line))

            return images

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []


class PodmanEngine(ContainerEngine):
    """
    Podman container engine implementation.

    Supports rootless containers and enhanced security features.
    """

    def __init__(self, engine_info: Dict[str, Any]):
        super().__init__(engine_info)
        self.buildah_available = engine_info.get('buildah_available', False)

    def build(self, image_name: str, context_path: str, **kwargs) -> bool:
        """Build container image using Podman"""
        dockerfile = kwargs.get('dockerfile', 'Containerfile')

        # Try Containerfile first (Podman convention), then Dockerfile
        containerfile_path = os.path.join(context_path, 'Containerfile')
        dockerfile_path = os.path.join(context_path, 'Dockerfile')

        if os.path.exists(containerfile_path):
            dockerfile = 'Containerfile'
        elif os.path.exists(dockerfile_path):
            dockerfile = 'Dockerfile'
        else:
            raise ContainerBuildError(
                self.name,
                1,
                f"Neither Containerfile nor Dockerfile found in {context_path}"
            )

        target_platform = kwargs.get('target_platform')
        build_args = kwargs.get('build_args', {})
        no_cache = kwargs.get('no_cache', False)

        cmd = ['podman', 'build']

        # Add platform if specified
        if target_platform:
            cmd.extend(['--platform', target_platform])

        # Add build arguments
        for key, value in build_args.items():
            cmd.extend(['--build-arg', f'{key}={value}'])

        # Add other options
        if no_cache:
            cmd.append('--no-cache')

        cmd.extend(['-t', image_name, '-f', dockerfile, context_path])

        print(f"🔨 Building container image: {image_name}")
        print(f"   Context: {context_path}")
        print("   Engine: Podman")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=context_path
            )

            if result.returncode != 0:
                print("❌ Build failed:")
                print(result.stderr)
                raise ContainerBuildError(self.name, result.returncode, result.stderr)

            print(f"✅ Build successful: {image_name}")
            return True

        except subprocess.CalledProcessError as e:
            raise ContainerBuildError(self.name, e.returncode, str(e))

    def push(self, image_name: str, registry_url: Optional[str] = None) -> bool:
        """Push image to registry"""
        target_image = f"{registry_url}/{image_name}" if registry_url else image_name

        print(f"📤 Pushing image: {target_image}")

        try:
            result = subprocess.run(
                ['podman', 'push', target_image],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                error_msg = result.stderr.lower()
                
                # Provide better error messages for common issues
                if "authentication failed" in error_msg or "unauthorized" in error_msg:
                    print(f"❌ Authentication failed when pushing to {registry_url}")
                    print(f"💡 To fix authentication:")
                    print(f"   1. Run: gcloud auth configure-docker {registry_url}")
                    print(f"   2. Or run: podman login {registry_url}")
                    print(f"   3. Make sure you have push permissions to the registry")
                elif "permission denied" in error_msg:
                    print(f"❌ Permission denied - insufficient registry permissions")
                    print(f"💡 Make sure you have push access to {registry_url}")
                elif "network" in error_msg or "timeout" in error_msg:
                    print(f"❌ Network error - check internet connection")
                    print(f"💡 Try again in a moment or check network connectivity")
                else:
                    print(f"❌ Push failed: {result.stderr}")
                
                raise ContainerPushError(
                    registry_url or self.get_default_registry(),
                    image_name,
                    result.stderr
                )

            print(f"✅ Push successful: {target_image}")
            return True

        except subprocess.CalledProcessError as e:
            raise ContainerPushError(
                registry_url or self.get_default_registry(),
                image_name,
                str(e)
            )

    def pull(self, image_name: str) -> bool:
        """Pull image from registry"""
        print(f"📥 Pulling image: {image_name}")

        try:
            result = subprocess.run(
                ['podman', 'pull', image_name],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"❌ Pull failed: {result.stderr}")
                return False

            print(f"✅ Pull successful: {image_name}")
            return True

        except subprocess.CalledProcessError:
            return False

    def run(self, image_name: str, **kwargs) -> subprocess.Popen:
        """Run a container"""
        port_mapping = kwargs.get('ports', {})
        environment = kwargs.get('environment', {})
        volumes = kwargs.get('volumes', {})
        detach = kwargs.get('detach', True)
        name = kwargs.get('name')

        cmd = ['podman', 'run']

        if detach:
            cmd.append('-d')

        if name:
            cmd.extend(['--name', name])

        # Add port mappings
        for host_port, container_port in port_mapping.items():
            cmd.extend(['-p', f'{host_port}:{container_port}'])

        # Add environment variables
        for key, value in environment.items():
            cmd.extend(['-e', f'{key}={value}'])

        # Add volume mounts
        for host_path, container_path in volumes.items():
            cmd.extend(['-v', f'{host_path}:{container_path}'])

        cmd.append(image_name)

        return subprocess.Popen(cmd)

    def tag(self, source_image: str, target_image: str) -> bool:
        """Tag an image"""
        try:
            result = subprocess.run(
                ['podman', 'tag', source_image, target_image],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def remove_image(self, image_name: str) -> bool:
        """Remove an image"""
        try:
            result = subprocess.run(
                ['podman', 'rmi', image_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def list_images(self) -> List[Dict[str, Any]]:
        """List available images"""
        try:
            result = subprocess.run(
                ['podman', 'images', '--format', 'json'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            # Podman returns a JSON array
            return json.loads(result.stdout)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []
