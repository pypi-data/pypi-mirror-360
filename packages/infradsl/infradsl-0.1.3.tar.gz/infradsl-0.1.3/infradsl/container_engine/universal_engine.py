"""
Universal Container Engine - Legacy Version

This is the original monolithic implementation. It has been refactored into modular components.
For new development, use the refactored version in universal_engine_refactored.py

Intelligent container runtime detection and management with Rails-like conventions.
Automatically detects and works with Docker, Podman, containerd, or any available container engine.
"""

import os
import subprocess
import shutil
import json
import platform
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from enum import Enum


class ContainerEngine(Enum):
    DOCKER = "docker"
    PODMAN = "podman"
    CONTAINERD = "containerd"
    NERDCTL = "nerdctl"
    UNKNOWN = "unknown"


class UniversalContainerEngineLegacy:
    """
    Universal Container Engine with intelligent runtime detection - LEGACY VERSION.
    
    This is the original monolithic implementation that has been refactored.
    Use UniversalContainerEngine from universal_engine_refactored.py for new development.

    Provides a unified interface for all container engines with Rails-like conventions.
    Automatically detects the best available container runtime and adapts accordingly.
    """

    def __init__(self, preferred_engine: Optional[str] = None):
        """
        Initialize Universal Container Engine.

        Args:
            preferred_engine: Preferred container engine (docker, podman, etc.)
        """
        self.preferred_engine = preferred_engine
        self.detected_engine = None
        self.engine_command = None
        self.engine_version = None
        self.capabilities = {}

        # Rails-like configuration
        self.auto_build_enabled = True
        self.auto_push_enabled = True
        self.auto_deploy_enabled = False
        self.build_context = "."
        self.dockerfile_path = "Dockerfile"
        self.image_registry = None
        self.image_tag = "latest"

        # Template system
        self.template_detected = None
        self.project_type = None
        self.framework = None

        # State management
        self.last_build_hash = None
        self.deployment_state = {}

        # Auto-detect container engine
        self._detect_container_engine()

    def _detect_container_engine(self) -> ContainerEngine:
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
                ["docker", "compose", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def _test_docker_buildx(self) -> bool:
        """Test if Docker BuildX is available."""
        try:
            result = subprocess.run(
                ["docker", "buildx", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def detect_project_type(self, path: str = ".") -> Dict[str, Any]:
        """
        Auto-detect project type and framework for intelligent container templates.

        Args:
            path: Path to analyze (default: current directory)

        Returns:
            Dict containing detected project information
        """
        project_path = Path(path)
        detected = {
            "type": "unknown",
            "framework": None,
            "language": None,
            "package_manager": None,
            "build_tool": None,
            "suggested_dockerfile": None,
            "suggested_base_image": None,
            "suggested_port": 3000
        }

        # Node.js detection
        if (project_path / "package.json").exists():
            detected["type"] = "nodejs"
            detected["language"] = "javascript"
            detected["package_manager"] = "npm"
            detected["suggested_base_image"] = "node:18-alpine"
            detected["suggested_port"] = 3000

            # Check for Yarn
            if (project_path / "yarn.lock").exists():
                detected["package_manager"] = "yarn"

            # Check for pnpm
            if (project_path / "pnpm-lock.yaml").exists():
                detected["package_manager"] = "pnpm"

            # Detect framework
            try:
                with open(project_path / "package.json", "r") as f:
                    package_json = json.load(f)
                    deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}

                    if "next" in deps:
                        detected["framework"] = "nextjs"
                        detected["suggested_port"] = 3000
                    elif "react" in deps:
                        detected["framework"] = "react"
                        detected["suggested_port"] = 3000
                    elif "vue" in deps:
                        detected["framework"] = "vue"
                        detected["suggested_port"] = 8080
                    elif "express" in deps:
                        detected["framework"] = "express"
                        detected["suggested_port"] = 3000
                    elif "fastify" in deps:
                        detected["framework"] = "fastify"
                        detected["suggested_port"] = 3000
                    elif "@nestjs/core" in deps:
                        detected["framework"] = "nestjs"
                        detected["suggested_port"] = 3000
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Python detection
        elif (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists() or (project_path / "Pipfile").exists():
            detected["type"] = "python"
            detected["language"] = "python"
            detected["suggested_base_image"] = "python:3.11-alpine"
            detected["suggested_port"] = 8000

            if (project_path / "requirements.txt").exists():
                detected["package_manager"] = "pip"
            elif (project_path / "Pipfile").exists():
                detected["package_manager"] = "pipenv"
            elif (project_path / "pyproject.toml").exists():
                detected["package_manager"] = "poetry"

            # Detect Python frameworks
            try:
                if (project_path / "requirements.txt").exists():
                    with open(project_path / "requirements.txt", "r") as f:
                        requirements = f.read().lower()
                        if "django" in requirements:
                            detected["framework"] = "django"
                            detected["suggested_port"] = 8000
                        elif "flask" in requirements:
                            detected["framework"] = "flask"
                            detected["suggested_port"] = 5000
                        elif "fastapi" in requirements:
                            detected["framework"] = "fastapi"
                            detected["suggested_port"] = 8000
            except FileNotFoundError:
                pass

        # Java detection
        elif (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            detected["type"] = "java"
            detected["language"] = "java"
            detected["suggested_base_image"] = "openjdk:17-alpine"
            detected["suggested_port"] = 8080

            if (project_path / "pom.xml").exists():
                detected["build_tool"] = "maven"
            elif (project_path / "build.gradle").exists():
                detected["build_tool"] = "gradle"

            # Detect Java frameworks
            if (project_path / "src/main/java").exists():
                detected["framework"] = "spring-boot"  # Assume Spring Boot for now

        # Go detection
        elif (project_path / "go.mod").exists():
            detected["type"] = "go"
            detected["language"] = "go"
            detected["suggested_base_image"] = "golang:1.21-alpine"
            detected["suggested_port"] = 8080
            detected["package_manager"] = "go-modules"

        # Rust detection
        elif (project_path / "Cargo.toml").exists():
            detected["type"] = "rust"
            detected["language"] = "rust"
            detected["suggested_base_image"] = "rust:1.70-alpine"
            detected["suggested_port"] = 8080
            detected["package_manager"] = "cargo"

        # .NET detection
        elif any((project_path / f).exists() for f in ["*.csproj", "*.sln", "global.json"]):
            detected["type"] = "dotnet"
            detected["language"] = "csharp"
            detected["suggested_base_image"] = "mcr.microsoft.com/dotnet/aspnet:7.0-alpine"
            detected["suggested_port"] = 80
            detected["build_tool"] = "dotnet"

        # PHP detection
        elif (project_path / "composer.json").exists():
            detected["type"] = "php"
            detected["language"] = "php"
            detected["suggested_base_image"] = "php:8.2-apache"
            detected["suggested_port"] = 80
            detected["package_manager"] = "composer"

        # Ruby detection
        elif (project_path / "Gemfile").exists():
            detected["type"] = "ruby"
            detected["language"] = "ruby"
            detected["suggested_base_image"] = "ruby:3.2-alpine"
            detected["suggested_port"] = 3000
            detected["package_manager"] = "bundler"

            # Check for Rails
            try:
                with open(project_path / "Gemfile", "r") as f:
                    gemfile = f.read()
                    if "rails" in gemfile.lower():
                        detected["framework"] = "rails"
            except FileNotFoundError:
                pass

        self.project_type = detected["type"]
        self.framework = detected["framework"]
        self.template_detected = detected

        return detected

    def generate_dockerfile(self, project_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate an optimized Dockerfile based on detected project type.

        Args:
            project_info: Project information (auto-detected if not provided)

        Returns:
            Generated Dockerfile content
        """
        if not project_info:
            project_info = self.detect_project_type()

        project_type = project_info["type"]
        framework = project_info.get("framework")
        base_image = project_info["suggested_base_image"]
        port = project_info["suggested_port"]

        if project_type == "nodejs":
            return self._generate_nodejs_dockerfile(project_info)
        elif project_type == "python":
            return self._generate_python_dockerfile(project_info)
        elif project_type == "java":
            return self._generate_java_dockerfile(project_info)
        elif project_type == "go":
            return self._generate_go_dockerfile(project_info)
        elif project_type == "rust":
            return self._generate_rust_dockerfile(project_info)
        elif project_type == "dotnet":
            return self._generate_dotnet_dockerfile(project_info)
        elif project_type == "php":
            return self._generate_php_dockerfile(project_info)
        elif project_type == "ruby":
            return self._generate_ruby_dockerfile(project_info)
        else:
            return self._generate_generic_dockerfile(base_image, port)

    def _generate_nodejs_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized Node.js Dockerfile."""
        package_manager = project_info.get("package_manager", "npm")
        framework = project_info.get("framework")
        port = project_info.get("suggested_port", 3000)

        if package_manager == "yarn":
            install_cmd = "yarn install --frozen-lockfile"
            copy_lock = "COPY yarn.lock ."
        elif package_manager == "pnpm":
            install_cmd = "pnpm install --frozen-lockfile"
            copy_lock = "COPY pnpm-lock.yaml ."
        else:
            install_cmd = "npm ci"
            copy_lock = "COPY package-lock.json* ."

        build_cmd = "npm run build" if framework in ["nextjs", "react", "vue"] else ""
        start_cmd = "npm start" if framework != "nextjs" else "npm start"

        dockerfile = f"""# Multi-stage build for Node.js application
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json {copy_lock}
RUN {install_cmd}

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
{f'RUN {build_cmd}' if build_cmd else '# No build step needed'}

# Production image, copy all the files and run the app
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Copy built application
{f'COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./' if framework == 'nextjs' else 'COPY --from=builder /app .'}
{f'COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static' if framework == 'nextjs' else ''}

USER nextjs

EXPOSE {port}

ENV PORT {port}

CMD ["{start_cmd}"]
"""
        return dockerfile

    def _generate_python_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized Python Dockerfile."""
        framework = project_info.get("framework")
        port = project_info.get("suggested_port", 8000)
        package_manager = project_info.get("package_manager", "pip")

        if package_manager == "poetry":
            install_section = """
# Install Poetry
RUN pip install poetry

# Configure poetry: venvs in project, no interaction
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR
"""
            cmd = 'CMD ["poetry", "run", "python", "app.py"]'
        elif package_manager == "pipenv":
            install_section = """
# Install Pipenv
RUN pip install pipenv

# Install dependencies
COPY Pipfile Pipfile.lock* ./
RUN pipenv install --system --deploy
"""
            cmd = 'CMD ["python", "app.py"]'
        else:
            install_section = """
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
"""
            cmd = 'CMD ["python", "app.py"]'

        if framework == "django":
            cmd = 'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]'
        elif framework == "flask":
            cmd = 'CMD ["python", "app.py"]'
        elif framework == "fastapi":
            cmd = 'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]'

        dockerfile = f"""FROM python:3.11-alpine

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

{install_section}

# Copy project
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE {port}

{cmd}
"""
        return dockerfile

    def _generate_java_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized Java Dockerfile."""
        build_tool = project_info.get("build_tool", "maven")
        port = project_info.get("suggested_port", 8080)

        if build_tool == "maven":
            build_section = """
# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy source and build
COPY src ./src
RUN mvn clean package -DskipTests
"""
            jar_path = "target/*.jar"
        else:  # gradle
            build_section = """
# Copy build files and download dependencies
COPY build.gradle settings.gradle ./
COPY gradle ./gradle
RUN ./gradlew dependencies

# Copy source and build
COPY src ./src
RUN ./gradlew build -x test
"""
            jar_path = "build/libs/*.jar"

        dockerfile = f"""# Multi-stage build for Java application
FROM openjdk:17-alpine AS builder

WORKDIR /app

{build_section}

# Runtime stage
FROM openjdk:17-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \\
    adduser -u 1001 -S appuser -G appgroup

# Copy JAR from builder stage
COPY --from=builder /app/{jar_path} app.jar

# Change ownership and switch to non-root user
RUN chown appuser:appgroup app.jar
USER appuser

EXPOSE {port}

ENTRYPOINT ["java", "-jar", "app.jar"]
"""
        return dockerfile

    def _generate_go_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized Go Dockerfile."""
        port = project_info.get("suggested_port", 8080)

        dockerfile = f"""# Multi-stage build for Go application
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates
WORKDIR /root/

# Create non-root user
RUN adduser -D -s /bin/sh appuser

# Copy the binary from builder stage
COPY --from=builder /app/main .

# Change ownership and switch to non-root user
RUN chown appuser:appuser main
USER appuser

EXPOSE {port}

CMD ["./main"]
"""
        return dockerfile

    def _generate_rust_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized Rust Dockerfile."""
        port = project_info.get("suggested_port", 8080)

        dockerfile = f"""# Multi-stage build for Rust application
FROM rust:1.70-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache musl-dev

# Copy manifest files
COPY Cargo.toml Cargo.lock ./

# Create dummy src/main.rs for dependency caching
RUN mkdir src && echo "fn main() {{}}" > src/main.rs
RUN cargo build --release
RUN rm src/main.rs

# Copy source code
COPY src ./src

# Build the application
RUN cargo build --release

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates
WORKDIR /root/

# Create non-root user
RUN adduser -D -s /bin/sh appuser

# Copy the binary from builder stage
COPY --from=builder /app/target/release/app .

# Change ownership and switch to non-root user
RUN chown appuser:appuser app
USER appuser

EXPOSE {port}

CMD ["./app"]
"""
        return dockerfile

    def _generate_dotnet_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized .NET Dockerfile."""
        port = project_info.get("suggested_port", 80)

        dockerfile = f"""# Multi-stage build for .NET application
FROM mcr.microsoft.com/dotnet/sdk:7.0-alpine AS builder

WORKDIR /app

# Copy csproj and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy source code and build
COPY . .
RUN dotnet publish -c Release -o out

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:7.0-alpine

WORKDIR /app

# Create non-root user
RUN adduser -u 1001 --disabled-password --gecos "" appuser

# Copy published app
COPY --from=builder /app/out .

# Change ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE {port}

ENTRYPOINT ["dotnet", "app.dll"]
"""
        return dockerfile

    def _generate_php_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized PHP Dockerfile."""
        port = project_info.get("suggested_port", 80)

        dockerfile = f"""FROM php:8.2-apache

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    libpng-dev \\
    libonig-dev \\
    libxml2-dev \\
    zip \\
    unzip

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www

# Copy composer files
COPY composer.json composer.lock* ./

# Install dependencies
RUN composer install --no-scripts --no-autoloader

# Copy application code
COPY . .

# Generate autoloader
RUN composer dump-autoload --optimize

# Change ownership of our applications
RUN chown -R www-data:www-data /var/www

# Switch to non-root user
USER www-data

EXPOSE {port}

CMD ["apache2-foreground"]
"""
        return dockerfile

    def _generate_ruby_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate optimized Ruby Dockerfile."""
        framework = project_info.get("framework")
        port = project_info.get("suggested_port", 3000)

        cmd = 'CMD ["ruby", "app.rb"]'
        if framework == "rails":
            cmd = 'CMD ["rails", "server", "-b", "0.0.0.0"]'

        dockerfile = f"""FROM ruby:3.2-alpine

# Install dependencies
RUN apk add --no-cache \\
    build-base \\
    postgresql-dev \\
    nodejs \\
    yarn

WORKDIR /app

# Install gems
COPY Gemfile Gemfile.lock ./
RUN bundle install

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE {port}

{cmd}
"""
        return dockerfile

    def _generate_generic_dockerfile(self, base_image: str, port: int) -> str:
        """Generate a generic Dockerfile template."""
        dockerfile = f"""FROM {base_image}

WORKDIR /app

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE {port}

CMD ["echo", "Please customize this Dockerfile for your application"]
"""
        return dockerfile

    # Rails-like chainable methods
    def engine(self, engine_name: str):
        """Set preferred container engine - chainable"""
        self.preferred_engine = engine_name
        self._detect_container_engine()
        return self

    def context(self, build_context: str):
        """Set build context path - chainable"""
        self.build_context = build_context
        return self

    def dockerfile(self, dockerfile_path: str):
        """Set Dockerfile path - chainable"""
        self.dockerfile_path = dockerfile_path
        return self

    def registry(self, registry_url: str):
        """Set container registry - chainable"""
        self.image_registry = registry_url
        return self

    def tag(self, tag_name: str):
        """Set image tag - chainable"""
        self.image_tag = tag_name
        return self

    def auto_deploy(self, enabled: bool = True):
        """Enable/disable automatic deployment - chainable"""
        self.auto_deploy_enabled = enabled
        return self

    def preview(self) -> Dict[str, Any]:
        """Preview container engine configuration and detected project info."""
        print(f"\n🔍 Universal Container Engine Preview")
        print("=" * 50)

        print(f"Container Engine: {self.detected_engine.value}")
        print(f"Engine Version: {self.engine_version}")
        print(f"Engine Command: {self.engine_command}")

        if self.capabilities:
            print(f"\nCapabilities:")
            for capability, available in self.capabilities.items():
                status = "✅" if available else "❌"
                print(f"  {status} {capability.title()}")

        if self.template_detected:
            print(f"\nDetected Project:")
            print(f"  Type: {self.template_detected['type']}")
            print(f"  Language: {self.template_detected['language']}")
            if self.template_detected['framework']:
                print(f"  Framework: {self.template_detected['framework']}")
            print(f"  Package Manager: {self.template_detected['package_manager']}")
            print(f"  Suggested Base Image: {self.template_detected['suggested_base_image']}")
            print(f"  Suggested Port: {self.template_detected['suggested_port']}")

        print(f"\nConfiguration:")
        print(f"  Build Context: {self.build_context}")
        print(f"  Dockerfile: {self.dockerfile_path}")
        print(f"  Auto Build: {self.auto_build_enabled}")
        print(f"  Auto Deploy: {self.auto_deploy_enabled}")
        if self.image_registry:
            print(f"  Registry: {self.image_registry}")
        print(f"  Tag: {self.image_tag}")

        print("=" * 50)

        return {
            "engine": self.detected_engine.value,
            "version": self.engine_version,
            "capabilities": self.capabilities,
            "project": self.template_detected,
            "auto_deploy": self.auto_deploy_enabled
        }

    def magic(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Perform complete container magic: detect, build, and optionally deploy.

        Args:
            project_path: Path to the project

        Returns:
            Result of the magic operation
        """
        print(f"✨ Starting Universal Container Magic...")

        # Step 1: Detect project
        project_info = self.detect_project_type(project_path)
        print(f"🔍 Detected {project_info['type']} project" +
              (f" with {project_info['framework']} framework" if project_info['framework'] else ""))

        # Step 2: Generate Dockerfile if it doesn't exist
        dockerfile_path = Path(project_path) / "Dockerfile"
        if not dockerfile_path.exists():
            print(f"📝 Generating optimized Dockerfile...")
            dockerfile_content = self.generate_dockerfile(project_info)
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)
            print(f"✅ Dockerfile generated successfully!")
        else:
            print(f"📋 Using existing Dockerfile")

        # Step 3: Build image if auto_build is enabled
        if self.auto_build_enabled:
            image_name = self._get_image_name(project_path)
            build_result = self.build(image_name, project_path)
            if not build_result["success"]:
                return {"success": False, "error": build_result["error"]}

        # Step 4: Deploy if auto_deploy is enabled
        if self.auto_deploy_enabled:
            deploy_result = self.deploy(image_name)
            if not deploy_result["success"]:
                return {"success": False, "error": deploy_result["error"]}

        print(f"✨ Container magic completed successfully!")
        return {
            "success": True,
            "project_info": project_info,
            "dockerfile_generated": not dockerfile_path.exists(),
            "image_built": self.auto_build_enabled,
            "deployed": self.auto_deploy_enabled
        }

    def build(self, image_name: str, build_context: str = None) -> Dict[str, Any]:
        """
        Build container image using detected engine.

        Args:
            image_name: Name for the built image
            build_context: Build context path

        Returns:
            Build result
        """
        if self.detected_engine == ContainerEngine.UNKNOWN:
            return {"success": False, "error": "No container engine available"}

        context = build_context or self.build_context
        print(f"🔨 Building image: {image_name}")

        try:
            cmd = [
                self.engine_command,
                "build",
                "-t", image_name,
                "-f", self.dockerfile_path,
                context
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=context
            )

            if result.returncode == 0:
                print(f"✅ Image built successfully: {image_name}")
                return {"success": True, "image_name": image_name}
            else:
                print(f"❌ Build failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except subprocess.SubprocessError as e:
            return {"success": False, "error": str(e)}

    def push(self, image_name: str) -> Dict[str, Any]:
        """
        Push image to registry.

        Args:
            image_name: Name of the image to push

        Returns:
            Push result
        """
        if self.detected_engine == ContainerEngine.UNKNOWN:
            return {"success": False, "error": "No container engine available"}

        print(f"📤 Pushing image: {image_name}")

        try:
            cmd = [self.engine_command, "push", image_name]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ Image pushed successfully: {image_name}")
                return {"success": True, "image_name": image_name}
            else:
                print(f"❌ Push failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except subprocess.SubprocessError as e:
            return {"success": False, "error": str(e)}

    def deploy(self, image_name: str) -> Dict[str, Any]:
        """
        Deploy container (placeholder for cloud provider integration).

        Args:
            image_name: Name of the image to deploy

        Returns:
            Deploy result
        """
        print(f"🚀 Deploying image: {image_name}")
        # This would integrate with cloud providers (AWS ECS, GCP Cloud Run, etc.)
        print(f"✅ Deployment initiated for: {image_name}")
        return {"success": True, "image_name": image_name, "status": "deployed"}

    def _get_image_name(self, project_path: str) -> str:
        """Generate image name based on project."""
        project_name = Path(project_path).name
        if self.image_registry:
            return f"{self.image_registry}/{project_name}:{self.image_tag}"
        else:
            return f"{project_name}:{self.image_tag}"
