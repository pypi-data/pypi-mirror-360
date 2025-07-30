"""
Base Dockerfile Generator

This module provides the base class for all Dockerfile generators,
with common functionality and template methods.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class BaseDockerfileGenerator(ABC):
    """
    Base class for all Dockerfile generators.
    
    This class provides common functionality and defines the interface
    that all specific generators must implement.
    """
    
    def __init__(self, project_info: Dict[str, Any]):
        """Initialize the generator with project information"""
        self.project_info = project_info
        self.dockerfile_content = []
    
    @abstractmethod
    def generate(self) -> str:
        """Generate the Dockerfile content. Must be implemented by subclasses."""
        pass
    
    def add_from(self, base_image: str, platform: str = None):
        """Add FROM instruction"""
        if platform:
            self.dockerfile_content.append(f"FROM --platform={platform} {base_image}")
        else:
            self.dockerfile_content.append(f"FROM {base_image}")
    
    def add_workdir(self, path: str = "/app"):
        """Add WORKDIR instruction"""
        self.dockerfile_content.append(f"WORKDIR {path}")
    
    def add_copy(self, src: str, dest: str, chown: str = None):
        """Add COPY instruction"""
        if chown:
            self.dockerfile_content.append(f"COPY --chown={chown} {src} {dest}")
        else:
            self.dockerfile_content.append(f"COPY {src} {dest}")
    
    def add_run(self, command: str):
        """Add RUN instruction"""
        self.dockerfile_content.append(f"RUN {command}")
    
    def add_run_multi(self, commands: list):
        """Add RUN instruction with multiple commands"""
        if not commands:
            return
        
        if len(commands) == 1:
            self.add_run(commands[0])
        else:
            command_str = " && \\\n    ".join(commands)
            self.dockerfile_content.append(f"RUN {command_str}")
    
    def add_expose(self, port: int):
        """Add EXPOSE instruction"""
        self.dockerfile_content.append(f"EXPOSE {port}")
    
    def add_env(self, key: str, value: str):
        """Add ENV instruction"""
        self.dockerfile_content.append(f'ENV {key}="{value}"')
    
    def add_env_multi(self, env_vars: Dict[str, str]):
        """Add multiple ENV instructions"""
        for key, value in env_vars.items():
            self.add_env(key, value)
    
    def add_user(self, user: str):
        """Add USER instruction"""
        self.dockerfile_content.append(f"USER {user}")
    
    def add_cmd(self, command: str):
        """Add CMD instruction"""
        self.dockerfile_content.append(f'CMD {command}')
    
    def add_entrypoint(self, command: str):
        """Add ENTRYPOINT instruction"""
        self.dockerfile_content.append(f'ENTRYPOINT {command}')
    
    def add_healthcheck(self, test: str, interval: str = "30s", timeout: str = "3s", retries: int = 3):
        """Add HEALTHCHECK instruction"""
        self.dockerfile_content.append(
            f"HEALTHCHECK --interval={interval} --timeout={timeout} --retries={retries} "
            f"CMD {test}"
        )
    
    def add_label(self, key: str, value: str):
        """Add LABEL instruction"""
        self.dockerfile_content.append(f'LABEL {key}="{value}"')
    
    def add_labels(self, labels: Dict[str, str]):
        """Add multiple LABEL instructions"""
        for key, value in labels.items():
            self.add_label(key, value)
    
    def add_comment(self, comment: str):
        """Add a comment"""
        self.dockerfile_content.append(f"# {comment}")
    
    def add_blank_line(self):
        """Add a blank line for readability"""
        self.dockerfile_content.append("")
    
    def get_content(self) -> str:
        """Get the complete Dockerfile content"""
        return "\n".join(self.dockerfile_content)
    
    def get_base_image(self) -> str:
        """Get the recommended base image"""
        return self.project_info.get("suggested_base_image", "alpine:latest")
    
    def get_port(self) -> int:
        """Get the recommended port"""
        return self.project_info.get("suggested_port", 8080)
    
    def get_framework(self) -> str:
        """Get the detected framework"""
        return self.project_info.get("framework", "")
    
    def get_package_manager(self) -> str:
        """Get the detected package manager"""
        return self.project_info.get("package_manager", "")
    
    def should_use_multi_stage(self) -> bool:
        """Determine if multi-stage build should be used"""
        # Use multi-stage for compiled languages or when explicitly configured
        compiled_languages = ["go", "rust", "java", "dotnet"]
        return self.project_info.get("type") in compiled_languages
    
    def add_security_hardening(self):
        """Add common security hardening steps"""
        self.add_comment("Security hardening")
        self.add_run("addgroup -g 1001 -S appgroup")
        self.add_run("adduser -u 1001 -S appuser -G appgroup")
        self.add_blank_line()
    
    def add_performance_optimizations(self):
        """Add common performance optimizations"""
        project_type = self.project_info.get("type", "")
        
        if project_type == "nodejs":
            self.add_env("NODE_ENV", "production")
        elif project_type == "python":
            self.add_env("PYTHONUNBUFFERED", "1")
            self.add_env("PYTHONDONTWRITEBYTECODE", "1")
        elif project_type == "java":
            self.add_env("JAVA_OPTS", "-Xmx512m -XX:+UseContainerSupport")
        elif project_type == "dotnet":
            self.add_env("ASPNETCORE_ENVIRONMENT", "Production")
    
    def add_standard_labels(self):
        """Add standard OCI labels"""
        labels = {
            "org.opencontainers.image.created": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
            "org.opencontainers.image.title": self.project_info.get("name", "app"),
            "org.opencontainers.image.description": f"{self.project_info.get('type', 'unknown')} application",
            "org.opencontainers.image.source": "generated-by-infradsl"
        }
        self.add_labels(labels)