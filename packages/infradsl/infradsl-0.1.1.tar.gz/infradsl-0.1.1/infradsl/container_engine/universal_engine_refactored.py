"""
Universal Container Engine - Refactored

Intelligent container runtime detection and management with Rails-like conventions.
This is the new modular version that orchestrates all the specialized components.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from .engine_detector import EngineDetector, ContainerEngine
from .project_detector import ProjectDetector
from .dockerfile_generators import (
    NodeJSDockerfileGenerator,
    PythonDockerfileGenerator, 
    JavaDockerfileGenerator,
    GoDockerfileGenerator,
    RustDockerfileGenerator,
    DotNetDockerfileGenerator,
    PHPDockerfileGenerator,
    RubyDockerfileGenerator
)


class UniversalContainerEngine:
    """
    Universal Container Engine with intelligent runtime detection.

    Provides a unified interface for all container engines with Rails-like conventions.
    Automatically detects the best available container runtime and adapts accordingly.
    
    This refactored version uses specialized modules for:
    - Container engine detection and management
    - Project type and framework detection  
    - Language-specific Dockerfile generation
    """

    def __init__(self, preferred_engine: Optional[str] = None):
        """
        Initialize Universal Container Engine.

        Args:
            preferred_engine: Preferred container engine (docker, podman, etc.)
        """
        # Initialize specialized components
        self.engine_detector = EngineDetector(preferred_engine)
        self.project_detector = ProjectDetector()
        
        # Rails-like configuration
        self.auto_build_enabled = True
        self.auto_push_enabled = True
        self.auto_deploy_enabled = False
        self.build_context = "."
        self.dockerfile_path = "Dockerfile"
        self.image_registry = None
        self.image_tag = "latest"

        # State management
        self.last_build_hash = None
        self.deployment_state = {}
        self.project_info = {}

        # Auto-detect container engine
        self.detected_engine = self.engine_detector.detect_container_engine()

    @property
    def engine_command(self) -> str:
        """Get the container engine command."""
        return self.engine_detector.engine_command

    @property
    def engine_version(self) -> str:
        """Get the container engine version."""
        return self.engine_detector.engine_version

    @property
    def capabilities(self) -> Dict[str, bool]:
        """Get the container engine capabilities."""
        return self.engine_detector.capabilities

    def detect_project_type(self, path: str = ".") -> Dict[str, Any]:
        """
        Auto-detect project type and framework for intelligent container templates.

        Args:
            path: Path to analyze (default: current directory)

        Returns:
            Dict containing detected project information
        """
        self.project_info = self.project_detector.detect_project_type(path)
        return self.project_info

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
        
        # Get the appropriate generator for the project type
        generator = self._get_dockerfile_generator(project_type, project_info)
        
        if generator:
            return generator.generate()
        else:
            return self._generate_generic_dockerfile(project_info)

    def _get_dockerfile_generator(self, project_type: str, project_info: Dict[str, Any]):
        """Get the appropriate Dockerfile generator for the project type."""
        generators = {
            "nodejs": NodeJSDockerfileGenerator,
            "python": PythonDockerfileGenerator,
            "java": JavaDockerfileGenerator,
            "go": GoDockerfileGenerator,
            "rust": RustDockerfileGenerator,
            "dotnet": DotNetDockerfileGenerator,
            "php": PHPDockerfileGenerator,
            "ruby": RubyDockerfileGenerator
        }
        
        generator_class = generators.get(project_type)
        if generator_class:
            return generator_class(project_info)
        return None

    def _generate_generic_dockerfile(self, project_info: Dict[str, Any]) -> str:
        """Generate a generic Dockerfile template for unsupported project types."""
        base_image = project_info.get("suggested_base_image", "alpine:latest")
        port = project_info.get("suggested_port", 8080)
        
        return f"""FROM {base_image}

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

    # Rails-like chainable methods
    def engine(self, engine_name: str):
        """Set preferred container engine - chainable"""
        self.engine_detector.preferred_engine = engine_name
        self.detected_engine = self.engine_detector.detect_container_engine()
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
        print(f"\\n🔍 Universal Container Engine Preview")
        print("=" * 50)

        # Engine information
        engine_status = self.engine_detector.get_engine_status()
        print(f"Container Engine: {engine_status['engine']}")
        print(f"Engine Version: {engine_status['version']}")
        print(f"Engine Command: {engine_status['command']}")

        if engine_status['capabilities']:
            print(f"\\nCapabilities:")
            for capability, available in engine_status['capabilities'].items():
                status = "✅" if available else "❌"
                print(f"  {status} {capability.title()}")

        # Project information
        if self.project_info:
            print(f"\\nDetected Project:")
            print(f"  Type: {self.project_info['type']}")
            print(f"  Language: {self.project_info['language']}")
            if self.project_info['framework']:
                print(f"  Framework: {self.project_info['framework']}")
            print(f"  Package Manager: {self.project_info['package_manager']}")
            print(f"  Suggested Base Image: {self.project_info['suggested_base_image']}")
            print(f"  Suggested Port: {self.project_info['suggested_port']}")

        print(f"\\nConfiguration:")
        print(f"  Build Context: {self.build_context}")
        print(f"  Dockerfile: {self.dockerfile_path}")
        print(f"  Auto Build: {self.auto_build_enabled}")
        print(f"  Auto Deploy: {self.auto_deploy_enabled}")
        if self.image_registry:
            print(f"  Registry: {self.image_registry}")
        print(f"  Tag: {self.image_tag}")

        print("=" * 50)

        return {
            "engine": engine_status,
            "project": self.project_info,
            "configuration": {
                "auto_deploy": self.auto_deploy_enabled,
                "build_context": self.build_context,
                "dockerfile_path": self.dockerfile_path,
                "image_registry": self.image_registry,
                "image_tag": self.image_tag
            }
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
        dockerfile_generated = False
        if not dockerfile_path.exists():
            print(f"📝 Generating optimized Dockerfile...")
            dockerfile_content = self.generate_dockerfile(project_info)
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)
            print(f"✅ Dockerfile generated successfully!")
            dockerfile_generated = True
        else:
            print(f"📋 Using existing Dockerfile")

        # Step 3: Build image if auto_build is enabled
        image_built = False
        if self.auto_build_enabled:
            image_name = self._get_image_name(project_path)
            build_result = self.build(image_name, project_path)
            if not build_result["success"]:
                return {"success": False, "error": build_result["error"]}
            image_built = True

        # Step 4: Deploy if auto_deploy is enabled
        deployed = False
        if self.auto_deploy_enabled and image_built:
            deploy_result = self.deploy(image_name)
            if not deploy_result["success"]:
                return {"success": False, "error": deploy_result["error"]}
            deployed = True

        print(f"✨ Container magic completed successfully!")
        return {
            "success": True,
            "project_info": project_info,
            "dockerfile_generated": dockerfile_generated,
            "image_built": image_built,
            "deployed": deployed
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
            import subprocess
            
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
            import subprocess
            
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

    def get_optimization_recommendations(self, project_type: str = None) -> Dict[str, Any]:
        """Get optimization recommendations for the current or specified project type."""
        if not project_type and self.project_info:
            project_type = self.project_info.get("type")
        
        if not project_type:
            return {"error": "No project type specified or detected"}
        
        generator = self._get_dockerfile_generator(project_type, self.project_info)
        if generator and hasattr(generator, 'get_optimization_recommendations'):
            return generator.get_optimization_recommendations()
        
        return {"message": f"No specific recommendations available for {project_type} projects"}