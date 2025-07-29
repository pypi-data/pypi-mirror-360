# fastloguru

`fastloguru` is a wrapper around [Loguru](https://github.com/Delgan/loguru) that provides:
- Named loggers with automatic file naming
- Dual logging files: one plain, one color-coded
- Preconfigured format, rotation, and retention
- Cross-platform logging directories
- Optional log tagging for filtering

## Installation

```bash
pip install fastloguru
```

## Usage

```python
from fastloguru import get_logger

log1 = get_logger("api")
log2 = get_logger("auth", prefix="server1", tag="auth")

log1.info("API started")
log2.error("Authentication failed")
```
