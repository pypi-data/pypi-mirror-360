# safeio 📂

A tiny Python library to simplify file I/O with features like appending, backups, and log rotation.

## Install

```bash
pip install safeio
```

## Usage

```python
from safeio import File

file = File("example.txt")
file.write("Hello").append("World").backup().rotate_if_large(max_mb=1)
```
