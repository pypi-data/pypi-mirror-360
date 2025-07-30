"""
Node.js Dockerfile Generator

This module provides specialized Dockerfile generation for Node.js applications,
with support for various package managers and frameworks.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class NodeJSDockerfileGenerator(BaseDockerfileGenerator):
    """
    Node.js Dockerfile Generator
    
    Supports:
    - npm, yarn, pnpm package managers
    - Next.js, React, Vue, Express, Fastify, NestJS frameworks
    - Multi-stage builds for production optimization
    - Security hardening with non-root users
    """
    
    def generate(self) -> str:
        """Generate optimized Node.js Dockerfile."""
        package_manager = self.get_package_manager()
        framework = self.get_framework()
        port = self.get_port()
        
        # Start with multi-stage build base
        self.add_comment("Multi-stage build for Node.js application")
        self.add_from("node:18-alpine", "linux/amd64")
        self.add_label("stage", "base")
        self.add_blank_line()
        
        # Dependencies stage
        self.add_comment("Install dependencies only when needed")
        self.add_from("base", platform="linux/amd64")
        self.add_label("stage", "deps")
        self.add_run("apk add --no-cache libc6-compat")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Install dependencies based on package manager
        self._add_dependency_installation(package_manager)
        self.add_blank_line()
        
        # Builder stage
        self.add_comment("Rebuild the source code only when needed")
        self.add_from("base", platform="linux/amd64")
        self.add_label("stage", "builder")
        self.add_workdir("/app")
        self.add_copy("--from=deps /app/node_modules ./node_modules")
        self.add_copy(". .")
        self.add_blank_line()
        
        # Build application if needed
        if self._should_build_app(framework):
            self.add_comment("Build application")
            build_cmd = self._get_build_command(framework)
            self.add_run(build_cmd)
            self.add_blank_line()
        
        # Production runtime stage
        self.add_comment("Production image, copy all the files and run the app")
        self.add_from("base", platform="linux/amd64")
        self.add_label("stage", "runner")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_performance_optimizations()
        self.add_blank_line()
        
        # Security hardening
        self.add_security_hardening()
        
        # Copy built application
        self._copy_built_application(framework)
        self.add_blank_line()
        
        # Switch to non-root user
        self.add_user("appuser")
        self.add_blank_line()
        
        # Expose port and set environment
        self.add_expose(port)
        self.add_env("PORT", str(port))
        self.add_blank_line()
        
        # Add health check
        self._add_health_check(port)
        self.add_blank_line()
        
        # Add standard labels
        self.add_standard_labels()
        self.add_blank_line()
        
        # Start command
        start_cmd = self._get_start_command(framework)
        self.add_cmd(start_cmd)
        
        return self.get_content()
    
    def _add_dependency_installation(self, package_manager: str):
        """Add package manager specific dependency installation."""
        if package_manager == "yarn":
            self.add_comment("Install dependencies based on yarn")
            self.add_copy("package.json yarn.lock* ./")
            self.add_run("yarn install --frozen-lockfile --production")
        elif package_manager == "pnpm":
            self.add_comment("Install dependencies based on pnpm")
            self.add_copy("package.json pnpm-lock.yaml* ./")
            self.add_run("corepack enable pnpm")
            self.add_run("pnpm install --frozen-lockfile --prod")
        else:  # npm
            self.add_comment("Install dependencies based on npm")
            self.add_copy("package.json package-lock.json* ./")
            self.add_run("npm ci --only=production")
    
    def _should_build_app(self, framework: str) -> bool:
        """Determine if the application needs a build step."""
        build_frameworks = ["nextjs", "react", "vue", "svelte", "nuxt"]
        return framework in build_frameworks
    
    def _get_build_command(self, framework: str) -> str:
        """Get the appropriate build command for the framework."""
        build_commands = {
            "nextjs": "npm run build",
            "react": "npm run build", 
            "vue": "npm run build",
            "svelte": "npm run build",
            "nuxt": "npm run build"
        }
        return build_commands.get(framework, "npm run build")
    
    def _copy_built_application(self, framework: str):
        """Copy the built application files based on framework."""
        if framework == "nextjs":
            self.add_comment("Copy Next.js application")
            self.add_copy("--from=builder /app/public ./public")
            self.add_copy("--from=builder --chown=appuser:appgroup /app/.next/standalone ./")
            self.add_copy("--from=builder --chown=appuser:appgroup /app/.next/static ./.next/static")
        elif framework in ["react", "vue", "svelte"]:
            self.add_comment("Copy built static files")
            self.add_copy("--from=builder /app/build ./build")
            self.add_copy("--from=builder /app/package.json ./package.json")
        elif framework == "nuxt":
            self.add_comment("Copy Nuxt.js application")
            self.add_copy("--from=builder /app/.output ./.output")
        else:
            self.add_comment("Copy application files")
            self.add_copy("--from=builder --chown=appuser:appgroup /app .")
    
    def _get_start_command(self, framework: str) -> str:
        """Get the appropriate start command for the framework."""
        start_commands = {
            "nextjs": '["node", "server.js"]',
            "react": '["npx", "serve", "-s", "build", "-l", "3000"]',
            "vue": '["npx", "serve", "-s", "dist", "-l", "8080"]',
            "express": '["node", "server.js"]',
            "fastify": '["node", "server.js"]',
            "nestjs": '["node", "dist/main.js"]',
            "svelte": '["node", "build"]',
            "nuxt": '["node", ".output/server/index.mjs"]'
        }
        return start_commands.get(framework, '["npm", "start"]')
    
    def _add_health_check(self, port: int):
        """Add health check configuration."""
        health_test = f"curl --fail http://localhost:{port}/health || wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1"
        self.add_healthcheck(health_test, interval="30s", timeout="5s", retries=3)
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get Node.js specific optimization recommendations."""
        framework = self.get_framework()
        package_manager = self.get_package_manager()
        
        recommendations = {
            "multi_stage_build": True,
            "node_modules_caching": True,
            "production_dependencies_only": True,
            "framework_optimizations": []
        }
        
        if framework == "nextjs":
            recommendations["framework_optimizations"].extend([
                "Use standalone output for smaller image size",
                "Leverage Next.js built-in optimizations",
                "Enable compression and static file serving"
            ])
        elif framework in ["react", "vue"]:
            recommendations["framework_optimizations"].extend([
                "Use static file serving for production builds",
                "Enable gzip compression",
                "Consider using nginx for static file serving"
            ])
        
        if package_manager == "pnpm":
            recommendations["package_manager_benefits"] = [
                "Faster installs with content-addressable storage",
                "Smaller node_modules with symlinks",
                "Better dependency resolution"
            ]
        elif package_manager == "yarn":
            recommendations["package_manager_benefits"] = [
                "Deterministic installs with yarn.lock",
                "Faster parallel downloads",
                "Built-in workspaces support"
            ]
        
        return recommendations