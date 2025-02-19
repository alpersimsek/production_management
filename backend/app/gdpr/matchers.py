import dataclasses
import re
import itertools
from database.models import RuleCategory
from gdpr.patchers import ReplacePatcher
from typing import Iterable, Callable, Iterator, Sequence


@dataclasses.dataclass(frozen=True)
class Match:
    """Represents matched object."""
    start: int
    end: int
    word: str
    patcher: Callable

    def process(self) -> str:
        """Patch word."""
        patched = self.patcher(self.word)
        return patched


class BaseMatcher:
    """Base matcher."""
    def __init__(self, patcher=None):
        if not patcher:
            patcher = ReplacePatcher()
        self.patcher = patcher

    def make_match(self, *args, **kwargs) -> Match:
        """Match factory function. It creates match with predefined patcher."""
        match = Match(patcher=self.patcher, *args, **kwargs)
        return match

    def _search(self, data: Iterable[str]):
        """Actual search method to override in the subclasses."""
        raise NotImplementedError
    
    def search_iter(self, data: Iterable[str]) -> Iterator[Sequence[Match]]:
        """Search words to replace in the input stream."""
        data = iter(data)
        line = next(data, None)
        if line is None:
            return []
        if not isinstance(line, str):
            raise ValueError(f"`data` should be a `io.TextIOBase` instance for {self}")

        yield from self._search(itertools.chain([line], data))


class RegexpMatcher(BaseMatcher):
    """Generic regexp matcher."""
    def __init__(self, pattern: str, **kwargs):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        super().__init__(**kwargs)

    def _search(self, data: Iterable[str]):
        """Search ``data`` for matches."""
        for line in data:
            matches = []
            for match in self.pattern.finditer(line):
                if match.lastindex is None:
                    group_indexes = [0]
                else:
                    group_indexes = range(1, match.lastindex + 1)
                for group in group_indexes:
                    start, end = match.span(group)
                    word = line[start:end]
                    match = self.make_match(start=start, end=end, word=word)
                    matches.append(match)
            yield matches


class IPAddrMatcher(RegexpMatcher):
    """IP address matcher."""
    def __init__(self, **kwargs):
        pattern = rf"\b((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\b"
        super().__init__(pattern, **kwargs)


class MacAddrMatcher(RegexpMatcher):
    """Mac address matcher."""
    def __init__(self, **kwargs):
        pattern = rf"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})|[0-9A-Fa-f]{12}\b"
        super().__init__(pattern, **kwargs)