"""
Project Type Detector

This module handles automatic detection of project types, frameworks,
and languages to enable intelligent Dockerfile generation.
"""

import json
from pathlib import Path
from typing import Dict, Any


class ProjectDetector:
    """
    Project Type and Framework Detection
    
    This class handles:
    - Language detection (Node.js, Python, Java, Go, etc.)
    - Framework detection (React, Django, Spring Boot, etc.)
    - Package manager detection (npm, pip, maven, etc.)
    - Intelligent defaults for base images and ports
    """

    def __init__(self):
        """Initialize the project detector"""
        self.detected_info = {}

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
            detected.update(self._detect_nodejs_project(project_path))

        # Python detection
        elif self._is_python_project(project_path):
            detected.update(self._detect_python_project(project_path))

        # Java detection
        elif self._is_java_project(project_path):
            detected.update(self._detect_java_project(project_path))

        # Go detection
        elif (project_path / "go.mod").exists():
            detected.update(self._detect_go_project(project_path))

        # Rust detection
        elif (project_path / "Cargo.toml").exists():
            detected.update(self._detect_rust_project(project_path))

        # .NET detection
        elif self._is_dotnet_project(project_path):
            detected.update(self._detect_dotnet_project(project_path))

        # PHP detection
        elif (project_path / "composer.json").exists():
            detected.update(self._detect_php_project(project_path))

        # Ruby detection
        elif (project_path / "Gemfile").exists():
            detected.update(self._detect_ruby_project(project_path))

        self.detected_info = detected
        return detected

    def _detect_nodejs_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect Node.js project details"""
        info = {
            "type": "nodejs",
            "language": "javascript",
            "package_manager": "npm",
            "suggested_base_image": "node:18-alpine",
            "suggested_port": 3000
        }

        # Check for package managers
        if (project_path / "yarn.lock").exists():
            info["package_manager"] = "yarn"
        elif (project_path / "pnpm-lock.yaml").exists():
            info["package_manager"] = "pnpm"

        # Detect framework from package.json
        try:
            with open(project_path / "package.json", "r") as f:
                package_json = json.load(f)
                deps = {**package_json.get("dependencies", {}), **package_json.get("devDependencies", {})}

                if "next" in deps:
                    info["framework"] = "nextjs"
                    info["suggested_port"] = 3000
                elif "react" in deps:
                    info["framework"] = "react"
                    info["suggested_port"] = 3000
                elif "vue" in deps:
                    info["framework"] = "vue"
                    info["suggested_port"] = 8080
                elif "express" in deps:
                    info["framework"] = "express"
                    info["suggested_port"] = 3000
                elif "fastify" in deps:
                    info["framework"] = "fastify"
                    info["suggested_port"] = 3000
                elif "@nestjs/core" in deps:
                    info["framework"] = "nestjs"
                    info["suggested_port"] = 3000
                elif "svelte" in deps:
                    info["framework"] = "svelte"
                    info["suggested_port"] = 5000
                elif "nuxt" in deps:
                    info["framework"] = "nuxt"
                    info["suggested_port"] = 3000

        except (json.JSONDecodeError, FileNotFoundError):
            pass

        return info

    def _is_python_project(self, project_path: Path) -> bool:
        """Check if this is a Python project"""
        python_files = [
            "requirements.txt", "pyproject.toml", "Pipfile", 
            "setup.py", "setup.cfg", "poetry.lock"
        ]
        return any((project_path / f).exists() for f in python_files)

    def _detect_python_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect Python project details"""
        info = {
            "type": "python",
            "language": "python",
            "suggested_base_image": "python:3.11-alpine",
            "suggested_port": 8000
        }

        # Detect package manager
        if (project_path / "requirements.txt").exists():
            info["package_manager"] = "pip"
        elif (project_path / "Pipfile").exists():
            info["package_manager"] = "pipenv"
        elif (project_path / "pyproject.toml").exists():
            info["package_manager"] = "poetry"
        elif (project_path / "setup.py").exists():
            info["package_manager"] = "setuptools"

        # Detect Python frameworks
        try:
            if (project_path / "requirements.txt").exists():
                with open(project_path / "requirements.txt", "r") as f:
                    requirements = f.read().lower()
                    if "django" in requirements:
                        info["framework"] = "django"
                        info["suggested_port"] = 8000
                    elif "flask" in requirements:
                        info["framework"] = "flask"
                        info["suggested_port"] = 5000
                    elif "fastapi" in requirements:
                        info["framework"] = "fastapi"
                        info["suggested_port"] = 8000
                    elif "starlette" in requirements:
                        info["framework"] = "starlette"
                        info["suggested_port"] = 8000
        except FileNotFoundError:
            pass

        return info

    def _is_java_project(self, project_path: Path) -> bool:
        """Check if this is a Java project"""
        java_files = ["pom.xml", "build.gradle", "build.gradle.kts"]
        return any((project_path / f).exists() for f in java_files)

    def _detect_java_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect Java project details"""
        info = {
            "type": "java",
            "language": "java",
            "suggested_base_image": "openjdk:17-alpine",
            "suggested_port": 8080
        }

        # Detect build tool
        if (project_path / "pom.xml").exists():
            info["build_tool"] = "maven"
        elif (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists():
            info["build_tool"] = "gradle"

        # Detect Java frameworks
        if (project_path / "src/main/java").exists():
            info["framework"] = "spring-boot"  # Default assumption
            
        return info

    def _detect_go_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect Go project details"""
        return {
            "type": "go",
            "language": "go",
            "suggested_base_image": "golang:1.21-alpine",
            "suggested_port": 8080,
            "package_manager": "go-modules"
        }

    def _detect_rust_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect Rust project details"""
        info = {
            "type": "rust",
            "language": "rust",
            "suggested_base_image": "rust:1.70-alpine",
            "suggested_port": 8080,
            "package_manager": "cargo"
        }

        # Check for web frameworks
        try:
            with open(project_path / "Cargo.toml", "r") as f:
                cargo_content = f.read().lower()
                if "actix-web" in cargo_content:
                    info["framework"] = "actix-web"
                elif "warp" in cargo_content:
                    info["framework"] = "warp"
                elif "rocket" in cargo_content:
                    info["framework"] = "rocket"
        except FileNotFoundError:
            pass

        return info

    def _is_dotnet_project(self, project_path: Path) -> bool:
        """Check if this is a .NET project"""
        dotnet_files = ["*.csproj", "*.sln", "global.json", "Directory.Build.props"]
        return any(list(project_path.glob(pattern)) for pattern in dotnet_files)

    def _detect_dotnet_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect .NET project details"""
        return {
            "type": "dotnet",
            "language": "csharp",
            "suggested_base_image": "mcr.microsoft.com/dotnet/aspnet:7.0-alpine",
            "suggested_port": 80,
            "build_tool": "dotnet"
        }

    def _detect_php_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect PHP project details"""
        info = {
            "type": "php",
            "language": "php",
            "suggested_base_image": "php:8.2-apache",
            "suggested_port": 80,
            "package_manager": "composer"
        }

        # Detect PHP frameworks
        try:
            with open(project_path / "composer.json", "r") as f:
                composer_json = json.load(f)
                deps = {**composer_json.get("require", {}), **composer_json.get("require-dev", {})}
                
                if "laravel/framework" in deps:
                    info["framework"] = "laravel"
                elif "symfony/framework-bundle" in deps:
                    info["framework"] = "symfony"
                elif "codeigniter4/framework" in deps:
                    info["framework"] = "codeigniter"
        except (json.JSONDecodeError, FileNotFoundError):
            pass

        return info

    def _detect_ruby_project(self, project_path: Path) -> Dict[str, Any]:
        """Detect Ruby project details"""
        info = {
            "type": "ruby",
            "language": "ruby",
            "suggested_base_image": "ruby:3.2-alpine",
            "suggested_port": 3000,
            "package_manager": "bundler"
        }

        # Check for Rails
        try:
            with open(project_path / "Gemfile", "r") as f:
                gemfile = f.read().lower()
                if "rails" in gemfile:
                    info["framework"] = "rails"
                elif "sinatra" in gemfile:
                    info["framework"] = "sinatra"
                    info["suggested_port"] = 4567
        except FileNotFoundError:
            pass

        return info

    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of the detected project information"""
        if not self.detected_info:
            return {"error": "No project detected yet. Run detect_project_type() first."}

        summary = {
            "project_type": self.detected_info.get("type", "unknown"),
            "language": self.detected_info.get("language", "unknown"),
            "framework": self.detected_info.get("framework", "none"),
            "recommended_base_image": self.detected_info.get("suggested_base_image", "alpine"),
            "recommended_port": self.detected_info.get("suggested_port", 8080),
            "package_manager": self.detected_info.get("package_manager", "none"),
            "build_tool": self.detected_info.get("build_tool", "none")
        }

        return summary

    def is_supported_project(self) -> bool:
        """Check if the detected project type is supported for Dockerfile generation"""
        supported_types = [
            "nodejs", "python", "java", "go", "rust", 
            "dotnet", "php", "ruby"
        ]
        return self.detected_info.get("type", "unknown") in supported_types

    def get_dockerfile_recommendations(self) -> Dict[str, Any]:
        """Get specific recommendations for Dockerfile generation"""
        if not self.detected_info:
            return {}

        recommendations = {
            "base_image": self.detected_info.get("suggested_base_image", "alpine"),
            "working_directory": "/app",
            "expose_port": self.detected_info.get("suggested_port", 8080),
            "build_commands": self._get_build_commands(),
            "start_command": self._get_start_command(),
            "health_check": self._get_health_check(),
            "environment_variables": self._get_env_variables()
        }

        return recommendations

    def _get_build_commands(self) -> list:
        """Get build commands based on project type"""
        project_type = self.detected_info.get("type", "unknown")
        package_manager = self.detected_info.get("package_manager", "")

        commands = {
            "nodejs": {
                "npm": ["npm ci --only=production"],
                "yarn": ["yarn install --frozen-lockfile --production"],
                "pnpm": ["pnpm install --frozen-lockfile --prod"]
            },
            "python": {
                "pip": ["pip install --no-cache-dir -r requirements.txt"],
                "poetry": ["poetry install --no-dev"],
                "pipenv": ["pipenv install --deploy"]
            },
            "java": {
                "maven": ["mvn clean package -DskipTests"],
                "gradle": ["./gradlew build -x test"]
            },
            "go": ["go build -o main ."],
            "rust": ["cargo build --release"],
            "dotnet": ["dotnet publish -c Release -o out"],
            "php": ["composer install --no-dev --optimize-autoloader"],
            "ruby": ["bundle install --deployment --without development test"]
        }

        if project_type in commands:
            if isinstance(commands[project_type], dict):
                return commands[project_type].get(package_manager, ["echo 'No build command configured'"])
            else:
                return commands[project_type]

        return ["echo 'No build command configured'"]

    def _get_start_command(self) -> str:
        """Get start command based on project type and framework"""
        project_type = self.detected_info.get("type", "unknown")
        framework = self.detected_info.get("framework", "")

        start_commands = {
            "nodejs": {
                "nextjs": "npm start",
                "react": "npm start", 
                "express": "node server.js",
                "default": "npm start"
            },
            "python": {
                "django": "python manage.py runserver 0.0.0.0:8000",
                "flask": "python app.py",
                "fastapi": "uvicorn main:app --host 0.0.0.0 --port 8000",
                "default": "python main.py"
            },
            "java": "java -jar target/*.jar",
            "go": "./main",
            "rust": "./target/release/main",
            "dotnet": "dotnet out/app.dll",
            "php": "apache2-foreground",
            "ruby": {
                "rails": "rails server -b 0.0.0.0",
                "default": "ruby app.rb"
            }
        }

        if project_type in start_commands:
            commands = start_commands[project_type]
            if isinstance(commands, dict):
                return commands.get(framework, commands.get("default", "echo 'No start command'"))
            else:
                return commands

        return "echo 'No start command configured'"

    def _get_health_check(self) -> Dict[str, Any]:
        """Get health check configuration"""
        port = self.detected_info.get("suggested_port", 8080)
        return {
            "test": f"curl --fail http://localhost:{port}/health || exit 1",
            "interval": "30s",
            "timeout": "3s",
            "retries": 3
        }

    def _get_env_variables(self) -> Dict[str, str]:
        """Get recommended environment variables"""
        project_type = self.detected_info.get("type", "unknown")
        
        env_vars = {
            "nodejs": {"NODE_ENV": "production"},
            "python": {"PYTHONUNBUFFERED": "1"},
            "java": {"JAVA_OPTS": "-Xmx512m"},
            "go": {"CGO_ENABLED": "0"},
            "rust": {"RUST_LOG": "info"},
            "dotnet": {"ASPNETCORE_ENVIRONMENT": "Production"},
            "php": {"APP_ENV": "production"},
            "ruby": {"RAILS_ENV": "production"}
        }

        return env_vars.get(project_type, {})