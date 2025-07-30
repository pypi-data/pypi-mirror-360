from typing import Any, Callable

import functools
import logging
import re
from pathlib import Path

from . import send_email


def _clean_previous_alarms_logs(alarm_log: Path) -> None:
    """
    Receive a file like "payback.de.alert.2021-12-01.log"
    and
    delete file like "payback.de.alert.2021-11-30.log"
    """

    prefix = alarm_log.name.rsplit(".", 2)[0]
    alarms_logs = alarm_log.parent.glob(f"{prefix}.*.log")
    for the_alarms_logs in alarms_logs:
        if the_alarms_logs != alarm_log:
            the_alarms_logs.unlink()


# FIXME: reduce number os arguments with data structure pylint: disable=fixme
# pylint: disable=too-many-arguments,too-many-positional-arguments
def catch_alarms(subject: str, log: logging.Logger, alarm_log: Path,
                 gmail_from: str, gmail_to: str, gmail_password: str) -> Callable[..., Any]:
    """
    Catch unexpected errors from code and emailing them to a gmail account
    """
    def actual_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            exception = None
            try:
                func(*args, **kwargs)
            except KeyboardInterrupt:
                log.info('Exit the application with CTRL^C')
            except (Exception, BaseException) as exc:  # pylint: disable=broad-except
                log.exception(exc)
                exception = exc
            finally:
                if alarm_log.exists():
                    content = alarm_log.read_text()
                    if content:
                        find = re.compile(r"look into '(.+?\.png)'")
                        files = [Path(path) for path in find.findall(content)]
                        files.append(alarm_log)

                        send_email.gmailing_logs(
                            content,
                            send_email.Email(
                                sender=gmail_from,
                                to=gmail_to,
                                subject=subject,
                                password=gmail_password,
                                html='to-be-filed',
                                files=files
                            )
                        )
                        logging.shutdown()

                        new_path = alarm_log.with_name(alarm_log.name.replace(".log", ".sent.log"))
                        alarm_log.rename(new_path)
                    else:
                        logging.shutdown()

                    _clean_previous_alarms_logs(alarm_log)

                if exception:
                    raise SystemExit(1) from exception

        return wrapper
    return actual_decorator
# pylint: enable=too-many-arguments,too-many-positional-arguments
