import abc
import itertools


class BaseProcessor(abc.ABC):
    """Base processor class."""
    def __init__(self, rules):
        self.rules = rules

    def analyze(self, data):
       pass

    def process(self, data):
        pass

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
            # TODO
            # analyze and process/patch line