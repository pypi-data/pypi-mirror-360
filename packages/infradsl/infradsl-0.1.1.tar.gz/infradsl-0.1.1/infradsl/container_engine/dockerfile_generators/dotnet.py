"""
.NET Dockerfile Generator

This module provides specialized Dockerfile generation for .NET applications,
with multi-stage builds and ASP.NET Core optimizations.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class DotNetDockerfileGenerator(BaseDockerfileGenerator):
    """
    .NET Dockerfile Generator
    
    Supports:
    - ASP.NET Core applications
    - Multi-stage builds for smaller production images
    - Runtime optimization for container environments
    - Security hardening with non-root users
    """
    
    def generate(self) -> str:
        """Generate optimized .NET Dockerfile."""
        port = self.get_port()
        
        # Always use multi-stage build for .NET
        self.add_comment("Multi-stage build for .NET application")
        
        # Builder stage
        self._add_builder_stage()
        self.add_blank_line()
        
        # Runtime stage
        self._add_runtime_stage(port)
        
        return self.get_content()
    
    def _add_builder_stage(self):
        """Add the builder stage for building .NET application."""
        self.add_from("mcr.microsoft.com/dotnet/sdk:7.0-alpine", platform="linux/amd64")
        self.add_label("stage", "builder")
        self.add_blank_line()
        
        self.add_workdir("/src")
        self.add_blank_line()
        
        # Copy project files and restore dependencies
        self.add_comment("Copy project files and restore dependencies")
        self.add_copy("*.csproj ./")
        self.add_copy("*.sln* ./")
        self.add_run("dotnet restore")
        self.add_blank_line()
        
        # Copy source code and build
        self.add_comment("Copy source code and build")
        self.add_copy(". .")
        self.add_run("dotnet publish -c Release -o /app/publish --no-restore")
        self.add_blank_line()
        
        # Optional: Run tests
        self.add_comment("Optional: Run tests (uncomment if needed)")
        self.add_comment("RUN dotnet test --no-restore --verbosity normal")
    
    def _add_runtime_stage(self, port: int):
        """Add the runtime stage for running the .NET application."""
        # Use ASP.NET Core runtime image
        self.add_comment("Runtime stage")
        self.add_from("mcr.microsoft.com/dotnet/aspnet:7.0-alpine")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Install runtime dependencies
        self.add_comment("Install runtime dependencies")
        self.add_run("apk add --no-cache curl icu-libs")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_performance_optimizations()
        self.add_blank_line()
        
        # Globalization settings
        self.add_comment("Configure globalization")
        self.add_env("DOTNET_SYSTEM_GLOBALIZATION_INVARIANT", "false")
        self.add_env("LC_ALL", "en_US.UTF-8")
        self.add_env("LANG", "en_US.UTF-8")
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        
        # Copy published app from builder
        self.add_comment("Copy published app")
        self.add_copy("--from=builder --chown=appuser:appgroup /app/publish .")
        self.add_blank_line()
        
        # Switch to non-root user
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Add health check
        self._add_health_check(port)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Configure ASP.NET Core to bind to the correct port
        self.add_env("ASPNETCORE_URLS", f"http://+:{port}")
        self.add_blank_line()
        
        # Start command
        self._add_start_command()
    
    def _add_start_command(self):
        """Add the appropriate start command for the .NET application."""
        # Try to detect the main assembly name
        project_name = self.project_info.get("name", "app")
        
        # Common patterns for .NET entry points
        possible_dlls = [
            f"{project_name}.dll",
            "app.dll",
            "main.dll"
        ]
        
        # Use the project name if available, otherwise default to app.dll
        main_dll = possible_dlls[0] if project_name != "app" else "app.dll"
        
        self.add_entrypoint(f'["dotnet", "{main_dll}"]')
    
    def _add_health_check(self, port: int):
        """Add health check configuration for ASP.NET Core."""
        # ASP.NET Core typically has health checks at /health or /healthz
        health_test = f"curl --fail http://localhost:{port}/health || curl --fail http://localhost:{port}/healthz || exit 1"
        self.add_healthcheck(health_test, interval="30s", timeout="10s", retries=3)
    
    def generate_for_minimal_api(self) -> str:
        """Generate optimized Dockerfile for .NET Minimal APIs."""
        port = self.get_port()
        
        # Reset content
        self.dockerfile_content = []
        
        self.add_comment("Multi-stage build for .NET Minimal API")
        
        # Use the same builder stage
        self._add_builder_stage()
        self.add_blank_line()
        
        # Minimal runtime stage
        self.add_comment("Minimal runtime stage")
        self.add_from("mcr.microsoft.com/dotnet/aspnet:7.0-alpine")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Minimal dependencies
        self.add_comment("Install minimal runtime dependencies")
        self.add_run("apk add --no-cache curl")
        self.add_blank_line()
        
        # Performance optimizations for minimal APIs
        self.add_comment("Configure for minimal API performance")
        self.add_env("ASPNETCORE_ENVIRONMENT", "Production")
        self.add_env("DOTNET_USE_POLLING_FILE_WATCHER", "true")
        self.add_env("DOTNET_RUNNING_IN_CONTAINER", "true")
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        
        # Copy published app
        self.add_copy("--from=builder --chown=appuser:appgroup /app/publish .")
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_env("ASPNETCORE_URLS", f"http://+:{port}")
        self.add_blank_line()
        
        # Health check for minimal API
        health_test = f"curl --fail http://localhost:{port}/ || exit 1"
        self.add_healthcheck(health_test, interval="30s", timeout="5s", retries=3)
        self.add_blank_line()
        
        # Standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command
        self._add_start_command()
        
        return self.get_content()
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get .NET specific optimization recommendations."""
        return {
            "multi_stage_build": True,
            "runtime_optimization": True,
            "dependency_restoration": True,
            "build_optimizations": [
                "Use dotnet restore for dependency caching",
                "Enable ReadyToRun compilation for faster startup",
                "Use trimming for smaller deployment size",
                "Consider AOT compilation for minimal APIs"
            ],
            "runtime_optimizations": [
                "Use ASP.NET Core runtime image for web apps",
                "Configure container-aware garbage collection",
                "Enable server garbage collection mode",
                "Use tiered compilation for better performance"
            ],
            "security_recommendations": [
                "Run as non-root user",
                "Use minimal runtime dependencies",
                "Enable HTTPS in production",
                "Configure proper CORS policies"
            ],
            "aspnet_core_features": [
                "Use built-in health checks",
                "Enable request logging middleware",
                "Configure proper exception handling",
                "Use dependency injection container"
            ],
            "container_optimizations": [
                "Set ASPNETCORE_URLS to bind to all interfaces",
                "Configure DOTNET_RUNNING_IN_CONTAINER=true",
                "Use proper globalization settings",
                "Enable container-aware resource limits"
            ],
            "deployment_patterns": {
                "web_api": "Full ASP.NET Core runtime with MVC features",
                "minimal_api": "Lightweight runtime with minimal dependencies",
                "blazor": "Enhanced runtime with SignalR and WebAssembly support",
                "grpc": "Optimized for gRPC services with HTTP/2"
            }
        }