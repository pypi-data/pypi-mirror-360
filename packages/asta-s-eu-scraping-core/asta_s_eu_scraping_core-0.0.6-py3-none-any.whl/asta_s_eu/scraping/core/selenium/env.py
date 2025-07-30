import logging
import os

LOG = logging.getLogger(__name__)

CHROME_DEBUGGER_ADDRESS_PORT = os.getenv('ADA_CHROME_DEBUGGER_ADDRESS_PORT')

if not CHROME_DEBUGGER_ADDRESS_PORT:
    raise ValueError("env 'ADA_CHROME_DEBUGGER_ADDRESS_PORT' is not set with a value")  # pragma: no cover

ADA_CHROME_DRIVER_EXECUTABLE_PATH = os.getenv('ADA_CHROME_DRIVER_EXECUTABLE_PATH')

__all__ = [
    "CHROME_DEBUGGER_ADDRESS_PORT",
    "ADA_CHROME_DRIVER_EXECUTABLE_PATH"
]
