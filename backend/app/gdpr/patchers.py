import string
import random
import ipaddress
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
    def __init__(self, **kwargs):
        self._ip_ranges = [ipaddress.IPv4Network("10.0.0.0/8"), ipaddress.IPv4Network("192.168.0.0/16")]        

    def _fetch_mask(self, original: str) -> str | None:
        """Check if the original string has an existing masked value."""
        entry = self.session.query(MaskingMap).filter_by(original=original).first()
        return entry.masked if entry else None

    def _store_mask(self, original: str, masked: str):
        """Store a new masked value in the database."""
        new_entry = MaskingMap(original=original, masked=masked)
        self.session.add(new_entry)
        self.session.commit()

    def _generate_masked_value(self, original: str, type: str) -> str:
        """Generate a new masked value based on entity type."""
        count = self.gdpr_repo.get_mapping_count(type) + 1

        if type == "IPV4_ADDRESS":
            network = random.choice(self._ip_ranges)
            return str(ipaddress.IPv4Address(network.network_address + count))

        if type == "MAC_ADDRESS":
            return f"00:00:00:00:{count//256:02x}:{count%256:02x}"

        if type == "USERNAME":
            return f"user{count}"

        if type == "DOMAIN":
            return f"domain{count}.masked"

        if type == "PHONE":
            return f"+0{count:010d}"

        # Default fallback: Generate a random alphanumeric string of same length
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choices(chars, k=len(original)))

    def _patch(self, match: str) -> str:
        """Replace a matched string."""

        replacement = self._fetch_mask(match)

        if replacement is None:
            # Generate a new masked value based on entity type
            replacement = self._generate_masked_value(match, type)
            # Store it in the database for future consistency
            self._store_mask(match, replacement)

        return replacement