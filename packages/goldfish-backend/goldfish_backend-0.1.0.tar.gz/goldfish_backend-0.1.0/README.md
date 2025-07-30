# Goldfish Backend

Shared backend package for the Goldfish AI-First Personal Knowledge Management system.

## Overview

This package contains the core shared components used by both the Goldfish CLI and web application:

- **Models**: SQLModel database models for all entities
- **Services**: Business logic layer for entity recognition and management
- **Core**: Database connection, authentication, and utility functions
- **CLI**: Command-line interface components

## Installation

```bash
pip install goldfish-backend
```

## Usage

This package is designed to be used as a dependency by the Goldfish CLI and web application. It provides the shared data layer and business logic.

### In your code:

```python
from goldfish_backend.models import User, Person, Project, Task
from goldfish_backend.services import EntityRecognitionService
from goldfish_backend.core.database import get_session
```

## Development

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/ tests/
```

## Architecture

- `models/`: SQLModel database models
- `services/`: Business logic services
- `core/`: Core utilities (database, auth)
- `cli/`: Command-line interface components

## License

MIT License