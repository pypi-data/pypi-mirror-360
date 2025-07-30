"""
AWS LoadBalancer Resource - Refactored Entry Point

This file serves as the main entry point for the AWS LoadBalancer resource.
The actual implementation has been refactored into modular components
in the load_balancer/ directory for better maintainability.

Previous monolithic structure:
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- load_balancer/load_balancer_core.py: Core LoadBalancer class with main functionality
- load_balancer/load_balancer_discovery.py: Load balancer discovery and management
- load_balancer/load_balancer_lifecycle.py: Lifecycle operations (create/update/destroy)
- load_balancer/load_balancer_configuration.py: Chainable configuration methods

The LoadBalancer class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main LoadBalancer class from the refactored module
from .load_balancer.load_balancer import LoadBalancer

# For backwards compatibility, ensure all existing imports still work
__all__ = ['LoadBalancer'] 