"""
LoadBalancer Module (Refactored)

This module contains the refactored LoadBalancer components that were previously
in a single large load_balancer.py file. The components are now organized as:

- load_balancer_core.py: Core LoadBalancer class with main functionality
- load_balancer_discovery.py: Load balancer discovery and management
- load_balancer_lifecycle.py: Lifecycle operations (create/update/destroy)
- load_balancer_configuration.py: Chainable configuration methods

This modular structure makes the LoadBalancer resource more maintainable and testable.
The main LoadBalancer class combines all functionality through multiple inheritance.
"""

# Import the comprehensive LoadBalancer implementation
from .load_balancer import LoadBalancer


__all__ = ['LoadBalancer'] 