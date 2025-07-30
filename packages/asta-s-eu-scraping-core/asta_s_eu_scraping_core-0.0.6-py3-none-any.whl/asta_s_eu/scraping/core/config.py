from typing import Final

from pathlib import Path

CONFIG_DIR: Final = Path("~/.config/ada-automation").expanduser()
CONFIG_DIR.mkdir(exist_ok=True, parents=True)

__all__ = ["CONFIG_DIR"]
