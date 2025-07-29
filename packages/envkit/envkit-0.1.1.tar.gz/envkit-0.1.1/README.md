# EnvKit

*A lightweight package for parsing environment variables.*

Does not work with [mypy](https://github.com/python/mypy) yet, but it does work with [pyright](https://github.com/microsoft/pyright)/[basedpyright](https://github.com/DetachHead/basedpyright).

## Installation

```bash
pip install envkit
```


## Usage

```python
from envkit import Fields

# Required string with minimum length
api_key = Fields.str("API_KEY", min_length=32)

# Optional integer with default and range
port = Fields.int("PORT", default=8080, min_value=1, max_value=65535)

# Boolean with default
debug = Fields.bool("DEBUG", default=False)

# Enum parsing
log_level = Fields.enum("LOG_LEVEL", enum=LogLevel, default=LogLevel.INFO)
```
