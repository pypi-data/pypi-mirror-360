"""School of Prompt 🎸

Rock your prompts! Simple, powerful prompt optimization with minimal boilerplate.
Inspired by the School of Rock - where every prompt can be a rock star.
"""

__version__ = "0.2.0"
__author__ = "School of Prompt Team"

# Main API
from .optimize import optimize

# Extension points for advanced users
from .core.simple_interfaces import (
    CustomMetric,
    CustomDataSource,
    CustomModel,
    CustomTask
)

__all__ = [
    # Main API
    "optimize",

    # Extension interfaces
    "CustomMetric",
    "CustomDataSource",
    "CustomModel",
    "CustomTask",
]
