"""
AWS EC2 Resource - Refactored Entry Point

This file serves as the main entry point for the AWS EC2 resource.
The actual implementation has been refactored into modular components
in the ec2/ directory for better maintainability.

Previous monolithic structure (1,147 lines):
- Mixed core functionality, discovery, lifecycle, and configuration

New modular structure:
- ec2/ec2_core.py: Core EC2 class with main functionality (~350 lines)
- ec2/ec2_discovery.py: Instance discovery and management (~200 lines)  
- ec2/ec2_lifecycle.py: Lifecycle operations (start/stop/destroy) (~250 lines)
- ec2/ec2_configuration.py: Chainable configuration methods (~400 lines)

Benefits of refactoring:
- Single Responsibility Principle: Each module has one clear purpose
- Easier Testing: Smaller, focused modules are easier to unit test
- Better Maintainability: Changes are isolated to specific concerns
- Improved Readability: Developers can focus on specific functionality
- Multiple Inheritance: Clean composition of capabilities

The EC2 class now combines all functionality through multiple inheritance,
providing the same interface as before but with much better organization.
"""

# Import the main EC2 class from the refactored module
from .ec2 import EC2

# For backwards compatibility, ensure all existing imports still work
__all__ = ['EC2']