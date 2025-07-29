# Elara Wrapper

A FastAPI middleware package to validate requests to Elara agents based on the permissions set in their ENS name.

## Installation

```bash
pip install elara-wrapper
```

## Usage

### Basic Usage

```python
import os
from fastapi import FastAPI
from elara_wrapper import add_elara_middleware

app = FastAPI()

# Add the Elara middleware with the agent name automatically injected in Oasis ROFL
middleware = add_elara_middleware(app, os.getenv("ELARA_AGENT_ENS_NAME"))


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Development

This package uses Poetry for dependency management:

```bash
poetry install
poetry run python example_usage.py
```

## License

MIT License