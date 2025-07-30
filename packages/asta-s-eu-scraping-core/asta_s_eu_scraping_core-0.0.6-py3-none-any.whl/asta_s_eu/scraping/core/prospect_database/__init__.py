from typing import Any, Callable, Iterable, Optional, Sequence, TypedDict, cast

import abc
import datetime
import logging
import pathlib
import socket
import time

LOG = logging.getLogger(__name__)


class DataType(TypedDict):
    """Dynamodb Data Type Definition"""
    successful: dict[str, str]
    failed: dict[str, dict[str, str]]


def _default_progress_bar_log_function(index: int, item: Any, size: Optional[int]) -> None:
    """
    Default progress bar log function to be used if is not set
    ``log_function`` in ``progress_bar_log`` function.
    """
    if size:
        print(f'Processed {index}/{size}, last_processed_item {item}')
    else:
        print(f'Processed {index}/unknown,  last_processed_item {item}')


def progress_bar_log(iterator: Iterable[Any],

                     log_function: Callable[
                         [int, Any, Optional[int]], None
                     ] = _default_progress_bar_log_function,

                     display_after_n_seconds: int = 10) -> Iterable[Any]:
    """
    Progress bar log

    Example::

        def _log_function(index: int, item: Dict[str, Any], size: int):
            LOG.info('Precessed %r/%r %r%% prospects', index, size, round(index/size * 100))

        for prospect in progress_bar_log(prospects, _log_function):
            if prospect not in self:
                self.write(prospect)
                new_prospects.append(prospect)
    """
    begin_at = time.time()

    size = None
    if hasattr(iterator, '__len__'):
        size = len(iterator)  # type: ignore[arg-type]

    for index, item in enumerate(iterator, start=1):
        now = time.time()
        if now - begin_at > display_after_n_seconds:
            log_function(index, item, size)
            begin_at = now

        yield item


# TODO use pydantic instead of raw class
class Prospect:  # pylint: disable=too-many-instance-attributes
    """
    Prospect object,
    can be compared and hashed in a set comparing with just a raw representation as a dict.
    """
    def __init__(self, prospect: Optional[dict[str, Any]] = None, **kwargs: Any) -> None:
        self.location: str
        self.product_id: str
        self.price: Optional[str] = None
        self.text: str

        self.link: str
        self.img: Optional[str] = None
        self.date: Optional[str] = None
        self.tag_list: Optional[Sequence[str]] = None

        if not (prospect or kwargs):
            raise ValueError('One of prospect is required')

        if prospect and kwargs:
            raise ValueError('Mutual exclusion between prospect and kwargs, choose one')

        if not prospect:
            prospect = kwargs

        if prospect and isinstance(prospect, dict):
            self.location = prospect['location']
            self.product_id = prospect['product_id']
            self.price = prospect.get('price')
            self.text = prospect['text']

            self.slug = self._text_to_slug()

            self.link = prospect['link']
            self.img = prospect.get('img')
            self.date = prospect.get('date')
            self.tag_list = prospect.get('tag_list')
            return

        raise NotImplementedError(type(prospect))

    def __lt__(self, prospect: Any) -> bool:
        if not isinstance(prospect, Prospect):
            raise NotImplementedError

        if self.slug >= prospect.slug:
            return False

        return True

    def __str__(self) -> str:
        raise NotImplementedError

    def _text_to_slug(self) -> str:
        slug = (
            self
            .text.upper()
            .replace('Ö', 'O')
            .replace('Ä', 'A')
            .replace('Ü', 'U')
            .replace(' ', '_')
            .replace('/', '_')
            .replace('°', '_')
            .replace('(', '')
            .replace(')', '')
            .replace(',', '')
            .replace('.', '')
            .replace('-', '_')
            .replace('–', '_')
            .replace('__', '_')
            .replace('__', '_')
        )
        if '0' <= slug[0] <= '9':
            slug = '_' + slug

        slug = slug.rstrip('_')

        return slug

    def to_print(self) -> Sequence[str]:
        """
        Print Object as code sample to be used as fixture for test assertions.
        """
        # noinspection PyListCreation
        out = []

        out.append("")
        out.append(f"{self.slug} = Prospect(")
        out.append(f"        location={self.location!r},")
        out.append(f"        product_id={self.product_id!r},")
        if self.price:
            out.append(f"        price={self.price!r},")
        out.append(f"        text={self.text!r},")
        out.append(f"        link={self.link!r},")
        if self.img:
            out.append(f"        img={self.img!r},")
        if self.date:
            out.append(f"        date={self.date!r},")
        if self.tag_list:
            out.append(f"        tag_list={self.tag_list!r},")
        out.append(")")
        return out

    @staticmethod
    def print_from_prospect_list(
            prospect_list: Iterable['Prospect'],
            dump_path: Optional[pathlib.Path] = None) -> str:
        """
        Print List of Object as code sample to be used as fixture for test assertions.
        """
        out: list[str] = []
        for prospect in sorted(prospect_list):
            out.extend(prospect.to_print())

        res = "\n".join(out)

        if dump_path:
            dump_path.write_text(res)

        return res


class LastRun(metaclass=abc.ABCMeta):
    """
    Abstract interface for encapsulating rules to:

    - do not run again if previous run was successfully an any host
    - run on current host if previous run another host failed
    """
    def __init__(self) -> None:
        self._data: DataType = {
            "successful": {},
            "failed": {},
        }

    @property
    def hostname(self) -> str:
        """
        Get current OS host name
        """
        return socket.gethostname()

    def successful_less_than_24hour_ago(self) -> bool:
        """
        Check if passed on any host
        """
        successful = cast(dict[str, str], self._data.get('successful'))
        if not successful:
            return False

        # 2023-12-13T11:00:17.276950
        # -or-
        # 2024-03-20T10:38:26.609310+00:00
        # TODO: remove this check after db is updated as 2024
        successful_datetime = successful['datetime']
        if "+" not in successful_datetime:
            successful_datetime += "+00:00"

        when = datetime.datetime.fromisoformat(successful_datetime)
        now = datetime.datetime.now(datetime.UTC)

        return (now - when).days < 1

    def failed_less_than_24hour_ago_on_current_host(self) -> bool:
        """
        Check if failed on the current host
        """
        failed = self._data.get('failed')
        if not failed:
            return False

        failed_on_host = failed.get(self.hostname)
        if not failed_on_host:
            return False

        # 2022-06-28T23:59:59
        when = datetime.datetime.fromisoformat(failed_on_host['datetime'])
        now = datetime.datetime.now(datetime.UTC)
        return (now - when).days < 1

    @abc.abstractmethod
    def mark_successful_run(self) -> None:
        """
        To be implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def mark_failed_run_per_current_host(self) -> None:
        """
        To be implemented
        """
        raise NotImplementedError


class ProspectDatabase(metaclass=abc.ABCMeta):
    """
    Interface for any prospect database implementation e.g. Dynamodb, Postgres, MongoDb
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        LOG.info("Capture all prospects")

    def __contains__(self, prospect: dict[str, str]) -> bool:
        raise NotImplementedError

    def write(self, prospect: dict[str, str]) -> None:
        """Upsert and item into database"""
        raise NotImplementedError

    @abc.abstractmethod
    def last_run(self, key: str) -> LastRun:
        """
        To be implemented last run factory method
        """
        raise NotImplementedError

    def capture(self, prospects: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        """
        Save new items into database out of new prospects
        :return: freshly inserted new prospects from the current session
        """
        new_prospects = []

        def _log_function(index: int, _item: dict[str, Any], size: int) -> None:
            LOG.info('Precessed %r/%r %r%% prospects', index, size, round(index/size * 100))

        for prospect in progress_bar_log(prospects, _log_function):  # type: ignore[arg-type]
            if prospect not in self:
                self.write(prospect)
                new_prospects.append(prospect)

        return new_prospects
