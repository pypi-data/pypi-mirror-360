# Installation

## Requirements

slack-models requires Python 3.12 or higher and depends on Pydantic 2.x for data validation and serialization.

### System Requirements

- Python 3.12+
- pip (Python package installer)

### Dependencies

The library has minimal dependencies:

- `pydantic>=2.11.3,<3` - Core data validation and serialization

## Installation Methods

### Using pip (Recommended)

Install slack-models from PyPI using pip:

```bash
pip install slack-models
```

### Using pip with specific version

To install a specific version:

```bash
pip install slack-models==1.0.0
```

### Development Installation

For development or contributing to the project:

```bash
# Clone the repository
git clone https://github.com/gmr/slack-models.git
cd slack-models

# Install in development mode
pip install -e '.[dev]'

# Install pre-commit hooks
pre-commit install
```

## Verification

Verify your installation by importing the library:

```python
import slack_models

# Check the installed version
print(slack_models.version)

# Import some models to test
from slack_models import User, Channel, MessageEvent
print("Installation successful!")
```

## Virtual Environment (Recommended)

It's recommended to install slack-models in a virtual environment:

```bash
# Create a virtual environment
python -m venv slack-models-env

# Activate the virtual environment
# On Linux/macOS:
source slack-models-env/bin/activate
# On Windows:
slack-models-env\Scripts\activate

# Install slack-models
pip install slack-models
```

## Troubleshooting

### Python Version Issues

If you encounter Python version compatibility issues:

```bash
# Check your Python version
python --version

# Make sure you're using Python 3.12+
python3.12 -m pip install slack-models
```

### Dependency Conflicts

If you encounter dependency conflicts with Pydantic:

```bash
# Install with specific Pydantic version
pip install slack-models pydantic>=2.11.3,<3
```

### Development Dependencies

For development, install additional dependencies:

```bash
pip install -e '.[dev]'
```

This includes tools for:
- Testing: `pytest`, `coverage`
- Linting: `ruff`, `mypy`
- Documentation: `mkdocs`, `mkdocs-material`
- Pre-commit hooks: `pre-commit`

## Next Steps

Once installed, continue with the [Quick Start](quickstart.md) guide to begin using slack-models in your project.
