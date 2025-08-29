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
    def __init__(self, patcher=None, category=None):
        if not patcher:
            patcher = ReplacePatcher()
        self.patcher = patcher
        self.category = category

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
    """Enhanced regexp matcher with better group handling and debugging."""
    def __init__(self, pattern: str, **kwargs):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        super().__init__(**kwargs)

    def _is_exception_match(self, word: str) -> bool:
        """Check if the word matches any exception patterns for this category."""
        if not self.category or not hasattr(settings, 'EXCEPTION_PATTERNS'):
            return False
        
        category_name = self.category.value if hasattr(self.category, 'value') else str(self.category)
        if category_name not in settings.EXCEPTION_PATTERNS:
            return False
        
        exception_patterns = settings.EXCEPTION_PATTERNS[category_name]
        for exception_pattern in exception_patterns:
            if re.match(exception_pattern, word, re.IGNORECASE):
                logger.debug(
                    {
                        "event": "exception_match_found",
                        "matcher": self.__class__.__name__,
                        "category": category_name,
                        "word": word,
                        "exception_pattern": exception_pattern,
                    }
                )
                return True
        
        return False

    def _get_best_capturing_group(self, match) -> tuple[int, str]:
        """Get the best capturing group that contains actual content."""
        # Try to find a non-empty capturing group
        for i in range(1, match.lastindex + 1 if match.lastindex else 0):
            group_content = match.group(i)
            if group_content and group_content.strip():
                return i, group_content
        
        # Fallback to group 0 (full match) if no capturing groups have content
        return 0, match.group(0)

    def _validate_match(self, match, group_index: int, word: str) -> bool:
        """Validate if the match is valid and should be processed."""
        # Skip empty or whitespace-only matches
        if not word or not word.strip():
            return False
        
        # Skip matches that are too short (likely false positives)
        if len(word.strip()) < 2:
            return False
        
        # Check if this is an exception match
        if self._is_exception_match(word.strip()):
            return False
            
        return True

    def debug_pattern(self, test_strings: list[str]) -> dict:
        """Debug method to test regex pattern with sample strings."""
        results = []
        
        for test_string in test_strings:
            matches = list(self.pattern.finditer(test_string))
            match_info = []
            
            for i, match in enumerate(matches):
                groups = []
                for j in range(match.lastindex + 1) if match.lastindex else [0]:
                    group_content = match.group(j)
                    groups.append({
                        "group_index": j,
                        "content": group_content,
                        "span": match.span(j),
                        "is_capturing": j > 0
                    })
                
                match_info.append({
                    "match_index": i,
                    "full_match": match.group(0),
                    "full_span": match.span(),
                    "groups": groups,
                    "best_group": self._get_best_capturing_group(match)
                })
            
            results.append({
                "test_string": test_string,
                "matches": match_info
            })
        
        return {
            "pattern": self.pattern.pattern,
            "flags": self.pattern.flags,
            "test_results": results
        }

    def _search(self, data: Iterable[str]):
        """Enhanced search with better group handling and validation."""
        for line in data:
            matches = []
            line_matches = list(self.pattern.finditer(line))
            
            # Sort matches by start position to handle overlapping matches
            line_matches.sort(key=lambda m: m.start())
            
            for match in line_matches:
                try:
                    # Get the best capturing group
                    group_index, word = self._get_best_capturing_group(match)
                    
                    # Validate the match
                    if not self._validate_match(match, group_index, word):
                        logger.debug(
                            {
                                "event": "match_skipped",
                                "matcher": self.__class__.__name__,
                                "reason": "invalid_match",
                                "word": word,
                                "start": match.start(),
                                "end": match.end(),
                            }
                        )
                        continue
                    
                    # Get the span for the specific group
                    if group_index == 0:
                        start, end = match.span()
                    else:
                        start, end = match.span(group_index)
                    
                    # Create match object
                    match_obj = self.make_match(start=start, end=end, word=word)
                    matches.append(match_obj)
                    
                    logger.debug(
                        {
                            "event": "match_found",
                            "matcher": self.__class__.__name__,
                            "line_preview": line[:50],
                            "word": word,
                            "start": start,
                            "end": end,
                            "group_index": group_index,
                            "full_match": match.group(0),
                            "all_groups": [match.group(i) for i in range(match.lastindex + 1)] if match.lastindex else [match.group(0)],
                        }
                    )
                    
                except Exception as e:
                    logger.warning(
                        {
                            "event": "match_processing_error",
                            "matcher": self.__class__.__name__,
                            "error": str(e),
                            "match": str(match),
                            "line_preview": line[:50],
                        }
                    )
                    continue
            
            yield matches

class IPAddrMatcher(RegexpMatcher):
    """IP address matcher."""
    def __init__(self, **kwargs):
        pattern = r"\b((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\b"
        super().__init__(pattern, **kwargs)

class MacAddrMatcher(RegexpMatcher):
    """Matcher for MAC addresses."""
    def __init__(self, **kwargs):
        pattern = r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})|[0-9A-Fa-f]{12}\b"
        super().__init__(pattern, **kwargs)