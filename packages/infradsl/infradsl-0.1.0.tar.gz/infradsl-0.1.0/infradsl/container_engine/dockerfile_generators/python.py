"""
Python Dockerfile Generator

This module provides specialized Dockerfile generation for Python applications,
with support for various package managers and frameworks.
"""

from typing import Dict, Any
from .base import BaseDockerfileGenerator


class PythonDockerfileGenerator(BaseDockerfileGenerator):
    """
    Python Dockerfile Generator
    
    Supports:
    - pip, poetry, pipenv package managers
    - Django, Flask, FastAPI, Starlette frameworks
    - Multi-stage builds for compiled dependencies
    - Security hardening with non-root users
    """
    
    def generate(self) -> str:
        """Generate optimized Python Dockerfile."""
        package_manager = self.get_package_manager()
        framework = self.get_framework()
        port = self.get_port()
        
        if self.should_use_multi_stage():
            return self._generate_multi_stage_dockerfile()
        else:
            return self._generate_single_stage_dockerfile()
    
    def _generate_single_stage_dockerfile(self) -> str:
        """Generate single-stage Python Dockerfile."""
        package_manager = self.get_package_manager()
        framework = self.get_framework()
        port = self.get_port()
        
        # Base image
        self.add_comment("Python application")
        self.add_from("python:3.11-alpine")
        self.add_blank_line()
        
        # Set working directory
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_performance_optimizations()
        self.add_blank_line()
        
        # Install system dependencies if needed
        self._add_system_dependencies(framework)
        
        # Install Python dependencies
        self._add_dependency_installation(package_manager)
        self.add_blank_line()
        
        # Copy project files
        self.add_comment("Copy project")
        self.add_copy(". .")
        self.add_blank_line()
        
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
    
    def _generate_multi_stage_dockerfile(self) -> str:
        """Generate multi-stage Python Dockerfile for better optimization."""
        package_manager = self.get_package_manager()
        framework = self.get_framework()
        port = self.get_port()
        
        # Builder stage
        self.add_comment("Multi-stage build for Python application")
        self.add_from("python:3.11-alpine", platform="linux/amd64")
        self.add_label("stage", "builder")
        self.add_blank_line()
        
        # Install build dependencies
        self.add_comment("Install build dependencies")
        self.add_run("apk add --no-cache gcc musl-dev libffi-dev")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_performance_optimizations()
        self.add_blank_line()
        
        # Install Python dependencies
        self._add_dependency_installation(package_manager)
        self.add_blank_line()
        
        # Production stage
        self.add_comment("Production stage")
        self.add_from("python:3.11-alpine")
        self.add_workdir("/app")
        self.add_blank_line()
        
        # Performance optimizations
        self.add_performance_optimizations()
        self.add_blank_line()
        
        # Install runtime dependencies
        self._add_system_dependencies(framework)
        
        # Copy installed packages from builder
        if package_manager == "poetry":
            self.add_copy("--from=builder /app/.venv /app/.venv")
            self.add_env("PATH", "/app/.venv/bin:$PATH")
        else:
            self.add_copy("--from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages")
            self.add_copy("--from=builder /usr/local/bin /usr/local/bin")
        
        self.add_blank_line()
        
        # Copy project files
        self.add_comment("Copy project")
        self.add_copy(". .")
        self.add_blank_line()
        
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
    
    def _add_system_dependencies(self, framework: str):
        """Add system dependencies based on framework."""
        if framework in ["django", "flask", "fastapi"]:
            self.add_comment("Install runtime dependencies")
            deps = ["curl", "postgresql-client"]
            if framework == "django":
                deps.extend(["gettext", "postgresql-dev"])
            self.add_run(f"apk add --no-cache {' '.join(deps)}")
            self.add_blank_line()
    
    def _add_dependency_installation(self, package_manager: str):
        """Add package manager specific dependency installation."""
        if package_manager == "poetry":
            self.add_comment("Install Poetry and dependencies")
            self.add_run("pip install poetry")
            self.add_blank_line()
            
            self.add_comment("Configure poetry: venvs in project, no interaction")
            self.add_env("POETRY_VENV_IN_PROJECT", "1")
            self.add_env("POETRY_NO_INTERACTION", "1") 
            self.add_env("POETRY_CACHE_DIR", "/tmp/poetry_cache")
            self.add_blank_line()
            
            self.add_comment("Install dependencies")
            self.add_copy("pyproject.toml poetry.lock* ./")
            self.add_run("poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR")
            
        elif package_manager == "pipenv":
            self.add_comment("Install Pipenv and dependencies")
            self.add_run("pip install pipenv")
            self.add_blank_line()
            
            self.add_comment("Install dependencies")
            self.add_copy("Pipfile Pipfile.lock* ./")
            self.add_run("pipenv install --system --deploy")
            
        else:  # pip
            self.add_comment("Install dependencies")
            self.add_copy("requirements.txt .")
            self.add_run("pip install --no-cache-dir -r requirements.txt")
    
    def _get_start_command(self, framework: str) -> str:
        """Get the appropriate start command for the framework."""
        start_commands = {
            "django": '["python", "manage.py", "runserver", "0.0.0.0:8000"]',
            "flask": '["python", "app.py"]',
            "fastapi": '["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]',
            "starlette": '["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]'
        }
        
        package_manager = self.get_package_manager()
        base_cmd = start_commands.get(framework, '["python", "main.py"]')
        
        if package_manager == "poetry":
            # Wrap command in poetry run
            return f'["poetry", "run"] + {base_cmd}' if base_cmd.startswith('[') else f'["poetry", "run", "{base_cmd}"]'
        
        return base_cmd
    
    def _add_health_check(self, port: int, framework: str):
        """Add health check configuration."""
        if framework == "django":
            health_test = f"python manage.py check --deploy || exit 1"
        elif framework in ["fastapi", "starlette"]:
            health_test = f"curl --fail http://localhost:{port}/health || wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1"
        else:
            health_test = f"curl --fail http://localhost:{port}/ || wget --no-verbose --tries=1 --spider http://localhost:{port}/ || exit 1"
        
        self.add_healthcheck(health_test, interval="30s", timeout="5s", retries=3)
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get Python specific optimization recommendations."""
        framework = self.get_framework()
        package_manager = self.get_package_manager()
        
        recommendations = {
            "multi_stage_build": self.should_use_multi_stage(),
            "alpine_base": True,
            "compiled_dependencies": framework in ["django", "fastapi"],
            "framework_optimizations": []
        }
        
        if framework == "django":
            recommendations["framework_optimizations"].extend([
                "Use Django's collectstatic for static files",
                "Enable Django's database connection pooling",
                "Configure proper logging for production"
            ])
        elif framework == "fastapi":
            recommendations["framework_optimizations"].extend([
                "Use uvicorn with multiple workers",
                "Enable async database connections",
                "Configure proper CORS settings"
            ])
        elif framework == "flask":
            recommendations["framework_optimizations"].extend([
                "Use Gunicorn as WSGI server",
                "Enable Flask-Caching for better performance",
                "Configure proper error handling"
            ])
        
        if package_manager == "poetry":
            recommendations["package_manager_benefits"] = [
                "Deterministic builds with poetry.lock",
                "Virtual environment isolation",
                "Better dependency resolution"
            ]
        elif package_manager == "pipenv":
            recommendations["package_manager_benefits"] = [
                "Pipfile for better dependency management",
                "Automatic virtual environment creation",
                "Security vulnerability scanning"
            ]
        
        return recommendations