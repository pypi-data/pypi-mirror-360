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

### 1. Basic Usage

```bash
# Run optimization with default settings
python -m mlflashtune.cli --environment development

# Run with custom parameters
python -m mlflashtune.cli --config config/environments/development.json --trials 20
```

### 2. Configuration

Create a configuration file or use one of the provided templates:

```json
{
  "DATA_PATH": "data/your_dataset.parquet",
  "TARGET_COLUMN": "target",
  "FEATURES": ["feature1", "feature2", "feature3"],
  "CATEGORICAL_FEATURES": ["feature1"],
  "AE_NUM_TRIALS": 50,
  "N_ENSEMBLE_GROUP_NUMBER": 20,
  "RANDOM_SEED": 42
}
```

### 3. Web Interface

```bash
# Start interactive web interface
python -m mlflashtune.web.interactive.app

# Or use the convenience script
./scripts/start-web.sh
```

## Architecture

MLFlashTune is organized into several key modules:

- **`mlflashtune.core`**: Core optimization engine and configuration management
- **`mlflashtune.cli`**: Command-line interface
- **`mlflashtune.web`**: Web-based visualization and analysis tools

## Configuration System

The system uses a hierarchical configuration approach:

1. **Environment configs**: Main configuration files per environment
2. **Hyperparameter spaces**: Python modules defining search spaces  
3. **Templates**: Predefined configs for specific domains

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
  version={0.0.2},
  year={2025}
}
```