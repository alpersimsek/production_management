import dataclasses
import re
import itertools
from database.models import RuleCategory
from gdpr.patchers import ReplacePatcher
from typing import Iterable, Callable, Iterator, Sequence
import settings
from logger import logger

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
                group_index = 0 if match.lastindex is None else 1
                start, end = match.span(group_index)
                word = match.group(group_index)
                if word:
                    logger.debug(
                        {
                            "event": "match_found",
                            "matcher": self.__class__.__name__,
                            "line": line[:50],
                            "word": word,
                            "start": start,
                            "end": end,
                        }
                    )
                    match_obj = self.make_match(start=start, end=end, word=word)
                    matches.append(match_obj)
            yield matches

class IPAddrMatcher(RegexpMatcher):
    """IP address matcher."""
    def __init__(self, **kwargs):
        pattern = r"\b((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\b"
        super().__init__(pattern, **kwargs)

class MacAddrMatcher(RegexpMatcher):
    """Mac address matcher."""
    def __init__(self, **kwargs):
        pattern = r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})|[0-9A-Fa-f]{12}\b"
        super().__init__(pattern, **kwargs)

class SIPPhoneMatcher(RegexpMatcher):
    """Matcher for phone numbers in SIP URIs."""
    def __init__(self, pattern: str, **kwargs):
        super().__init__(pattern, **kwargs)
        self.exceptions = [re.compile(p, re.IGNORECASE) for p in settings.EXCEPTION_PATTERNS.get('phone_num', [])]

    def _search(self, data: Iterable[str]):
        for line in data:
            matches = []
            for match in self.pattern.finditer(line):
                if not (match.lastindex and match.lastindex >= 1):
                    continue
                start, end = match.span(1)  # Group 1: phone number
                word = match.group(1)
                if not word:
                    continue
                if any(exc.match(word) for exc in self.exceptions):
                    logger.debug(
                        {
                            "event": "match_skipped",
                            "matcher": self.__class__.__name__,
                            "word": word,
                            "reason": "exception_match",
                        }
                    )
                    continue
                if re.search(r'\.\d{2}\.\d{2}', word):
                    logger.debug(
                        {
                            "event": "match_skipped",
                            "matcher": self.__class__.__name__,
                            "word": word,
                            "reason": "date_like",
                        }
                    )
                    continue
                digits = re.sub(r'\D', '', word)
                if len(digits) < 7 or not re.match(r'[\+\d]', word):
                    logger.debug(
                        {
                            "event": "match_skipped",
                            "matcher": self.__class__.__name__,
                            "word": word,
                            "reason": "invalid_phone",
                        }
                    )
                    continue
                logger.debug(
                    {
                        "event": "match_found",
                        "matcher": self.__class__.__name__,
                        "line": line[:50],
                        "word": word,
                        "start": start,
                        "end": end,
                    }
                )
                match_obj = self.make_match(start=start, end=end, word=word)
                matches.append(match_obj)
            yield matches

class SIPUsernameMatcher(RegexpMatcher):
    """Matcher for usernames in SIP URIs."""
    def __init__(self, pattern: str, **kwargs):
        super().__init__(pattern, **kwargs)

    def _search(self, data: Iterable[str]):
        for line in data:
            matches = []
            for match in self.pattern.finditer(line):
                if not (match.lastindex and match.lastindex >= 1):
                    continue
                start, end = match.span(1)  # Group 1: username
                word = match.group(1)
                if not word:
                    continue
                # Skip JSON-like strings
                if word.startswith('{') or '":' in word:
                    logger.debug(
                        {
                            "event": "match_skipped",
                            "matcher": self.__class__.__name__,
                            "word": word,
                            "reason": "json_like",
                        }
                    )
                    continue
                digits = re.sub(r'\D', '', word)
                if len(digits) >= 7 and re.match(r'[\+\d]', word):
                    logger.debug(
                        {
                            "event": "match_skipped",
                            "matcher": self.__class__.__name__,
                            "word": word,
                            "reason": "phone_like",
                        }
                    )
                    continue
                logger.debug(
                    {
                        "event": "match_found",
                        "matcher": self.__class__.__name__,
                        "line": line[:50],
                        "word": word,
                        "start": start,
                        "end": end,
                    }
                )
                match_obj = self.make_match(start=start, end=end, word=word)
                matches.append(match_obj)
            yield matches

class SIPDomainMatcher(RegexpMatcher):
    """Matcher for domains in SIP URIs (skips IPs)."""
    def __init__(self, pattern: str, **kwargs):
        super().__init__(pattern, **kwargs)

    def _search(self, data: Iterable[str]):
        for line in data:
            matches = []
            for match in self.pattern.finditer(line):
                if not (match.lastindex and match.lastindex >= 1):
                    continue
                start, end = match.span(1)  # Group 1: domain
                word = match.group(1)
                if not word:
                    continue
                if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', word):
                    logger.debug(
                        {
                            "event": "match_skipped",
                            "matcher": self.__class__.__name__,
                            "word": word,
                            "reason": "ip_like",
                        }
                    )
                    continue
                logger.debug(
                    {
                        "event": "match_found",
                        "matcher": self.__class__.__name__,
                        "line": line[:50],
                        "word": word,
                        "start": start,
                        "end": end,
                    }
                )
                match_obj = self.make_match(start=start, end=end, word=word)
                matches.append(match_obj)
            yield matches