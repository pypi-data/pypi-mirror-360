# MLFlashTune

[![PyPI version](https://badge.fury.io/py/mlflashtune.svg)](https://badge.fury.io/py/mlflashtune)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MLFlashTune is a comprehensive ensemble optimization system for Bayesian hyperparameter optimization of LightGBM models. It provides automated machine learning capabilities with a focus on speed, accuracy, and ease of use.

## Features

- 🚀 **Fast Optimization**: Advanced Bayesian optimization algorithms
- 🎯 **LightGBM Ensembles**: Automated ensemble model creation and tuning
- 🌐 **Web Interface**: Interactive visualization and analysis tools
- ⚙️ **Flexible Configuration**: Environment-based configuration system
- 📊 **Rich Analytics**: Comprehensive performance analysis and visualization
- 🔧 **Easy CLI**: Simple command-line interface for all operations

## Installation

```bash
pip install mlflashtune
```

For development installation:

```bash
git clone https://github.com/your-repo/mlflashtune
cd mlflashtune
pip install -e .[dev]
```

## Quick Start

MLFlashTune is a framework that requires you to provide your own configuration files. Here's how to get started:

### 1. Create Directory Structure

```bash
mkdir -p config/hyperparameters
mkdir -p data
# Note: Output directories (outputs/, outputs/runs/, etc.) are created automatically
```

### 2. Create Hyperparameter Space

Create a hyperparameter space file (e.g., `config/hyperparameters/my_space.py`):

```python
# config/hyperparameters/my_space.py
PARAMETERS = [
    {"name": "boosting_type", "type": "choice", "values": ["gbdt", "dart"], "value_type": "str"},
    {"name": "num_leaves", "type": "range", "bounds": [20, 200], "value_type": "int"},
    {"name": "learning_rate", "type": "range", "bounds": [0.01, 0.3], "value_type": "float", "log_scale": True},
    {"name": "n_estimators", "type": "range", "bounds": [100, 300], "value_type": "int"},
    {"name": "subsample", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    {"name": "colsample_bytree", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    {"name": "reg_alpha", "type": "range", "bounds": [1e-8, 0.5], "value_type": "float", "log_scale": True},
    {"name": "reg_lambda", "type": "range", "bounds": [1e-8, 0.5], "value_type": "float", "log_scale": True},
    {"name": "is_unbalance", "type": "choice", "values": [True, False], "value_type": "bool"},
]

def get_parameter_space():
    return PARAMETERS
```

### 3. Create Configuration File

Create your optimization configuration:

```json
{
  "DATA_PATH": "data/your_dataset.csv",
  "HYPERPARAMETER_PATH": "config/hyperparameters/my_space.py",
  "TARGET_COLUMN": "target",
  "FEATURES": ["feature1", "feature2", "feature3"],
  "CATEGORICAL_FEATURES": ["feature1"],
  "CLASS_WEIGHT": {"0": 1, "1": 2},
  "N_ENSEMBLE_GROUP_NUMBER": 10,
  "AE_NUM_TRIALS": 20,
  "NUM_SOBOL_TRIALS": 5,
  "RANDOM_SEED": 42,
  "PARALLEL_TRAINING": true,
  "N_JOBS": -1,
  "SOFT_PREDICTION_THRESHOLD": 0.7,
  "F1_THRESHOLD": 0.7,
  "MIN_RECALL_THRESHOLD": 0.75,
  "UNDER_SAMPLE_MAJORITY_RATIO": 1
}
```

### 4. Run Optimization

```bash
# Set threading environment variable (important!)
export OMP_NUM_THREADS=1

# Run optimization
python -m mlflashtune.cli --config my_config.json

# Validate configuration first
python -m mlflashtune.cli --validate --config my_config.json
```

## Architecture

MLFlashTune is organized into several key modules:

- **`mlflashtune.core`**: Core optimization engine and configuration management
- **`mlflashtune.cli`**: Command-line interface
- **`mlflashtune.web`**: Web-based visualization and analysis tools

## Configuration System

MLFlashTune is a framework that requires user-provided configurations:

1. **Configuration files**: JSON files defining optimization parameters and data paths
2. **Hyperparameter spaces**: Python modules defining LightGBM parameter search spaces
3. **Data files**: Your datasets in CSV, Parquet, or other pandas-compatible formats

All output directories are created automatically by the framework.

## Hyperparameter Tuning

MLFlashTune requires you to define custom hyperparameter spaces for your specific use case:

### Creating Parameter Spaces

You must create your own hyperparameter space files. Here's the syntax:

### Parameter Types

- **Choice**: `{"name": "param", "type": "choice", "values": ["a", "b"], "value_type": "str"}`
- **Range (Int)**: `{"name": "param", "type": "range", "bounds": [1, 100], "value_type": "int"}`
- **Range (Float)**: `{"name": "param", "type": "range", "bounds": [0.1, 1.0], "value_type": "float"}`
- **Log Scale**: Add `"log_scale": True` for logarithmic parameter exploration
- **Boolean**: `{"name": "param", "type": "choice", "values": [True, False], "value_type": "bool"}`

### Example Parameter Space

```python
# config/hyperparameters/my_space.py
PARAMETERS = [
    # Boosting algorithm
    {"name": "boosting_type", "type": "choice", "values": ["gbdt", "dart"], "value_type": "str"},
    
    # Tree structure
    {"name": "num_leaves", "type": "range", "bounds": [20, 200], "value_type": "int"},
    {"name": "max_depth", "type": "range", "bounds": [-1, 30], "value_type": "int"},
    
    # Learning parameters
    {"name": "learning_rate", "type": "range", "bounds": [0.01, 0.3], "value_type": "float", "log_scale": True},
    {"name": "n_estimators", "type": "range", "bounds": [100, 500], "value_type": "int"},
    
    # Regularization
    {"name": "reg_alpha", "type": "range", "bounds": [1e-8, 1.0], "value_type": "float", "log_scale": True},
    {"name": "reg_lambda", "type": "range", "bounds": [1e-8, 1.0], "value_type": "float", "log_scale": True},
    
    # Sampling
    {"name": "subsample", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    {"name": "colsample_bytree", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    
    # Class balance
    {"name": "is_unbalance", "type": "choice", "values": [True, False], "value_type": "bool"},
]

def get_parameter_space():
    """Required function that returns the parameter list"""
    return PARAMETERS
```

### Configuration

Reference your parameter space in the config file:

```json
{
  "HYPERPARAMETER_PATH": "config/hyperparameters/my_space.py",
  "DATA_PATH": "data/your_dataset.csv",
  "TARGET_COLUMN": "target",
  "AE_NUM_TRIALS": 50
}
```

## Requirements

- Python 3.8+
- LightGBM 3.3.0+
- Pandas, NumPy, Scikit-learn
- Flask (for web interface)
- Plotly, Matplotlib (for visualization)

## Performance Considerations

- Always set `OMP_NUM_THREADS=1` for LightGBM to avoid thread conflicts
- Parallel training is controlled via configuration parameters
- Optimization algorithms benefit from multiple CPU cores

## Examples

### Development Run (Fast)
```bash
# 15 trials, 10 models (~15-20 minutes)
OMP_NUM_THREADS=1 python -m mlflashtune.cli --environment development
```

### Production Run
```bash
# Full optimization with more trials
OMP_NUM_THREADS=1 python -m mlflashtune.cli --environment production
```

### Validation
```bash
# Validate configuration without running optimization
python -m mlflashtune.cli --config config/environments/development.json --validate
```

## Data Requirements

- Input data should be in Parquet, CSV, or other pandas-compatible formats
- Target column must be binary (0/1) for classification
- Features are automatically handled by LightGBM (nulls, categorical encoding)
- Categorical features should be specified in configuration

## Output Structure

All outputs are organized under `outputs/`:
- `outputs/runs/`: Individual optimization run results
- `outputs/best_trials/`: Best performing configurations  
- `outputs/logs/`: Execution logs
- `outputs/visualizations/`: Generated plots and analysis

## CLI Commands

The package provides several command-line entry points:

- `mlflashtune-optimize`: Main optimization CLI
- `mlflashtune-web`: Web interface launcher  
- `mlflashtune-analyze`: Analysis tools

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use MLFlashTune in your research, please cite:

```bibtex
@software{mlflashtune,
  title={MLFlashTune: Fast Ensemble Optimization with Advanced Bayesian Methods},
  author={MLFlashTune Development Team},
  url={https://github.com/your-repo/mlflashtune},
  version={0.0.3},
  year={2025}
}
```