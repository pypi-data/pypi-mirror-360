# lite_logging
A lightweight Python library for terminal logging with color support and debug information.

## Features
- Colorful terminal output
- Multiple log levels (INFO, DEBUG, WARNING, ERROR)
- Debug mode with file and line number information
- Simple and easy-to-use API

## Installation
Install the package from PyPI:

```
pip install lite_logging
```

## Usage
### Basic Logging
```python
from lite_logging.lite_logging import log

# Log levels: INFO (default), DEBUG, WARNING, ERROR
log("This is an info message")
log("This is a debug message", level="DEBUG")
log("This is a warning message", level="WARNING")
log("This is an error message", level="ERROR")
```

### Debug Logging (with file and line information)
```python
from lite_logging.lite_logging import log_debug

log_debug("This message includes file and line information")
log_debug("Debug error message", level="ERROR")
```

## Configuration
You can configure logging behavior by modifying these variables:
```python
from lite_logging.lite_logging import LOGGING_ENABLED, DEBUG_MODE, LOG_LEVEL

# Disable all logging
LOGGING_ENABLED = False

# Enable or disable debug messages
DEBUG_MODE = True

# Customize available log levels
LOG_LEVEL = ["INFO", "DEBUG", "WARNING", "ERROR", "CUSTOM"]
```

## Available Colors
The LogColors class provides the following terminal colors:

- `HEADER` (purple)
- `OKBLUE` (blue)
- `OKCYAN` (cyan)
- `OKGREEN` (green)
- `WARNING` (yellow)
- `FAIL` (red)
- `OKYELLOW` (yellow)
- `OKMAGENTA` (magenta)
- `OKWHITE` (white)
- `BOLD` (bold text)
- `UNDERLINE` (underlined text)

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
Missclick (gabrielgarronedev@gmail.com)