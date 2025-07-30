from typing import Optional
import inspect

LOGGING_ENABLED = True
DEBUG_MODE = True
LOG_LEVEL = ["INFO", "DEBUG", "WARNING", "ERROR"]

class LogColors:
    """Colors for log messages
    
    :param str HEADER: Header color
    :param str OKBLUE: Blue color
    :param str OKCYAN: Cyan color
    :param str OKGREEN: Green color
    :param str WARNING: Warning color
    :param str FAIL: Fail color
    :param str ENDC: End color
    :param str OKYELLOW: Yellow color
    :param str OKMAGENTA: Magenta color
    :param str OKWHITE: White color
    :param str BOLD: Bold color
    :param str UNDERLINE: Underline"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKYELLOW = '\033[93m'
    OKMAGENTA = '\033[35m'
    OKWHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_message(message: str, level: Optional[str]) -> Optional[tuple[str, str]]:
    """Returns the message and color for the log message

    :param str message: The message to print
    :param Optional[str] level: The log level.
    
    :return: The message and color for the log message
    :rtype: Optional[tuple[str, str]]"""
    level = level.upper()
    if not LOGGING_ENABLED:
        return None
    if level not in LOG_LEVEL:
        return None
    if level == "DEBUG" and not DEBUG_MODE:
        return None
    color = {
        "INFO": LogColors.OKGREEN,
        "WARNING": LogColors.WARNING,
        "ERROR": LogColors.FAIL,
        "DEBUG": LogColors.OKCYAN
    }.get(level, LogColors.ENDC)
    message_str = ' '.join(map(str, message))
    return message_str, color

def log(*message: tuple, level: Optional[str] = "INFO"):
    """Prints log messages with color

    :param tuple message: The message to print
    :param Optional[str] level: The log level."""
    result = get_message(message, level)
    if result is None:
        return
    message_str, color = result
    print(f"{color}[{level}] {message_str}{LogColors.ENDC}")

def log_debug(*message: tuple, level: Optional[str] = "INFO"):
    """Prints log messages with color and includes the file and line number.

    :param tuple message: The message to print
    :param Optional[str] level: The log level."""
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    file_name = caller_frame.f_code.co_filename
    line_number = caller_frame.f_lineno
    debug_message = f"-> File: {file_name}, Line: {line_number}\n"
    result = get_message(message, level)
    if result is None:
        return
    message_str, color = result
    print(f"{color}{debug_message}[{level}] {message_str}{LogColors.ENDC}")