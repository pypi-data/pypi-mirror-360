from typing import Optional, Sequence, Union

from .config import Config
from .library import Library


def compile(prog,
            cfg: Optional[Config] = ...,
            lib: Union[Library, Sequence[Library]] = ...,
            context: Optional[dict] = ...,
            **options):
    ...
