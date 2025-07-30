from json import dumps
from pathlib import Path

from . import LastRun, ProspectDatabase


class LocalFileSystem(ProspectDatabase):
    """
    Simplest LocalFileSystem implementation
    """
    def __init__(self, path: Path = Path("prospect_database.d")):
        super().__init__()
        self._db = path
        self._db.mkdir(exist_ok=True, parents=True)

    def __contains__(self, prospect: dict[str, str]) -> bool:
        record = self._db / f"{prospect['product_id']}.json"
        return record.exists()

    def write(self, prospect: dict[str, str]) -> None:
        """Save product"""
        record = self._db / f"{prospect['product_id']}.json"
        text = dumps(prospect, indent=4)

        record.write_text(text)

    def last_run(self, key: str) -> LastRun:
        """
        The API is deprecated and this new method is not supported
        """
        raise NotImplementedError
