"""
Go Dockerfile Generator

This module provides specialized Dockerfile generation for Go applications,
with multi-stage builds for minimal production images.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class GoDockerfileGenerator(BaseDockerfileGenerator):
    """
    Go Dockerfile Generator
    
    Supports:
    - Multi-stage builds for minimal production images
    - Static binary compilation
    - Security hardening with scratch/distroless base images
    - Go modules for dependency management
    """
    
    def generate(self) -> str:
        """Generate optimized Go Dockerfile."""
        port = self.get_port()
        
        # Always use multi-stage build for Go
        self.add_comment("Multi-stage build for Go application")
        
        # Builder stage
        self._add_builder_stage()
        self.add_blank_line()
        
        # Runtime stage
        self._add_runtime_stage(port)
        
        return self.get_content()
    
    def _add_builder_stage(self):
        """Add the builder stage for compiling Go application."""
        self.add_from("golang:1.21-alpine", platform="linux/amd64")
        self.add_label("stage", "builder")
        self.add_blank_line()
        
        # Install build dependencies
        self.add_comment("Install build dependencies")
        self.add_run("apk add --no-cache gcc musl-dev git ca-certificates")
        self.add_blank_line()
        
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Performance optimizations for build
        self.add_comment("Configure Go environment for optimal builds")
        self.add_env("CGO_ENABLED", "0")
        self.add_env("GOOS", "linux")
        self.add_env("GOARCH", "amd64")
        self.add_blank_line()
        
        # Download dependencies first for better caching
        self.add_comment("Download dependencies")
        self.add_copy("go.mod go.sum ./")
        self.add_run("go mod download")
        self.add_run("go mod verify")
        self.add_blank_line()
        
        # Copy source code
        self.add_comment("Copy source code")
        self.add_copy(". .")
        self.add_blank_line()
        
        # Build the application with optimizations
        self.add_comment("Build the application")
        build_flags = [
            "-a",
            "-installsuffix", "cgo",
            "-ldflags", "\"-w -s -extldflags '-static'\"",
            "-o", "main", "."
        ]
        self.add_run(f"go build {' '.join(build_flags)}")
        self.add_blank_line()
        
        # Verify the binary
        self.add_comment("Verify the binary")
        self.add_run("./main --version || true")
    
    def _add_runtime_stage(self, port: int):
        """Add the runtime stage using minimal base image."""
        # Use distroless for better security while maintaining basic utilities
        self.add_comment("Runtime stage - minimal image for security")
        self.add_from("gcr.io/distroless/static-debian11:nonroot")
        self.add_blank_line()
        
        # Copy CA certificates from builder
        self.add_comment("Copy CA certificates")
        self.add_copy("--from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/")
        self.add_blank_line()
        
        # Copy the binary from builder stage
        self.add_comment("Copy the binary from builder stage")
        self.add_copy("--from=builder /app/main /main")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_comment("Runtime configuration")
        self.add_env("GIN_MODE", "release")  # For Gin framework
        self.add_env("GO_ENV", "production")
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
        
        # Start command
        self.add_entrypoint('["/main"]')
    
    def _add_health_check(self, port: int):
        """Add health check configuration for Go applications."""
        # Note: distroless doesn't have curl, so we rely on the app's own health endpoint
        health_test = f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1"
        self.add_comment("Note: Health check requires the application to expose /health endpoint")
        # We comment this out for distroless images as they don't have wget/curl
        self.add_comment(f"HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD {health_test}")
    
    def generate_with_alpine_runtime(self) -> str:
        """Generate Go Dockerfile with Alpine runtime instead of distroless."""
        port = self.get_port()
        
        # Reset content
        self.dockerfile_content = []
        
        # Builder stage (same as above)
        self.add_comment("Multi-stage build for Go application")
        self._add_builder_stage()
        self.add_blank_line()
        
        # Alpine runtime stage
        self.add_comment("Runtime stage - Alpine for debugging capabilities")
        self.add_from("alpine:latest")
        self.add_blank_line()
        
        # Install runtime dependencies
        self.add_comment("Install runtime dependencies")
        self.add_run("apk --no-cache add ca-certificates curl")
        self.add_blank_line()
        
        self.add_workdir("/root/")
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        
        # Copy the binary from builder stage
        self.add_comment("Copy the binary from builder stage")
        self.add_copy("--from=builder /app/main .")
        self.add_run("chown appuser:appgroup main")
        self.add_blank_line()
        
        # Switch to non-root user
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Add health check
        health_test = f"curl --fail http://localhost:{port}/health || exit 1"
        self.add_healthcheck(health_test, interval="30s", timeout="5s", retries=3)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command
        self.add_cmd('["./main"]')
        
        return self.get_content()
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get Go specific optimization recommendations."""
        return {
            "multi_stage_build": True,
            "static_binary": True,
            "minimal_runtime": True,
            "build_optimizations": [
                "Use CGO_ENABLED=0 for static binaries",
                "Leverage Go modules for dependency caching",
                "Use build flags to reduce binary size",
                "Enable compile-time optimizations"
            ],
            "runtime_options": {
                "distroless": {
                    "pros": ["Minimal attack surface", "No shell", "Very small image"],
                    "cons": ["No debugging tools", "No shell access", "Limited health checks"]
                },
                "alpine": {
                    "pros": ["Small size", "Has shell and basic tools", "Easy debugging"],
                    "cons": ["Slightly larger than distroless", "More attack surface"]
                },
                "scratch": {
                    "pros": ["Smallest possible image", "Maximum security"],
                    "cons": ["No CA certificates", "No shell", "Difficult debugging"]
                }
            },
            "security_benefits": [
                "Static binaries eliminate dependency vulnerabilities",
                "Minimal runtime reduces attack surface",
                "Non-root user execution",
                "No package manager in final image"
            ],
            "framework_optimizations": {
                "gin": ["Set GIN_MODE=release", "Enable request logging"],
                "echo": ["Use Echo's built-in middleware", "Configure CORS properly"],
                "fiber": ["Enable Fiber's built-in compression", "Use proper error handling"]
            }
        }