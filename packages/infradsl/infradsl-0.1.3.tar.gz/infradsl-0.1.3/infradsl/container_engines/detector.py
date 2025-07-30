"""
Container Engine Detector

Intelligent detection and selection of available container engines.
Follows Rails philosophy: convention over configuration with smart defaults.
"""

import subprocess
import shutil
import platform
from typing import Optional, Dict, Any
from .exceptions import NoEngineFoundError, ContainerEngineError


class ContainerEngineDetector:
    """
    Detects available container engines and selects the best one.

    Rails philosophy:
    - Convention over configuration
    - Smart defaults based on platform
    - Graceful degradation
    - Clear error messages
    """

    def __init__(self):
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        self._detected_engines = None

    def detect_engines(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect all available container engines on the system.

        Returns:
            Dict mapping engine names to their details
        """
        if self._detected_engines is not None:
            return self._detected_engines

        engines = {}

        # Check for Docker
        docker_info = self._check_docker()
        if docker_info:
            engines['docker'] = docker_info

        # Check for Podman
        podman_info = self._check_podman()
        if podman_info:
            engines['podman'] = podman_info

        # Check for other OCI engines
        buildah_info = self._check_buildah()
        if buildah_info:
            engines['buildah'] = buildah_info

        self._detected_engines = engines
        return engines

    def get_best_engine(self):
        """
        Get the best available container engine based on platform and preferences.

        Selection priority:
        1. Available engines only (skip unavailable ones)
        2. Platform-specific preferences
        3. Feature completeness
        4. Performance characteristics

        Returns:
            ContainerEngine: Ready-to-use engine instance

        Raises:
            NoEngineFoundError: If no compatible engine found
        """
        engines = self.detect_engines()

        if not engines:
            raise NoEngineFoundError()

        # Filter to only available engines
        available_engines = {name: info for name, info in engines.items() 
                           if info.get('available', False)}

        if not available_engines:
            # No engines are actually available, provide helpful error
            unavailable_list = []
            for name, info in engines.items():
                reason = info.get('reason', 'Unknown issue')
                suggestion = info.get('suggestion', '')
                unavailable_list.append(f"{name}: {reason}" + (f" ({suggestion})" if suggestion else ""))
            
            error_msg = "Container engines found but not available:\n" + "\n".join(f"  • {item}" for item in unavailable_list)
            raise NoEngineFoundError()

        # Platform-specific preferences (Rails convention over configuration)
        # But only consider available engines
        if self.platform == 'darwin':  # macOS
            # Prefer Docker Desktop on macOS for best UX, but only if available
            if 'docker' in available_engines:
                from .engines import DockerEngine
                return DockerEngine(available_engines['docker'])
            elif 'podman' in available_engines:
                from .engines import PodmanEngine
                return PodmanEngine(available_engines['podman'])

        elif self.platform == 'linux':
            # Prefer Podman on Linux for security (rootless), but only if available
            if 'podman' in available_engines and available_engines['podman'].get('rootless', False):
                from .engines import PodmanEngine
                return PodmanEngine(available_engines['podman'])
            elif 'docker' in available_engines:
                from .engines import DockerEngine
                return DockerEngine(available_engines['docker'])
            elif 'podman' in available_engines:
                from .engines import PodmanEngine
                return PodmanEngine(available_engines['podman'])

        elif self.platform == 'windows':
            # Prefer Docker Desktop on Windows, but only if available
            if 'docker' in available_engines:
                from .engines import DockerEngine
                return DockerEngine(available_engines['docker'])

        # Fallback: use first available engine
        first_engine = next(iter(available_engines.items()))
        engine_name, engine_info = first_engine

        if engine_name == 'docker':
            from .engines import DockerEngine
            return DockerEngine(engine_info)
        elif engine_name == 'podman':
            from .engines import PodmanEngine
            return PodmanEngine(engine_info)
        else:
            raise ContainerEngineError(f"Unsupported engine: {engine_name}")

    def _check_docker(self) -> Optional[Dict[str, Any]]:
        """Check if Docker is available and get its capabilities"""
        try:
            # Check if docker command exists
            if not shutil.which('docker'):
                return None

            # Check if Docker daemon is running (silently)
            result = subprocess.run(
                ['docker', 'version', '--format', '{{.Server.Version}}'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                # Docker CLI exists but daemon not running - return info but mark as unavailable
                return {
                    'name': 'docker',
                    'version': None,
                    'available': False,
                    'reason': 'Docker daemon not running',
                    'suggestion': 'Start Docker Desktop or Docker daemon',
                    'silent_failure': True  # Don't show error messages during auto-detection
                }

            server_version = result.stdout.strip()

            # Get client version
            client_result = subprocess.run(
                ['docker', 'version', '--format', '{{.Client.Version}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            client_version = client_result.stdout.strip() if client_result.returncode == 0 else 'unknown'

            # Check for buildx support (multi-platform builds)
            buildx_available = self._check_docker_buildx()

            # Check if running rootless
            info_result = subprocess.run(
                ['docker', 'info', '--format', '{{.SecurityOptions}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            rootless = 'rootless' in info_result.stdout.lower()

            return {
                'name': 'docker',
                'client_version': client_version,
                'server_version': server_version,
                'available': True,
                'buildx_available': buildx_available,
                'rootless': rootless,
                'platform': self.platform,
                'features': {
                    'build': True,
                    'push': True,
                    'multi_platform': buildx_available,
                    'cache': True
                }
            }

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Silent failure - don't log errors during auto-detection
            return None

    def _check_podman(self) -> Optional[Dict[str, Any]]:
        """Check if Podman is available and get its capabilities"""
        try:
            # Check if podman command exists
            if not shutil.which('podman'):
                return None

            # Get version
            result = subprocess.run(
                ['podman', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            version_line = result.stdout.strip()
            version = version_line.split()[-1] if version_line else 'unknown'

            # Check if running rootless
            info_result = subprocess.run(
                ['podman', 'info', '--format', '{{.Host.Security.Rootless}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            rootless = info_result.stdout.strip().lower() == 'true'

            # Check for buildah integration
            buildah_available = shutil.which('buildah') is not None

            return {
                'name': 'podman',
                'version': version,
                'available': True,
                'rootless': rootless,
                'buildah_available': buildah_available,
                'platform': self.platform,
                'features': {
                    'build': True,
                    'push': True,
                    'multi_platform': buildah_available,
                    'cache': True,
                    'rootless': rootless
                }
            }

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return None

    def _check_buildah(self) -> Optional[Dict[str, Any]]:
        """Check if Buildah is available (build-only engine)"""
        try:
            if not shutil.which('buildah'):
                return None

            result = subprocess.run(
                ['buildah', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            version_line = result.stdout.strip()
            version = version_line.split()[-1] if version_line else 'unknown'

            return {
                'name': 'buildah',
                'version': version,
                'available': True,
                'platform': self.platform,
                'features': {
                    'build': True,
                    'push': True,
                    'multi_platform': True,
                    'cache': True
                }
            }

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return None

    def _check_docker_buildx(self) -> bool:
        """Check if Docker Buildx is available for multi-platform builds"""
        try:
            result = subprocess.run(
                ['docker', 'buildx', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def print_engine_status(self):
        """Print a Rails-like status report of available engines"""
        engines = self.detect_engines()

        print("🔍 Container Engine Detection Report")
        print("=" * 40)

        if not engines:
            print("❌ No container engines found")
            print("")
            print("💡 Install one of the following:")
            print("   • Docker Desktop: https://docker.com/desktop")
            print("   • Podman: https://podman.io/getting-started/installation")
            return

        for name, info in engines.items():
            status = "✅" if info.get('available', False) else "⚠️"
            print(f"{status} {name.capitalize()}")

            if info.get('available'):
                if 'version' in info:
                    print(f"   Version: {info['version']}")
                elif 'client_version' in info:
                    print(f"   Client: {info['client_version']}, Server: {info.get('server_version', 'unknown')}")

                features = info.get('features', {})
                if features.get('multi_platform'):
                    print("   ✅ Multi-platform builds supported")
                if features.get('rootless'):
                    print("   ✅ Rootless mode available")
            else:
                reason = info.get('reason', 'Not available')
                print(f"   Reason: {reason}")
                if 'suggestion' in info:
                    print(f"   Suggestion: {info['suggestion']}")
            print("")

        # Show recommended engine
        try:
            best_engine = self.get_best_engine()
            print(f"🎯 Recommended: {best_engine.name}")
            print("=" * 40)
        except NoEngineFoundError:
            print("❌ No usable engines found")
            print("=" * 40)
