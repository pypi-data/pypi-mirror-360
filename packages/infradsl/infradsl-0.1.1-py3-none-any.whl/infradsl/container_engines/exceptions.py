"""
Container Engine Exceptions

Custom exceptions for container engine operations with Rails-like
developer-friendly error messages and actionable suggestions.
"""


class ContainerEngineError(Exception):
    """Base exception for all container engine related errors"""

    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with optional suggestion"""
        formatted = f"❌ Container Engine Error: {self.message}"
        if self.suggestion:
            formatted += f"\n💡 Suggestion: {self.suggestion}"
        return formatted


class NoEngineFoundError(ContainerEngineError):
    """Raised when no compatible container engine is found on the system"""

    def __init__(self):
        message = "No compatible container engine found (Docker, Podman, etc.)"
        suggestion = (
            "Install Docker Desktop (https://docker.com/desktop) or "
            "Podman (https://podman.io/getting-started/installation)"
        )
        super().__init__(message, suggestion)


class ContainerBuildError(ContainerEngineError):
    """Raised when container build fails"""

    def __init__(self, engine_name: str, exit_code: int, output: str = None):
        message = f"{engine_name} build failed with exit code {exit_code}"

        # Provide intelligent suggestions based on common failures
        suggestion = self._get_build_suggestion(output or "")
        super().__init__(message, suggestion)

    def _get_build_suggestion(self, output: str) -> str:
        """Provide intelligent suggestions based on build output"""
        output_lower = output.lower()

        if "dockerfile" in output_lower and "not found" in output_lower:
            return "Create a Dockerfile in your project root or use .container() to auto-generate one"
        elif "permission denied" in output_lower:
            return "Check Docker/Podman permissions or try running with sudo"
        elif "no space left" in output_lower:
            return "Free up disk space or clean container images with 'docker system prune'"
        elif "network" in output_lower and ("timeout" in output_lower or "unreachable" in output_lower):
            return "Check internet connection or try building again"
        else:
            return "Check the build logs above for specific error details"


class ContainerPushError(ContainerEngineError):
    """Raised when container push to registry fails"""

    def __init__(self, registry: str, image: str, details: str = None):
        message = f"Failed to push {image} to {registry}"
        suggestion = self._get_push_suggestion(registry, details or "")
        super().__init__(message, suggestion)

    def _get_push_suggestion(self, registry: str, details: str) -> str:
        """Provide intelligent suggestions for push failures"""
        details_lower = details.lower()

        if "unauthorized" in details_lower or "authentication" in details_lower:
            if "gcr.io" in registry or "pkg.dev" in registry:
                return "Run 'gcloud auth configure-docker' to authenticate with Google Cloud Registry"
            elif "docker.io" in registry:
                return "Run 'docker login' to authenticate with Docker Hub"
            else:
                return f"Authenticate with {registry} registry"
        elif "not found" in details_lower or "does not exist" in details_lower:
            return f"Ensure the repository exists in {registry} or check repository permissions"
        elif "denied" in details_lower:
            return f"Check push permissions for {registry}"
        else:
            return "Verify registry URL and authentication"


class UnsupportedArchitectureError(ContainerEngineError):
    """Raised when trying to build for unsupported architecture"""

    def __init__(self, current_arch: str, target_arch: str, engine_name: str):
        message = f"Cannot build for {target_arch} on {current_arch} using {engine_name}"
        suggestion = (
            f"Use buildx with Docker or buildah with Podman for cross-architecture builds, "
            f"or enable multi-platform building"
        )
        super().__init__(message, suggestion)


class ContainerRunError(ContainerEngineError):
    """Raised when container run/execution fails"""

    def __init__(self, image: str, exit_code: int, details: str = None):
        message = f"Container {image} failed to run (exit code: {exit_code})"
        suggestion = self._get_run_suggestion(details or "")
        super().__init__(message, suggestion)

    def _get_run_suggestion(self, details: str) -> str:
        """Provide suggestions for container run failures"""
        details_lower = details.lower()

        if "port" in details_lower and "already in use" in details_lower:
            return "Change the port mapping or stop the service using the port"
        elif "not found" in details_lower:
            return "Ensure the image exists locally or pull it from registry"
        elif "permission denied" in details_lower:
            return "Check file permissions or run with appropriate user privileges"
        else:
            return "Check container logs for detailed error information"


class TemplateError(ContainerEngineError):
    """Raised when container template processing fails"""

    def __init__(self, template_name: str, reason: str):
        message = f"Failed to process template '{template_name}': {reason}"
        suggestion = "Check template syntax and ensure all required variables are provided"
        super().__init__(message, suggestion)


class ConfigurationError(ContainerEngineError):
    """Raised when container engine configuration is invalid"""

    def __init__(self, config_issue: str):
        message = f"Container engine configuration error: {config_issue}"
        suggestion = "Check container engine settings and daemon configuration"
        super().__init__(message, suggestion)
