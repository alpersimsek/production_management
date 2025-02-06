import abc
import itertools
from gdpr.matchers import BaseMatcher, RegexpMatcher, IPAddrMatcher, MacAddrMatcher, Match
from gdpr.patchers import ReplacePatcher
from database.models import ContentType
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
    def feed(self, data, chunk_size=1000):
        data = iter(data)
        while True:
            chunk = list(itertools.islice(data, chunk_size))
            if not chunk:
                break
            chunk_matches = self.analyze(chunk)
            for line, matches in zip(chunk, chunk_matches):
                line = self.process(line, matches)
                yield line


class ProcessingConfig:
    """Processign config class.

    Args:
        rules_config: List configurations (dicts) for each rule to be created.
        replacer_state: Common state for replacers.
    """

    MATCHER_MAP = {
        "regex": RegexpMatcher,
        "ip_addr": IPAddrMatcher,
        "mac_addr": MacAddrMatcher
    }

    PATCHERS_MAP = {
        'replacer': ReplacePatcher,
    }

    # Content type -> processor class maping
    PROC_CLS_MAP = {
        ContentType.TEXT.value: TextProcessor,
    }

    def __init__(self,
                 rules_config: Sequence[Mapping],
                 replacer_state: Optional[Mapping[str, str]] = None):
        self.rules_config = rules_config
        self._replacer_state = replacer_state or {}
        self._processor = None

    def make_patcher(self, cfg: Mapping[str, Any]):
        """Make a patcher instance from config."""
        patcher_type = cfg.pop('type')
        patcher_cls = self.PATCHERS_MAP[patcher_type]
        patcher = patcher_cls(**cfg)
        if isinstance(patcher, ReplacePatcher):
            # Set a shared state instance to replacer
            patcher.set_state(self._replacer_state)
        return patcher

    def make_rule(self, cfg: Mapping[str, Any]):
        """Create a rule instance with ``cfg``."""
        rule_type = cfg.pop('type')
        patcher_cfg = cfg.pop('patcher_cfg', None)
        rule_cls = self.MATCHER_MAP[rule_type]
        if patcher_cfg:
            patcher = self.make_patcher(patcher_cfg)
            cfg['patcher'] = patcher
        rule = rule_cls(**cfg)
        return rule

    def make_processor(
        self,
        content_type=ContentType.DEFAULT.value
    ) -> BaseProcessor:
        """Create a ``BaseProcessor`` instance."""
        if self._processor is None:
            rules = [self.make_rule(cfg) for cfg in self.rules_config]
            proc_cls = self.PROC_CLS_MAP[content_type]
            processor = proc_cls(rules)
            self._processor = processor
        return self._processor
