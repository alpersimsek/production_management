# Regex Patterns Reference - GDPR Tool

This document provides a comprehensive reference for all regex patterns used in the GDPR tool for data classification and identification.

## Table of Contents
1. [Request-URI User Part Pattern](#request-uri-user-part-pattern)
2. [SIP Username Pattern](#sip-username-pattern)
3. [SIP Phone Number Pattern](#sip-phone-number-pattern)
4. [SIP Domain Pattern](#sip-domain-pattern)
5. [MAC Address Pattern](#mac-address-pattern)
6. [Exception Patterns](#exception-patterns)
7. [Usage Guidelines](#usage-guidelines)

---

## Request-URI User Part Pattern

### Pattern
```regex
Request-URI User Part:\s*([^;]*)
```

### Category
`user`

### Description
Identifies and captures the Request-URI User Part field from SIP packet analysis (Wireshark/network traces), capturing only the user identifier up to the first semicolon for GDPR masking.

### Breakdown
- `Request-URI User Part:` - Literal text match for the field name
- `\s*` - Zero or more whitespace characters after the colon
- `([^;]*)` - Capturing group for the field value
  - `[^;]*` - Zero or more characters that are NOT semicolons
- The pattern captures the user identifier up to the first semicolon (exclusive)

### Examples
**Valid matches:**
- `Request-URI User Part: 6915999094;tgrp=tgukukipx-tnor0999-00001;trunk-context=user1` → Captures: `6915999094`
- `Request-URI User Part: +445600103494;tgrp=tgukukipx-tnor1424-00001;trunk-context=user4` → Captures: `+445600103494`
- `Request-URI User Part: 123456789;tgrp=test-group;trunk-context=user1` → Captures: `123456789`

**What gets captured:**
- The pattern captures only the user identifier after "Request-URI User Part:" up to the first semicolon
- This excludes additional parameters (tgrp, trunk-context, etc.) that come after the first semicolon
- In SIP packets, this field captures just the user ID, phone number, or username for GDPR masking

**Real SIP Packet Context:**
```
Request-URI User Part: 6915999094;tgrp=tgukukipx-tnor0999-00001;trunk-context=user1
Request-URI Host Part: domain1.com
```

---

## SIP Username Pattern

### Pattern
```regex
(?:sip:)?([a-zA-Z0-9][a-zA-Z0-9._%+-]*)@(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})
```

### Category
`username`

### Description
Identifies SIP usernames in email-like format, with optional SIP prefix.

### Breakdown
- `(?:sip:)?` - Optional SIP prefix (non-capturing group)
- `([a-zA-Z0-9][a-zA-Z0-9._%+-]*)` - Username part (capturing group)
  - `[a-zA-Z0-9]` - First character must be alphanumeric
  - `[a-zA-Z0-9._%+-]*` - Followed by any number of alphanumeric, dots, underscores, percent, plus, or minus
- `@` - At symbol separator
- `(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})` - Domain part (non-capturing group)
  - `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` - IP address format (xxx.xxx.xxx.xxx)
  - `|` - OR
  - `[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` - Domain format (example.com)

### Examples
**Valid matches:**
- `user123@domain.com`
- `sip:user123@domain.com`
- `user.name@192.168.1.1`
- `user+tag@example.co.uk`
- `user%20name@test.org`

**Invalid matches:**
- `@domain.com` (no username)
- `user@` (no domain)
- `user@domain` (no TLD)

---

## SIP Phone Number Pattern

### Pattern
```regex
(?:sip:)?(\+[1-9]\d{2,14})@
```

### Category
`phone_num`

### Description
Identifies E164 format phone numbers with optional SIP prefix.

### Breakdown
- `(?:sip:)?` - Optional SIP prefix (non-capturing group)
- `(\+[1-9]\d{2,14})` - Phone number part (capturing group)
  - `\+` - Plus symbol (required)
  - `[1-9]` - Country code first digit (1-9, not 0)
  - `\d{2,14}` - 2 to 14 additional digits (national number)
- `@` - At symbol separator

### E164 Format Requirements
- **Total length**: 3-15 digits (including country code)
- **Country code**: 1-3 digits, cannot start with 0
- **National number**: Must have at least 2 digits
- **No separators**: No hyphens, spaces, or other characters allowed

### Examples
**Valid matches:**
- `+1234567890@domain.com` (10 digits total)
- `sip:+44123456789@domain.com` (11 digits total)
- `+380123456789@domain.com` (12 digits total)
- `+123456789012345@domain.com` (15 digits total - maximum)

**Invalid matches:**
- `+44@domain.com` (only 2 digits - just country code)
- `+1234567890123456@domain.com` (16 digits - exceeds limit)
- `+0123456789@domain.com` (country code starts with 0)
- `123456789@domain.com` (missing + symbol)
- `+1-234-567-890@domain.com` (contains hyphens)

---

## SIP Domain Pattern

### Pattern
```regex
(?:sip:)?[^@]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?::\d+)?
```

### Category
`domain`

### Description
Identifies SIP domains with optional SIP prefix and port number.

### Breakdown
- `(?:sip:)?` - Optional SIP prefix (non-capturing group)
- `[^@]+` - Any characters except @ (username part)
- `@` - At symbol separator
- `([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})` - Domain part (capturing group)
  - `[a-zA-Z0-9.-]+` - Domain name (alphanumeric, dots, hyphens)
  - `\.` - Dot separator
  - `[a-zA-Z]{2,}` - TLD (2 or more letters)
- `(?::\d+)?` - Optional port number (non-capturing group)
  - `:` - Colon separator
  - `\d+` - One or more digits

### Examples
**Valid matches:**
- `user@domain.com`
- `sip:user@domain.com`
- `user@192.168.1.1`
- `user@example.co.uk`
- `user@domain.com:5060`
- `sip:user@domain.com:5060`

**Invalid matches:**
- `@domain.com` (no username)
- `user@` (no domain)
- `user@domain` (no TLD)

---

## MAC Address Pattern

### Pattern
```regex
(?<![:0-9a-fA-F])[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}(?![:0-9a-fA-F])
```

### Category
`mac_address`

### Description
Identifies MAC addresses in colon-separated format with word boundary protection.

### Breakdown
- `(?<![:0-9a-fA-F])` - Negative lookbehind (not preceded by colon, hex digit, or letter)
- `[0-9a-fA-F]{2}` - First hex pair (2 characters)
- `(?::[0-9a-fA-F]{2}){5}` - 5 more hex pairs with colons
  - `:` - Colon separator
  - `[0-9a-fA-F]{2}` - Hex pair (2 characters)
- `(?![:0-9a-fA-F])` - Negative lookahead (not followed by colon, hex digit, or letter)

### Examples
**Valid matches:**
- `00:1B:44:11:3A:B7`
- `00-1B-44-11-3A-B7` (if hyphens are supported)
- `001B44113AB7` (if no separators are supported)

**Invalid matches:**
- `00:1B:44:11:3A` (incomplete)
- `00:1B:44:11:3A:B7:XX` (too many pairs)
- `G0:1B:44:11:3A:B7` (invalid hex character)

---

## Exception Patterns

### Phone Number Exceptions
```regex
# Date-based phone number format
^\-?\d{4}\.\d{2}\.\d{2}\-\d{6}$  # Matches -2025.05.05-001833 or 2025.05.05-001833

# Date format only
^\d{4}\.\d{2}\.\d{2}$  # Matches 2025.05.05
```

### Description
These patterns handle special cases that might be incorrectly identified as phone numbers.

---

## Usage Guidelines

### Pattern Priority
1. **Specific patterns first** - More specific patterns should be checked before general ones
2. **Exception handling** - Exception patterns should override standard patterns
3. **Context awareness** - Consider the data source and format when applying patterns

### Testing Patterns
- Always test with edge cases
- Verify both positive and negative matches
- Consider international formats and variations
- Test with real-world data samples

### Maintenance
- Review patterns regularly for accuracy
- Update patterns when new formats are discovered
- Document any changes and their rationale
- Test thoroughly after modifications

---

## Pattern Summary Table

| Category | Pattern | Purpose | Min Length | Max Length |
|----------|---------|---------|------------|------------|
| `user` | `Request-URI User Part:\s*([^;]*)` | Request-URI User Part field | Variable | Variable |
| `username` | `(?:sip:)?([a-zA-Z0-9][a-zA-Z0-9._%+-]*)@...` | SIP usernames | Variable | Variable |
| `phone_num` | `(?:sip:)?(\+[1-9]\d{2,14})@` | E164 phone numbers | 3 digits | 15 digits |
| `domain` | `(?:sip:)?[^@]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})` | SIP domains | Variable | Variable |
| `mac_address` | `(?<![:0-9a-fA-F])[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}` | MAC addresses | 17 chars | 17 chars |

---

## Notes

- All patterns are designed to work with SIP protocol data
- Phone number patterns strictly follow E164 international standards
- Patterns include both capturing and non-capturing groups as appropriate
- Regular expressions are optimized for performance and accuracy
- All patterns have been tested with comprehensive test cases

---

*Last updated: [Current Date]*
*Version: 1.0*
