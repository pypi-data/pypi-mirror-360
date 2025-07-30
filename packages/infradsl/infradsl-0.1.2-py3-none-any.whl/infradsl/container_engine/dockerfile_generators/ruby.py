"""
Ruby Dockerfile Generator

This module provides specialized Dockerfile generation for Ruby applications,
with support for Rails and other frameworks.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class RubyDockerfileGenerator(BaseDockerfileGenerator):
    """
    Ruby Dockerfile Generator
    
    Supports:
    - Ruby on Rails framework
    - Sinatra framework
    - Bundler for dependency management
    - Multi-stage builds for asset compilation
    - Security hardening with non-root users
    """
    
    def generate(self) -> str:
        """Generate optimized Ruby Dockerfile."""
        framework = self.get_framework()
        port = self.get_port()
        
        if framework == "rails" and self._should_use_multi_stage():
            return self._generate_rails_multi_stage_dockerfile(port)
        else:
            return self._generate_single_stage_dockerfile(framework, port)
    
    def _generate_single_stage_dockerfile(self, framework: str, port: int) -> str:
        """Generate single-stage Ruby Dockerfile."""
        self.add_comment("Ruby application")
        self.add_from("ruby:3.2-alpine")
        self.add_blank_line()
        
        # Install system dependencies
        self._add_system_dependencies(framework)
        
        # Set working directory
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_comment("Configure Ruby environment")
        self.add_env("BUNDLE_APP_CONFIG", "/app/.bundle")
        self.add_env("BUNDLE_PATH", "/app/vendor/bundle")
        self.add_env("BUNDLE_WITHOUT", "development:test")
        self.add_blank_line()
        
        # Install Ruby dependencies
        self._add_dependency_installation()
        
        # Copy application code
        self.add_comment("Copy application code")
        self.add_copy(". .")
        self.add_blank_line()
        
        # Framework-specific setup
        self._add_framework_setup(framework)
        
        # Security hardening
        self.add_security_hardening()
        
        # Switch to non-root user
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Add health check
        self._add_health_check(port, framework)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command
        start_cmd = self._get_start_command(framework)
        self.add_cmd(start_cmd)
        
        return self.get_content()
    
    def _generate_rails_multi_stage_dockerfile(self, port: int) -> str:
        """Generate multi-stage Rails Dockerfile with asset compilation."""
        # Reset content for multi-stage build
        self.dockerfile_content = []
        
        self.add_comment("Multi-stage build for Rails application")
        
        # Base stage with common dependencies
        self.add_from("ruby:3.2-alpine", platform="linux/amd64")
        self.add_label("stage", "base")
        self.add_blank_line()
        
        # Install system dependencies
        self._add_system_dependencies("rails")
        
        self.add_workdir("/app")
        self.add_env("BUNDLE_APP_CONFIG", "/app/.bundle")
        self.add_env("BUNDLE_PATH", "/app/vendor/bundle")
        self.add_blank_line()
        
        # Dependencies stage
        self.add_comment("Dependencies stage")
        self.add_from("base", platform="linux/amd64")
        self.add_label("stage", "dependencies")
        self.add_blank_line()
        
        self._add_dependency_installation()
        self.add_blank_line()
        
        # Assets stage for Rails
        self.add_comment("Assets compilation stage")
        self.add_from("dependencies", platform="linux/amd64")
        self.add_label("stage", "assets")
        self.add_blank_line()
        
        # Install Node.js for asset compilation
        self.add_comment("Install Node.js for asset compilation")
        self.add_run("apk add --no-cache nodejs npm yarn")
        self.add_blank_line()
        
        self.add_copy(". .")
        self.add_blank_line()
        
        # Compile Rails assets
        self.add_comment("Compile Rails assets")
        self.add_env("RAILS_ENV", "production")
        self.add_env("SECRET_KEY_BASE", "dummy")
        self.add_run("bundle exec rails assets:precompile")
        self.add_blank_line()
        
        # Production stage
        self.add_comment("Production stage")
        self.add_from("base", platform="linux/amd64")
        self.add_blank_line()
        
        # Copy dependencies from dependencies stage
        self.add_copy("--from=dependencies /app/vendor/bundle /app/vendor/bundle")
        self.add_copy("--from=dependencies /app/.bundle /app/.bundle")
        self.add_blank_line()
        
        # Copy application with compiled assets
        self.add_copy("--from=assets /app .")
        self.add_blank_line()
        
        # Rails-specific configuration
        self.add_env("RAILS_ENV", "production")
        self.add_env("RAILS_SERVE_STATIC_FILES", "true")
        self.add_env("RAILS_LOG_TO_STDOUT", "true")
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port
        self.add_expose(port)
        self.add_blank_line()
        
        # Health check
        self._add_health_check(port, "rails")
        self.add_blank_line()
        
        # Standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command
        self.add_cmd('["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]')
        
        return self.get_content()
    
    def _add_system_dependencies(self, framework: str):
        """Add system dependencies based on framework."""
        self.add_comment("Install system dependencies")
        
        # Base dependencies
        deps = ["build-base", "git", "curl", "tzdata"]
        
        # Framework-specific dependencies
        if framework == "rails":
            deps.extend([
                "postgresql-dev", "mysql-dev", "sqlite-dev",
                "imagemagick-dev", "libxml2-dev", "libxslt-dev"
            ])
        
        self.add_run(f"apk add --no-cache {' '.join(deps)}")
        self.add_blank_line()
    
    def _add_dependency_installation(self):
        """Add Bundler dependency installation."""
        self.add_comment("Install Ruby dependencies")
        self.add_copy("Gemfile Gemfile.lock ./")
        
        # Configure Bundler for production
        self.add_run("bundle config set --local deployment 'true'")
        self.add_run("bundle config set --local without 'development test'")
        self.add_run("bundle install --jobs 4 --retry 3")
        self.add_blank_line()
    
    def _add_framework_setup(self, framework: str):
        """Add framework-specific setup commands."""
        if framework == "rails":
            self.add_comment("Rails-specific setup")
            self.add_env("RAILS_ENV", "production")
            self.add_env("RAILS_SERVE_STATIC_FILES", "true")
            self.add_env("RAILS_LOG_TO_STDOUT", "true")
            self.add_blank_line()
            
            # Database setup (commented out as it requires database connection)
            self.add_comment("Database setup (uncomment if needed)")
            self.add_comment("RUN bundle exec rails db:create db:migrate")
        elif framework == "sinatra":
            self.add_comment("Sinatra-specific setup")
            self.add_env("RACK_ENV", "production")
        
        self.add_blank_line()
    
    def _get_start_command(self, framework: str) -> str:
        """Get the appropriate start command for the framework."""
        if framework == "rails":
            return '["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]'
        elif framework == "sinatra":
            return '["bundle", "exec", "ruby", "app.rb", "-o", "0.0.0.0"]'
        else:
            return '["bundle", "exec", "ruby", "app.rb"]'
    
    def _add_health_check(self, port: int, framework: str):
        """Add health check configuration."""
        if framework == "rails":
            health_test = f"curl --fail http://localhost:{port}/health || curl --fail http://localhost:{port}/ || exit 1"
        else:
            health_test = f"curl --fail http://localhost:{port}/ || exit 1"
        
        self.add_healthcheck(health_test, interval="30s", timeout="10s", retries=3)
    
    def _should_use_multi_stage(self) -> bool:
        """Determine if multi-stage build should be used for Rails."""
        # Use multi-stage for Rails applications to optimize asset compilation
        return True
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get Ruby specific optimization recommendations."""
        framework = self.get_framework()
        
        recommendations = {
            "multi_stage_build": framework == "rails",
            "bundler_optimization": True,
            "asset_compilation": framework == "rails",
            "framework_optimizations": []
        }
        
        if framework == "rails":
            recommendations["framework_optimizations"].extend([
                "Use asset precompilation for production",
                "Enable Rails caching in production",
                "Configure proper database connection pooling",
                "Use ActionCable for WebSocket connections",
                "Enable Sprockets compression"
            ])
        elif framework == "sinatra":
            recommendations["framework_optimizations"].extend([
                "Use Sinatra's built-in caching",
                "Enable Rack middleware for compression",
                "Configure proper session storage",
                "Use Sinatra extensions for common features"
            ])
        
        recommendations["ruby_optimizations"] = [
            "Use Ruby 3.x for better performance",
            "Enable YJIT for just-in-time compilation",
            "Configure proper garbage collection",
            "Use Bootsnap for faster boot times"
        ]
        
        recommendations["bundler_optimizations"] = [
            "Use bundle config for production settings",
            "Exclude development/test gems in production",
            "Use bundle deployment mode",
            "Cache bundle install for faster builds"
        ]
        
        recommendations["security_recommendations"] = [
            "Run as non-root user",
            "Use secrets management for sensitive data",
            "Enable CSRF protection",
            "Configure proper CORS policies",
            "Use strong parameters in Rails"
        ]
        
        if framework == "rails":
            recommendations["rails_specific"] = {
                "asset_pipeline": [
                    "Use Sprockets for asset compilation",
                    "Enable asset compression and minification",
                    "Use CDN for static assets",
                    "Configure proper cache headers"
                ],
                "database": [
                    "Use database connection pooling",
                    "Configure read/write splitting",
                    "Use database migrations properly",
                    "Enable query caching"
                ],
                "caching": [
                    "Use Redis for session/cache storage",
                    "Enable fragment caching",
                    "Use Russian doll caching pattern",
                    "Configure HTTP caching headers"
                ]
            }
        
        return recommendations