"""
IntelligentApplication API - The Revolutionary Developer Experience (Modular Version)

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

This file imports from the modular structure for better maintainability.
"""

# Import all classes from the modular structure
from .intelligent_application import (
    IntelligentApplication,
    OptimizationPreferences,
    ServiceConfiguration
)

# For backwards compatibility, export the same interface
__all__ = ['IntelligentApplication', 'OptimizationPreferences', 'ServiceConfiguration']