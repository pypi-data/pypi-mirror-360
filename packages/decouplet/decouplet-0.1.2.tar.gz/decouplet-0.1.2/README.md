# Decouplet

- A tiny wrapper around `python-decouple` that adds support for reading secrets from a directory (like Docker secrets).

## Usage
```python
from decouplet import config

DATABASE_PASSWORD = config("DATABASE_PASSWORD")
```

By default, it looks in `/run/secrets/`. Set `SECRETS_PATH` environment variable to override.
