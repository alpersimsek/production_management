import abc
import itertools
from gdpr.matchers import BaseMatcher, RegexpMatcher, IPAddrMatcher, MacAddrMatcher, Match
# from gdpr.patchers import ReplacePatcher
# from database.models import ContentType
from typing import Union, Sequence, Mapping, Any, Optional, Iterator


class BaseProcessor(abc.ABC):
    """Base processor class."""
    def __init__(self, matchers: Sequence[BaseMatcher]):
        self.matchers = matchers

    @staticmethod
    def get_overlap(a: tuple[int, int], b: tuple[int, int]) -> int:
        """Returns overlap length between closed intervals a and b."""
        return max(0, min(a[1], b[1]) - max(a[0], b[0]))

    def analyze(self, data):
        result = []
        for matcher in self.matchers:
            matches = list(matcher.search_iter(data))
            result.append(matches)

        per_line_matches = []
        for line_matches in zip(*result):
            detected_intervals = []
            filtered_matches = []
            for rule_matches in line_matches:
                for match in rule_matches:
                    match_interval = (match.start, match.end)
                    for detected_interval in detected_intervals:
                        if self.get_overlap(match_interval, detected_interval) > 0:
                            break
                    else:
                        # No overlaps
                        detected_intervals.append(match_interval)
                        filtered_matches.append(match)
            filtered_matches.sort(key=lambda x: x.start)
            per_line_matches.append(filtered_matches)
        return per_line_matches

    def process(self, data, matches: Sequence[Match]):
        if not matches:
            return data

        patched = []
        # Process chunk before first match
        first_match_start = matches[0].start
        if first_match_start != 0:
            patched.append(data[:first_match_start])

        last_match_id = len(matches) - 1

        for i, match in enumerate(matches):
            # Process current match
            patched.append(match.process())
            # Process chunk after current match
            if i < last_match_id:
                next_match = matches[i + 1]
                patched.append(data[match.end:next_match.start])
            else:
                patched.append(data[match.end:])

        if isinstance(data, str):
            join_char = ''
        else:
            join_char = b''
        patched = join_char.join(patched)
        return patched

    @abc.abstractmethod
    def feed(self, data, chunk_size=1000):
        raise NotImplementedError()


class TextProcessor(BaseProcessor):
    """Text processor class."""
    def feed(self, data, chunk_size=1000) -> Iterator[bytes]:
        data = iter(data)
        while True:
            chunk = list(itertools.islice(data, chunk_size))
            if not chunk:
                break
            chunk_matches = self.analyze(chunk)
            for line, matches in zip(chunk, chunk_matches):
                line = self.process(line, matches)
                yield line
