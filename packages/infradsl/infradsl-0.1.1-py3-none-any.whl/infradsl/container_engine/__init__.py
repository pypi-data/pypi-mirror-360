"""
Container Engine Module

This module provides intelligent container runtime detection and management
with specialized Dockerfile generation for different programming languages.

Components:
- EngineDetector: Detects and manages container engines (Docker, Podman, etc.)
- ProjectDetector: Detects project types and frameworks
- DockerfileGenerators: Language-specific Dockerfile generators
- UniversalContainerEngine: Main orchestrator class
"""

# Import main classes for easy access
from .engine_detector import EngineDetector, ContainerEngine
from .project_detector import ProjectDetector
from .universal_engine_refactored import UniversalContainerEngine

# Legacy import for backward compatibility
from .universal_engine import UniversalContainerEngineLegacy

# Import Dockerfile generators
from .dockerfile_generators import (
    BaseDockerfileGenerator,
    NodeJSDockerfileGenerator,
    PythonDockerfileGenerator,
    JavaDockerfileGenerator,
    GoDockerfileGenerator,
    RustDockerfileGenerator,
    DotNetDockerfileGenerator,
    PHPDockerfileGenerator,
    RubyDockerfileGenerator
)

__all__ = [
    # Main classes
    'UniversalContainerEngine',
    'EngineDetector',
    'ProjectDetector',
    'ContainerEngine',
    
    # Legacy
    'UniversalContainerEngineLegacy',
    
    # Dockerfile generators
    'BaseDockerfileGenerator',
    'NodeJSDockerfileGenerator',
    'PythonDockerfileGenerator', 
    'JavaDockerfileGenerator',
    'GoDockerfileGenerator',
    'RustDockerfileGenerator',
    'DotNetDockerfileGenerator',
    'PHPDockerfileGenerator',
    'RubyDockerfileGenerator'
]