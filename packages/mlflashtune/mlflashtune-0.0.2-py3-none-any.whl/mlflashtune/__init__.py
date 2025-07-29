"""
MLFlashTune Package

A comprehensive ensemble optimization system using Meta's Ax platform for 
Bayesian hyperparameter optimization of LightGBM models.

Key Components:
- Core optimization engine (mlflashtune.core)
- Command-line interface (mlflashtune.cli)  
- Web visualization tools (mlflashtune.web)
- Utilities and helpers (mlflashtune.utils)
"""

__version__ = "0.0.2"
__author__ = "MLFlashTune Development Team"

# Main imports for easy access
from mlflashtune.core.config import AEConfig
from mlflashtune.core.optimizer import AEModelTuner

__all__ = [
    "AEConfig",
    "AEModelTuner",
    "__version__"
]