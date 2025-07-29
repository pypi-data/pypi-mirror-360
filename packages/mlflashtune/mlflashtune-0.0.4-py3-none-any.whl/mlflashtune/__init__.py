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

import warnings
import logging

# Suppress SQLAlchemy warnings from ax-platform
warnings.filterwarnings("ignore", 
                       message=".*sqlalchemy version below 2.0.*")

# Suppress Ax parameter warnings 
warnings.filterwarnings("ignore", 
                       message=".*is not specified for.*ChoiceParameter.*")

# Also suppress at the logging level
logging.getLogger("ax.service.utils.with_db_settings_base").setLevel(logging.ERROR)

__version__ = "0.0.4"
__author__ = "MLFlashTune Development Team"

# Main imports for easy access
from mlflashtune.core.config import AEConfig
from mlflashtune.core.optimizer import AEModelTuner

__all__ = [
    "AEConfig",
    "AEModelTuner",
    "__version__"
]