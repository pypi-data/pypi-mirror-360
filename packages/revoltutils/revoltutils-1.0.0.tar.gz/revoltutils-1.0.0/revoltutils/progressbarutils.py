from alive_progress import alive_bar
from typing import Optional

class ProgressBar:
    def __init__(self, total: Optional[int] = None, title: str="Progress") -> None:
        self.total = total
        self.title = title
        self._bar = alive_bar(total, title=title, enrich_print=False)
        self._update = None

    def start(self) -> None:
        self._update = self._bar.__enter__()

    def update(self,) -> None:
        if self._update:
            self._update()

    def close(self) -> None:
        if self._bar:
            self._bar.__exit__(None, None, None)