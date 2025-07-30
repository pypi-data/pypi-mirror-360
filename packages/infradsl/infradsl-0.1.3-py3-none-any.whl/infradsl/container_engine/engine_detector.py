"""
Container Engine Detector

This module handles the detection and capability analysis of available
container engines (Docker, Podman, containerd, etc.).
"""

import subprocess
import shutil
import json
from enum import Enum
from typing import Dict, Any, Optional


class ContainerEngine(Enum):
    DOCKER = "docker"
    PODMAN = "podman"
    CONTAINERD = "containerd"
    NERDCTL = "nerdctl"
    UNKNOWN = "unknown"


class EngineDetector:
    """
    Container Engine Detection and Capability Analysis
    
    This class handles:
    - Auto-detection of available container engines
    - Version information retrieval
    - Capability analysis (compose, buildx, rootless, etc.)
    - Engine preference handling
    """

    def __init__(self, preferred_engine: Optional[str] = None):
        """Initialize the engine detector"""
        self.preferred_engine = preferred_engine
        self.detected_engine = None
        self.engine_command = None
        self.engine_version = None
        self.capabilities = {}

    def detect_container_engine(self) -> ContainerEngine:
        """
        Intelligently detect the best available container engine.

        Returns:
            ContainerEngine: The detected container engine
        """
        engines_to_check = [
            (ContainerEngine.DOCKER, "docker"),
            (ContainerEngine.PODMAN, "podman"),
            (ContainerEngine.NERDCTL, "nerdctl"),
            (ContainerEngine.CONTAINERD, "ctr")
        ]

        # If user specified a preference, try that first
        if self.preferred_engine:
            for engine, command in engines_to_check:
                if engine.value == self.preferred_engine.lower():
                    if self._test_engine_availability(command):
                        self.detected_engine = engine
                        self.engine_command = command
                        break

        # If no preference or preference not available, auto-detect
        if not self.detected_engine:
            for engine, command in engines_to_check:
                if self._test_engine_availability(command):
                    self.detected_engine = engine
                    self.engine_command = command
                    break

        if not self.detected_engine:
            self.detected_engine = ContainerEngine.UNKNOWN
            print("⚠️  No container engine detected. Please install Docker or Podman.")
            return self.detected_engine

        # Get engine version and capabilities
        self._get_engine_info()

        print(f"🐳 Detected container engine: {self.detected_engine.value} ({self.engine_version})")
        return self.detected_engine

    def _test_engine_availability(self, command: str) -> bool:
        """Test if a container engine is available and working."""
        try:
            # Check if command exists
            if not shutil.which(command):
                return False

            # Test basic functionality
            result = subprocess.run(
                [command, "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def _get_engine_info(self):
        """Get detailed information about the detected engine."""
        try:
            result = subprocess.run(
                [self.engine_command, "version", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                version_info = json.loads(result.stdout)
                if self.detected_engine == ContainerEngine.DOCKER:
                    self.engine_version = version_info.get("Client", {}).get("Version", "unknown")
                elif self.detected_engine == ContainerEngine.PODMAN:
                    self.engine_version = version_info.get("client", {}).get("version", "unknown")
                else:
                    self.engine_version = "unknown"
            else:
                # Fallback to simple version command
                result = subprocess.run(
                    [self.engine_command, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.engine_version = result.stdout.strip().split()[-1]
        except (subprocess.TimeoutExpired, json.JSONDecodeError, subprocess.SubprocessError):
            self.engine_version = "unknown"

        # Detect capabilities
        self._detect_capabilities()

    def _detect_capabilities(self):
        """Detect what the container engine can do."""
        self.capabilities = {
            "build": True,
            "push": True,
            "run": True,
            "compose": False,
            "buildx": False,
            "rootless": False
        }

        if self.detected_engine == ContainerEngine.DOCKER:
            # Check for Docker Compose
            if shutil.which("docker-compose") or self._test_docker_compose_plugin():
                self.capabilities["compose"] = True

            # Check for BuildX
            if self._test_docker_buildx():
                self.capabilities["buildx"] = True

        elif self.detected_engine == ContainerEngine.PODMAN:
            # Podman has built-in compose support
            self.capabilities["compose"] = True
            self.capabilities["rootless"] = True

    def _test_docker_compose_plugin(self) -> bool:
        """Test if Docker Compose plugin is available."""
        try:
            result = subprocess.run(
                [self.engine_command, "compose", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def _test_docker_buildx(self) -> bool:
        """Test if Docker BuildX is available."""
        try:
            result = subprocess.run(
                [self.engine_command, "buildx", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status information."""
        return {
            "engine": self.detected_engine.value if self.detected_engine else "unknown",
            "command": self.engine_command,
            "version": self.engine_version,
            "capabilities": self.capabilities,
            "available": self.detected_engine != ContainerEngine.UNKNOWN
        }

    def is_engine_available(self, engine_name: str) -> bool:
        """Check if a specific engine is available."""
        engine_commands = {
            "docker": "docker",
            "podman": "podman",
            "nerdctl": "nerdctl",
            "containerd": "ctr"
        }
        
        command = engine_commands.get(engine_name.lower())
        if not command:
            return False
            
        return self._test_engine_availability(command)

    def get_available_engines(self) -> list:
        """Get list of all available container engines."""
        engines = []
        engine_commands = {
            "docker": "docker",
            "podman": "podman", 
            "nerdctl": "nerdctl",
            "containerd": "ctr"
        }
        
        for engine, command in engine_commands.items():
            if self._test_engine_availability(command):
                engines.append(engine)
                
        return engines

    def get_recommended_engine(self) -> str:
        """Get the recommended engine based on capabilities."""
        available = self.get_available_engines()
        
        # Preference order: Docker > Podman > Nerdctl > Containerd
        preference_order = ["docker", "podman", "nerdctl", "containerd"]
        
        for engine in preference_order:
            if engine in available:
                return engine
                
        return "none"

    def validate_engine_requirements(self, requirements: Dict[str, bool]) -> Dict[str, Any]:
        """Validate that the current engine meets specific requirements."""
        if self.detected_engine == ContainerEngine.UNKNOWN:
            return {
                "valid": False,
                "missing": list(requirements.keys()),
                "message": "No container engine detected"
            }
        
        missing = []
        for requirement, needed in requirements.items():
            if needed and not self.capabilities.get(requirement, False):
                missing.append(requirement)
        
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "message": f"Missing capabilities: {', '.join(missing)}" if missing else "All requirements met"
        }