"""
IntelligentApplication API - The Revolutionary Developer Experience

This is the magical interface that makes Cross-Cloud Magic possible.
Developers can create applications that automatically select optimal 
providers for each service based on intelligent analysis.

Example:
    app = InfraDSL.Application("my-app")
        .auto_optimize()
        .database("postgresql")      # → Chooses GCP (best price/performance)
        .compute("web-servers")      # → Chooses AWS (best global coverage)
        .cdn("static-assets")        # → Chooses Cloudflare (best edge network)
        .storage("user-uploads")     # → Chooses DigitalOcean (best simplicity)
        .create()

Result: Cost optimization, optimal performance, maximum reliability

This file has been refactored into a modular structure for better maintainability.
The original 1500+ line file has been split into focused modules:

- data_classes.py: Core data structures
- constraint_methods.py: Provider constraint methods  
- service_methods.py: Service definition methods
- lifecycle_methods.py: Intelligence & lifecycle methods
- resource_creation.py: Provider-specific resource creation
- preview_methods.py: Preview & utility methods
- core.py: Main class combining all mixins
"""

# Import all classes from the modular structure
from .intelligent_application import (
    IntelligentApplication,
    OptimizationPreferences,
    ServiceConfiguration
)

# For backwards compatibility, export the same interface
__all__ = ['IntelligentApplication', 'OptimizationPreferences', 'ServiceConfiguration']