"""
Helper function for scrapers
"""
from typing import Callable

import datetime
import logging
from pathlib import Path

from .config import CONFIG_DIR
from .prospect_database.dynamo_db import DynamoDB as ProspectDatabase

LOG = logging.getLogger(__name__)


def activate_coupons_just_once_per_day_by_dynamodb(
        check_on_key: str,
        activate_coupons_callback: Callable[[], None]) -> None:
    """
    Run just once per day
    """
    db = ProspectDatabase()
    last_run = db.last_run(check_on_key)
    if last_run.successful_less_than_24hour_ago():
        return

    if last_run.failed_less_than_24hour_ago_on_current_host():
        return

    try:
        activate_coupons_callback()
        last_run.mark_successful_run()
    except (Exception, BaseException):
        last_run.mark_failed_run_per_current_host()
        raise


def activate_coupons_just_once_per_day_by_filesystem(
        check_on_key: str,
        activate_coupons_callback: Callable[[], None]) -> None:  # pragma: deprecated
    """
    Run just once per day

    Deprecated in favor of ``activate_coupons_just_once_per_day_by_dynamodb``
    """

    last_run = Path(CONFIG_DIR, check_on_key)
    if not last_run.exists():
        last_run.touch()
        activate_coupons_callback()
        return

    last_time_modified = datetime.datetime.fromtimestamp(last_run.stat().st_mtime)
    more_than_one_day = (datetime.datetime.utcnow() - last_time_modified).days > 1
    if more_than_one_day:
        last_run.unlink()
        last_run.touch()
        activate_coupons_callback()
        return

    LOG.info('Already run once per day')


__all__ = [
    'activate_coupons_just_once_per_day_by_dynamodb'
]
