"""
GDPR Tool Patchers - Data Masking and Replacement

This module provides data patching and masking capabilities for GDPR compliance.
It implements various patcher types for replacing sensitive data with consistent
masked values while preserving data structure and relationships.

Key Components:
- BasePatcher: Abstract base class for all patcher implementations
- ReplacePatcher: Main patcher for consistent data replacement and masking

Patcher Features:
- Consistent Masking: Same original values always get the same masked values
- Category-Specific Generation: Different masking strategies for different data types
- Database Storage: Masked values are stored for consistency across processing
- IP Address Handling: Special handling for IP addresses with private network ranges
- MAC Address Handling: Consistent MAC address masking with proper formatting
- Username Generation: Systematic username generation with counters
- Domain Generation: Consistent domain name masking
- Phone Number Handling: Phone number masking with proper formatting

ReplacePatcher Features:
- Masking Map Integration: Uses MaskingMapService for consistent value storage
- Category-Based Generation: Different generation strategies per data category
- IP Range Selection: Uses private IP ranges for IP address masking
- Counter-Based Generation: Sequential generation for consistent numbering
- Fallback Generation: Random alphanumeric generation for unknown types
- Database Persistence: Stores masked values for future consistency

Supported Data Categories:
- IPV4_ADDR: IPv4 addresses with private network masking
- MAC_ADDR: MAC addresses with consistent formatting
- USERNAME: Usernames with systematic generation
- DOMAIN: Domain names with consistent structure
- PHONE_NUM: Phone numbers with proper formatting
- Generic: Random alphanumeric strings for unknown types

The patchers ensure that sensitive data is consistently masked while maintaining
data structure and relationships for GDPR compliance workflows.
"""

import string
import random
import ipaddress
from database.models import RuleCategory
# from services import MaskingMapService
from typing import Optional, Iterable, Mapping
from logger import logger

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
            masked_value = str(ipaddress.IPv4Address(network.network_address + count))
            logger.debug({
                "event": "ip_generation",
                "original": original,
                "network": str(network),
                "count": count,
                "generated": masked_value
            })
            return masked_value

        if self.category == RuleCategory.MAC_ADDR:
            masked_value = f"00:00:00:00:{count//256:02x}:{count%256:02x}"
            logger.debug({
                "event": "mac_generation",
                "original": original,
                "count": count,
                "generated": masked_value
            })
            return masked_value

        if self.category == RuleCategory.USERNAME:
            masked_value = f"user{count}"
            logger.debug({
                "event": "username_generation",
                "original": original,
                "count": count,
                "generated": masked_value
            })
            return masked_value

        if self.category == RuleCategory.DOMAIN:
            masked_value = f"domain{count}.com"
            logger.debug({
                "event": "domain_generation",
                "original": original,
                "count": count,
                "generated": masked_value
            })
            return masked_value

        if self.category == RuleCategory.PHONE_NUM:
            masked_value = f"+0{count:010d}"
            logger.debug({
                "event": "phone_generation",
                "original": original,
                "count": count,
                "generated": masked_value
            })
            return masked_value

        # Default fallback: Generate a random alphanumeric string of same length
        chars = string.ascii_lowercase + string.digits
        masked_value = ''.join(random.choices(chars, k=len(original)))
        logger.debug({
            "event": "fallback_generation",
            "original": original,
            "length": len(original),
            "generated": masked_value
        })
        return masked_value

    def _patch(self, match: str) -> str:
        """Replace a matched string."""

        replacement = self.maskingMapService.fetch_mask(match)

        if replacement is None:
            # Generate a new masked value based on entity type
            replacement = self._generate_masked_value(match)
            # Store it in the database for future consistency
            self.maskingMapService.store_mask(match, replacement, self.category)
            
            logger.info({
                "event": "data_masked_new",
                "category": self.category.value if self.category else "unknown",
                "original": match,
                "masked": replacement,
                "action": "Generated new masked value"
            })
        else:
            logger.info({
                "event": "data_masked_existing",
                "category": self.category.value if self.category else "unknown",
                "original": match,
                "masked": replacement,
                "action": "Used existing masked value"
            })

        return replacement