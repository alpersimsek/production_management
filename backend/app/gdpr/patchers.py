

class BasePatcher:
    """Base patcher class."""

    def _patch(self, word):
        """Actual patch method. Override in subclasses."""
        raise NotImplementedError

    def __call__(self, word):
        if not word:
            return word
        else:
            return self._patch(word)


class ReplacePatcher(BasePatcher):
    """Replace word with another with preserving consistency."""
    def __init__(self):
        pass

    def _patch(self, word):
        """Replace a word."""
        pass