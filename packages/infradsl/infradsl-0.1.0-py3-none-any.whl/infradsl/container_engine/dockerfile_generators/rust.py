"""
Rust Dockerfile Generator

This module provides specialized Dockerfile generation for Rust applications,
with multi-stage builds for minimal production images.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class RustDockerfileGenerator(BaseDockerfileGenerator):
    """
    Rust Dockerfile Generator
    
    Supports:
    - Multi-stage builds for minimal production images
    - Cargo dependency caching optimization
    - Security hardening with minimal runtime
    - Popular frameworks like Actix-web, Warp, Rocket
    """
    
    def generate(self) -> str:
        """Generate optimized Rust Dockerfile."""
        port = self.get_port()
        
        # Always use multi-stage build for Rust
        self.add_comment("Multi-stage build for Rust application")
        
        # Builder stage
        self._add_builder_stage()
        self.add_blank_line()
        
        # Runtime stage
        self._add_runtime_stage(port)
        
        return self.get_content()
    
    def _add_builder_stage(self):
        """Add the builder stage for compiling Rust application."""
        self.add_from("rust:1.70-alpine", platform="linux/amd64")
        self.add_label("stage", "builder")
        self.add_blank_line()
        
        # Install build dependencies
        self.add_comment("Install build dependencies")
        self.add_run("apk add --no-cache musl-dev pkgconfig openssl-dev")
        self.add_blank_line()
        
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Optimize Rust build environment
        self.add_comment("Configure Rust environment for optimal builds")
        self.add_env("RUSTFLAGS", "-C target-cpu=native")
        self.add_env("CARGO_NET_GIT_FETCH_WITH_CLI", "true")
        self.add_blank_line()
        
        # Copy manifest files first for better dependency caching
        self.add_comment("Copy manifest files for dependency caching")
        self.add_copy("Cargo.toml Cargo.lock ./")
        self.add_blank_line()
        
        # Create dummy src/main.rs for dependency building
        self.add_comment("Create dummy source for dependency caching")
        self.add_run("mkdir src")
        self.add_run("echo 'fn main() { println!(\"Building dependencies...\"); }' > src/main.rs")
        self.add_blank_line()
        
        # Build dependencies only
        self.add_comment("Build dependencies")
        self.add_run("cargo build --release")
        self.add_run("rm src/main.rs")
        self.add_blank_line()
        
        # Copy actual source code
        self.add_comment("Copy source code")
        self.add_copy("src ./src")
        self.add_blank_line()
        
        # Build the actual application
        self.add_comment("Build the application")
        self.add_run("cargo build --release")
        self.add_blank_line()
        
        # Strip the binary to reduce size
        self.add_comment("Strip binary to reduce size")
        self.add_run("strip target/release/*")
    
    def _add_runtime_stage(self, port: int):
        """Add the runtime stage using minimal base image."""
        # Use Alpine for minimal runtime with SSL support
        self.add_comment("Runtime stage - minimal Alpine image")
        self.add_from("alpine:latest")
        self.add_blank_line()
        
        # Install minimal runtime dependencies
        self.add_comment("Install runtime dependencies")
        self.add_run("apk --no-cache add ca-certificates libgcc")
        self.add_blank_line()
        
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        
        # Copy the binary from builder stage
        self.add_comment("Copy the binary from builder stage")
        binary_name = self._get_binary_name()
        self.add_copy(f"--from=builder --chown=appuser:appgroup /app/target/release/{binary_name} ./app")
        self.add_blank_line()
        
        # Switch to non-root user
        self.add_user("appuser")
        self.add_blank_line()
        
        # Runtime optimizations
        self.add_comment("Runtime configuration")
        self.add_env("RUST_LOG", "info")
        self.add_env("RUST_BACKTRACE", "1")
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
        self.add_cmd('["./app"]')
    
    def _get_binary_name(self) -> str:
        """Get the binary name from project info or use default."""
        project_name = self.project_info.get("name", "app")
        # Replace hyphens with underscores as Rust does for binary names
        return project_name.replace("-", "_")
    
    def _add_health_check(self, port: int):
        """Add health check configuration."""
        framework = self.get_framework()
        
        if framework in ["actix-web", "warp", "rocket"]:
            health_test = f"wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1"
        else:
            health_test = f"wget --no-verbose --tries=1 --spider http://localhost:{port}/ || exit 1"
        
        self.add_healthcheck(health_test, interval="30s", timeout="5s", retries=3)
    
    def generate_with_distroless_runtime(self) -> str:
        """Generate Rust Dockerfile with distroless runtime for maximum security."""
        port = self.get_port()
        
        # Reset content
        self.dockerfile_content = []
        
        # Builder stage (same as above)
        self.add_comment("Multi-stage build for Rust application")
        self._add_builder_stage()
        self.add_blank_line()
        
        # Distroless runtime stage
        self.add_comment("Runtime stage - distroless for maximum security")
        self.add_from("gcr.io/distroless/cc-debian11:nonroot")
        self.add_blank_line()
        
        # Copy the binary from builder stage
        self.add_comment("Copy the binary from builder stage")
        binary_name = self._get_binary_name()
        self.add_copy(f"--from=builder /app/target/release/{binary_name} /app")
        self.add_blank_line()
        
        # Runtime configuration
        self.add_env("RUST_LOG", "info")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Note about health check limitation
        self.add_comment("Note: Distroless images don't support traditional health checks")
        self.add_comment("Consider using Kubernetes readiness/liveness probes instead")
        self.add_blank_line()
        
        # Start command
        self.add_entrypoint('["/app"]')
        
        return self.get_content()
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get Rust specific optimization recommendations."""
        framework = self.get_framework()
        
        recommendations = {
            "multi_stage_build": True,
            "dependency_caching": True,
            "binary_stripping": True,
            "build_optimizations": [
                "Use dummy main.rs for dependency caching",
                "Enable release mode optimizations",
                "Use target-cpu=native for performance",
                "Strip binaries to reduce size"
            ],
            "runtime_options": {
                "alpine": {
                    "pros": ["Small size", "Has shell and debugging tools", "Easy health checks"],
                    "cons": ["Slightly larger than distroless", "More dependencies"]
                },
                "distroless": {
                    "pros": ["Minimal attack surface", "Very secure", "Small size"],
                    "cons": ["No shell", "No health check tools", "Harder debugging"]
                }
            },
            "security_benefits": [
                "Static binary eliminates runtime dependencies",
                "Minimal runtime reduces attack surface",
                "Memory safety from Rust language",
                "No package manager in final image"
            ]
        }
        
        if framework:
            framework_opts = {
                "actix-web": [
                    "Use Actix's built-in middleware",
                    "Enable compression middleware",
                    "Configure proper error handling",
                    "Use async runtime optimizations"
                ],
                "warp": [
                    "Leverage Warp's filter system",
                    "Use built-in JSON handling",
                    "Enable request logging",
                    "Configure CORS properly"
                ],
                "rocket": [
                    "Use Rocket's built-in features",
                    "Enable JSON support",
                    "Configure proper error catchers",
                    "Use Rocket's async support"
                ]
            }
            recommendations["framework_optimizations"] = framework_opts.get(framework, [])
        
        recommendations["cargo_optimizations"] = [
            "Use cargo-chef for better Docker layer caching",
            "Enable incremental compilation for development",
            "Use workspace optimization for multi-crate projects",
            "Consider using cargo-auditable for supply chain security"
        ]
        
        return recommendations