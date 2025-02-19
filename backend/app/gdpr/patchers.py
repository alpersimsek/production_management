import string
import random
import ipaddress
from database.models import RuleCategory
# from services import MaskingMapService
from typing import Optional, Iterable, Mapping

class BasePatcher:
    """Base patcher class."""

    def _patch(self, match):
        """Actual patch method. Override in subclasses."""
        raise NotImplementedError

    def __call__(self, match):
        if not match:
            return match
        else:
            return self._patch(match)


class ReplacePatcher(BasePatcher):
    """Replace match with another with preserving consistency."""
    def __init__(self, maskingMapService, **kwargs):
        self._ip_ranges = [ipaddress.IPv4Network("10.0.0.0/8"), ipaddress.IPv4Network("192.168.0.0/16")]
        self.maskingMapService = maskingMapService
        self.category = kwargs.get("category")

    def _generate_masked_value(self, original: str) -> str:
        """Generate a new masked value based on entity type."""
        count = self.maskingMapService.count_entries(self.category) + 1

        if self.category == RuleCategory.IPV4_ADDR:
            network = random.choice(self._ip_ranges)
            return str(ipaddress.IPv4Address(network.network_address + count))

        if self.category == RuleCategory.MAC_ADDR:
            return f"00:00:00:00:{count//256:02x}:{count%256:02x}"

        if self.category == RuleCategory.USERNAME:
            return f"user{count}"

        if self.category == RuleCategory.DOMAIN:
            return f"domain{count}.masked"

        if self.category == RuleCategory.PHONE_NUM:
            return f"+0{count:010d}"

        # Default fallback: Generate a random alphanumeric string of same length
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choices(chars, k=len(original)))

    def _patch(self, match: str) -> str:
        """Replace a matched string."""

        replacement = self.maskingMapService.fetch_mask(match)

        if replacement is None:
            # Generate a new masked value based on entity type
            replacement = self._generate_masked_value(match)
            # Store it in the database for future consistency
            self.maskingMapService.store_mask(match, replacement, self.category)

        return replacement