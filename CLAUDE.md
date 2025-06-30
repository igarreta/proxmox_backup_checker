# CLAUDE.md - Python Project
Store in project root directory. Inherits from ~/.claude/CLAUDE.md

## Download Template
```bash
git clone --depth 1 https://github.com/igarreta/claude.md.git
cp claude.md/python/CLAUDE.md ./
rm -rf claude.md
```

## Python preferred Stack
- Python: 3.13
- Package manager: uv (preferred over venv)
- Dependencies: pyproject.toml + requirements.txt for Docker
- Framework: FastAPI
- Database: SQLModel (type-safe SQLAlchemy)
- Logging: MyLogger submodule

## Project Structure
```
project_name/
├── README.md
├── CLAUDE.md  # This file
├── pyproject.toml
├── config.json
├── .pre-commit-config.yaml
├── .gitignore
├── main.py
├── mylogger/              # Git submodule
│   └── mylogger.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── modules/
│       ├── __init__.py
│       └── your_module.py
├── tests/
│   ├── __init__.py
│   └── test_your_module.py
├── docs/                  # Optional
├── log/                   # Write permissions in Docker
└── var/                   # Write permissions in Docker
```

## Setup Commands
```bash
# Project initialization
git clone --recurse-submodules <repo-url>
cd project_name
uv venv
uv pip install -e .
pre-commit install

# If cloned without submodules
git submodule update --init --recursive

# Development
uv pip install -e ".[dev]"
uv run python main.py
```

## Docker Configuration

Aplication code shall be incorporated into the container via a read-only volume, for a shorter development circuit

### Dockerfile
```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv for faster package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system .

CMD ["python", "main.py"]
```

### docker-compose.yaml
```yaml
services:
  project_name:
    container_name: project_name
    restart: unless-stopped
    build: .
    volumes:
      - .:/app:ro                # Read-only base
      - ./log:/app/log:rw        # Write access for logs
      - ./var:/app/var:rw        # Write access for data
    working_dir: /app
    environment:
      - PYTHONUNBUFFERED=1
      - TZ=America/Argentina/Buenos_Aires
    env_file:
      - ~/etc/project_name.env
    # ports:
    #   - "8000:8000"  # Uncomment if external access needed
```

## Configuration Management

### config.json (Non-secret settings)
```json
{
  "debug": true,
  "log_level": "DEBUG",
  "app_name": "project_name",
  "version": "0.1.0",
}
```

### Settings Pattern
```python
import json
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Non-secret config from JSON
    debug: bool = True
    log_level: str = "DEBUG"
    app_name: str
    version: str
    
    # Secrets from environment
    api_key: str
    database_url: str
    
    def __init__(self):
        # Load config.json
        try:
            with open('config.json') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
        
        super().__init__(**config)
    
    class Config:
        env_file = "~/etc/project_name.env"

settings = Settings()
```

## Pre-commit Configuration

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Setup & Override
```bash
# Install pre-commit hooks
pre-commit install

# Normal commit (runs checks)
git commit -m "add feature"

# Override when needed (WIP, emergency fixes)
git commit -m "WIP: debugging" --no-verify
```

## Dependencies (pyproject.toml)
```toml
[project]
name = "project_name"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "pydantic-settings",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "ruff",
    "mypy",
    "pre-commit",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.mypy]
python_version = "3.13"
strict = true
```

## Logging Setup
```python
import logging
import logging.handlers
import datetime
import sys
from mylogger.mylogger import MyLogger

# Configuration
LOG_FILENAME = 'log/project_name'
LOG_LEVEL = logging.DEBUG

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.propagate = False

# Weekly rotation, keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILENAME, 
    when="W0", 
    atTime=datetime.time(0, 0, 0), 
    backupCount=3
)

formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Redirect stdout/stderr to logger
sys.stdout = MyLogger(logger, logging.INFO)
sys.stderr = MyLogger(logger, logging.ERROR)
```

## .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.Python
.venv/
.uv-cache/
uv.lock

# Project specific
log/
var/
.env
.vscode/

# Distribution
dist/
build/
*.egg-info/
```

## Code Standards
- Line length: 88 characters (Black default)
- Type hints: Required for all functions
- Docstrings: Google style for all public functions
- Import order: stdlib, third-party, local
- Code formatting: Black + Ruff
- Testing: pytest for new functionality

## Development Workflow
1. Check git status: `git fetch && git status`
2. Run tests: `uv run pytest tests/ -v`
3. Format code: `uv run black . && uv run ruff check --fix .`
4. Type check: `uv run mypy src/`
5. Commit: Clear message + `git push`

## Common Commands
```bash
# Development
uv run python main.py
uv run pytest tests/ -v
uv run black . && uv run ruff check --fix .

# Docker
docker compose up -d
docker compose logs -f project_name
docker compose ps  # Check health status

# Dependencies
uv add package_name
uv add --group dev package_name
docker compose build        # Rebuild after adding deps
```
