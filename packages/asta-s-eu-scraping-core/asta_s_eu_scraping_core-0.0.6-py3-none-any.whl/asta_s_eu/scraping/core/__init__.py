"""
Ada Automation Selenium Bot
"""
from . import typing
from .config import CONFIG_DIR
from .decorators import catch_alarms
from .prospect_database import ProspectDatabase
from .send_email import gmailing_logs

__all__ = [
    'CONFIG_DIR',
    'catch_alarms',
]
