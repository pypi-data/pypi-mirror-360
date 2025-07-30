"""
Universal Container Engine Support for InfraDSL

This module provides Rails-like container engine abstraction that works seamlessly
with Docker, Podman, or any OCI-compatible container engine.

Philosophy:
- Convention over configuration
- Auto-detect available engines
- Cross-platform compatibility
- Developer-friendly error messages
"""

from .detector import ContainerEngineDetector
from .engines import DockerEngine, PodmanEngine, ContainerEngine
from .manager import UniversalContainerManager
from .builder import ContainerBuilder
from .exceptions import ContainerEngineError, NoEngineFoundError

__all__ = [
    'ContainerEngineDetector',
    'DockerEngine',
    'PodmanEngine',
    'ContainerEngine',
    'UniversalContainerManager',
    'ContainerBuilder',
    'ContainerEngineError',
    'NoEngineFoundError'
]

# Rails-like convenience - get the best available engine automatically
def get_container_engine():
    """
    Get the best available container engine on this system.

    Returns:
        ContainerEngine: Ready-to-use container engine instance

    Raises:
        NoEngineFoundError: If no compatible engine is found

    Example:
        >>> engine = get_container_engine()
        >>> engine.build("my-app", "/path/to/code")
    """
    detector = ContainerEngineDetector()
    return detector.get_best_engine()

# Rails-like convenience - get the universal manager
def get_container_manager():
    """
    Get a universal container manager that abstracts all engines.

    Returns:
        UniversalContainerManager: Manager that works with any engine

    Example:
        >>> manager = get_container_manager()
        >>> manager.build_and_push("my-app", "/path/to/code", "gcr.io/project/app")
    """
    return UniversalContainerManager()
