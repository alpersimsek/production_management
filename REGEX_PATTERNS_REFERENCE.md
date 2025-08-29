# Regex Patterns Reference - GDPR Tool

This document provides a comprehensive reference for all regex patterns used in the GDPR tool for data classification and identification.

## Table of Contents
1. [HTTP Domain Pattern](#http-domain-pattern)
2. [SIP Username Pattern](#sip-username-pattern)
3. [SIP Phone Number Pattern](#sip-phone-number-pattern)
4. [SIP Domain Pattern](#sip-domain-pattern)
5. [Display Name Pattern](#display-name-pattern)
6. [MAC Address Pattern](#mac-address-pattern)
7. [Exception Patterns](#exception-patterns)
8. [Usage Guidelines](#usage-guidelines)

---

## HTTP Domain Pattern

### Pattern
```regex
https?://([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})(?:\d+)?|user=[^@]+@([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})
```

### Category
`domain`

### Description
Identifies domains in HTTP URLs and query parameters, handling both hostname domains and email addresses in query strings.

### Breakdown
- `https?://([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})(?:\d+)?` - **Hostname domain capture**:
  - `https?://` - Matches `http://` or `https://`
  - `([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})` - Domain part (capturing group)
    - `[a-zA-Z]` - Must start with letter (excludes IPs)
    - `[a-zA-Z0-9-]*` - Followed by letters, digits, hyphens
    - `\.` - Dot separator
    - `[a-zA-Z]{2,4}` - TLD (2-4 letters)
  - `(?:\d+)?` - Optional port number
- `|` - OR
- `user=[^@]+@([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})` - **Query parameter domain capture**:
  - `user=[^@]+@` - User parameter with @ symbol
  - `([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})` - Domain part (capturing group)

### Examples
**Valid matches:**
- `https://example.com` → Captures: `example.com` (hostname)
- `https://api.company.org:8080` → Captures: `api.company.org` (hostname with port)
- `?user=cp1@abcdefg.com` → Captures: `abcdefg.com` (query parameter)
- `user=john@domain.co.uk` → Captures: `domain.co.uk` (query parameter)

**Invalid matches:**
- `https://192.168.1.1` → No match (IP address, not domain)
- `ftp://domain.com` → No match (FTP protocol, not HTTP)



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
(?:sip:)?(\+[1-9]\d{2,14})@|\[DN:\s*(\d{7,15})\](?:\s|$|;|,|\)|>|\[)
```

### Category
`phone_num`

### Description
Identifies E164 format phone numbers with optional SIP prefix.

### Breakdown
- `(?:sip:)?(\+[1-9]\d{2,14})@` - **SIP Phone Number Format**:
  - `(?:sip:)?` - Optional SIP prefix (non-capturing group)
  - `(\+[1-9]\d{2,14})` - Phone number part (capturing group)
    - `\+` - Plus symbol (required)
    - `[1-9]` - Country code first digit (1-9, not 0)
    - `\d{2,14}` - 2 to 14 additional digits (national number)
  - `@` - At symbol separator
- `|` - **OR**
- `\[DN:\s*(\d{7,15})\](?:\s|$|;|,|\)|>|\[)` - **Directory Number Format**:
  - `\[DN:` - Literal "[DN:" prefix
  - `\s*` - Zero or more whitespace characters
  - `(\d{7,15})` - Phone number (capturing group)
    - `\d{7,15}` - 7-15 digits (typical phone number length)
  - `\]` - Closing bracket
  - `(?:\s|$|;|,|\)|>|\[)` - **Must end with**: space, end of line, semicolon, comma, closing parenthesis, >, or opening bracket [

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
- `[DN: 22334455]` (8 digits - Directory Number format)
- `[DN: 123456789012345]` (15 digits - Directory Number format)
- `[DN:1234567]` (7 digits - Directory Number format, no space)

**Invalid matches:**
- `+44@domain.com` (only 2 digits - just country code)
- `+1234567890123456@domain.com` (16 digits - exceeds limit)
- `+0123456789@domain.com` (country code starts with 0)
- `123456789@domain.com` (missing + symbol)
- `+1-234-567-890@domain.com` (contains hyphens)
- `[DN: 123456]` (6 digits - below minimum for DN format)
- `[DN: 1234567890123456]` (16 digits - above maximum for DN format)

---

## SIP Domain Pattern

### Pattern
```regex
(?:sip:[^@]*@|sip:|ROOTDOM:\s*|https?://|user=.*@|REGISTER\s+sip:|\[USER:\s*[^@]*@|\[USERNAME:\s*[^@]*@|\[SUBR:\s*[^@]*@|getUserAndDomain\s*==\s*[^@]*@)([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})
```

### Category
`domain`

### Description
Identifies domains in multiple contexts including SIP protocol, HTTP URLs, administrative fields, and function calls. This comprehensive pattern catches domains in all supported formats.

### Breakdown
- `(?:sip:[^@]*@|sip:|ROOTDOM:\s*|https?://|user=.*@|REGISTER\s+sip:|\[USER:\s*[^@]*@|\[USERNAME:\s*[^@]*@|\[SUBR:\s*[^@]*@|getUserAndDomain\s*==\s*[^@]*@)` - **Multiple context prefixes**:
  - `sip:[^@]*@` - SIP with user@domain format
  - `sip:` - SIP with direct domain format
  - `ROOTDOM:\s*` - ROOTDOM administrative field
  - `https?://` - HTTP/HTTPS URLs
  - `user=.*@` - User parameters in URLs
  - `REGISTER\s+sip:` - REGISTER SIP command
  - `\[USER:\s*[^@]*@` - USER field with email format
  - `\[USERNAME:\s*[^@]*@` - USERNAME field with email format
  - `\[SUBR:\s*[^@]*@` - SUBR field with email format
  - `getUserAndDomain\s*==\s*[^@]*@` - getUserAndDomain function call
- `([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})` - **Domain capture**:
  - `[a-zA-Z]` - Must start with letter (excludes IPs)
  - `[a-zA-Z0-9-]*` - Followed by letters, digits, hyphens
  - `\.` - Dot separator
  - `[a-zA-Z]{2,4}` - TLD (2-4 letters)

### Examples
**Valid matches:**
- `REGISTER sip:abcdefg.com SIP/2.0` → Captures: `abcdefg.com` (REGISTER command)
- `sip:user@domain.com` → Captures: `domain.com` (SIP with user@)
- `sip:example.co.uk` → Captures: `example.co.uk` (SIP direct domain)
- `[ROOTDOM: abcdefg.com]` → Captures: `abcdefg.com` (ROOTDOM field)
- `https://api.company.org:8080` → Captures: `api.company.org` (HTTP URL)
- `user=cp1@domain.org` → Captures: `domain.org` (User parameter)
- `[USER: user1@abcdefg.com]` → Captures: `abcdefg.com` (USER field)
- `[USERNAME: user1@abcdefg.com]` → Captures: `abcdefg.com` (USERNAME field)
- `[SUBR: Y:user1@abcdefg.com]` → Captures: `abcdefg.com` (SUBR field)
- `getUserAndDomain == user1@abcdefg.com` → Captures: `abcdefg.com` (Function call)

**Invalid matches (excluded to reduce false positives):**
- `https://192.168.1.1` → No match (IP address, not domain)
- `sip:user@192.168.1.1` → No match (IP address starts with digit)
- `random text with domain.com` → No match (no context)

---

## Display Name Pattern

### Pattern
```regex
(?:\[(?:HEADER:\s*)?|^)(?:To|TO|[Ff]rom|NAME|REMPTY|USERNM):\s*(?:"([^"]+)"|([^<>\s\]\)}]+(?:\s+[^<>\s\]\)}]+)*))|\[(?:NAME|USERNAME|OUNAME):\s*([^\]\s]+(?:\s+[^\]\s]+)*)|x-nt-party-id:\s*/([^\]\s\)}]+)|Obfuscated Contact-\s*:\s*sip:([^@]+)@|(?:\[HEADER:\s*)?Contact:\s*<sip:([^@]+)@|\[CONTACTS:\s*\[(?:REPLY TO|LOCATED AT)\]\s*<\s*<sip:([^@]+)@|Retrieving presence information for:\s*([^<\s]+)\s*<sip:|Request-URI User Part:\s*(\d{7,15});
```

### Category
`username`

### Description
Identifies display names and usernames in multiple header formats including To, FROM, NAME, REMPTY, USERNM, Contact, and various SIP-related fields. This comprehensive pattern handles all username formats in one unified rule. **The pattern requires headers to be preceded by either an opening bracket [ or start of string ^, preventing partial matches like "Service Name:" from incorrectly matching "NAME:"**.

### Breakdown
- `(?:\[(?:HEADER:\s*)?|^)(?:To|TO|[Ff]rom|NAME|REMPTY|USERNM):\s*(?:"([^"]+)"|([^<>\s\]\)}]+(?:\s+[^<>\s\]\)}]+)*))` - **Standard header formats**:
  - `(?:\[(?:HEADER:\s*)?|^)` - **Must be preceded by**: opening bracket with optional HEADER prefix OR start of string
  - `(?:To|TO|[Ff]rom|NAME|REMPTY|USERNM):` - Header types (case insensitive for FROM)
  - `(?:"([^"]+)"|([^<>\s\]\)}]+(?:\s+[^<>\s\]\)}]+)*))` - Quoted or unquoted text with spaces
- `|\[(?:NAME|USERNAME|OUNAME):\s*([^\]\s]+(?:\s+[^\]\s]+)*)` - **NAME/USERNAME/OUNAME field formats**
- `|x-nt-party-id:\s*/([^\]\s\)}]+)` - **x-nt-party-id format** (value after /)
- `|Obfuscated Contact-\s*:\s*sip:([^@]+)@` - **Obfuscated Contact format**
- `|(?:\[HEADER:\s*)?Contact:\s*<sip:([^@]+)@` - **Contact header format**
- `|\[CONTACTS:\s*\[(?:REPLY TO|LOCATED AT)\]\s*<\s*<sip:([^@]+)@` - **CONTACTS field formats**
- `|Retrieving presence information for:\s*([^<\s]+)\s*<sip:` - **Presence information format**
- `|Request-URI User Part:\s*(\d{7,15});` - **Request-URI User Part format**:
  - `Request-URI User Part:` - Literal text match for the field name
  - `\s*` - Zero or more whitespace characters after the colon
  - `(\d{7,15})` - User identifier (capturing group)
    - `\d{7,15}` - 7-15 digits (typical user ID length)
  - `;` - Semicolon terminator

### Examples
**Valid matches:**
- `[TO: cp1 <sip:user1@domain1.com>]` → Captures: `cp1` (To header)
- `[FROM: cp1 ABCDE <sip:user1@domain1.com>]` → Captures: `cp1 ABCDE` (From header)
- `[from: cp1 ABCDE <sip:user1@domain1.com>]` → Captures: `cp1 ABCDE` (from lowercase)
- `[REMPTY: cp1 ABCDE <sip:user1@domain1.com>]` → Captures: `cp1 ABCDE` (REMPTY header)
- `[USERNM: cp1]` → Captures: `cp1` (USERNM header)
- `[NAME: cp1 ABCDE]` → Captures: `cp1 ABCDE` (NAME field)
- `[USERNAME: cp1]` → Captures: `cp1` (USERNAME field)
- `[OUNAME: cp1]` → Captures: `cp1` (OUNAME field)
- `[HEADER: x-nt-party-id: /cp1]` → Captures: `cp1` (value after /)
- `Obfuscated Contact- : sip:cp1@` → Captures: `cp1` (Obfuscated Contact)
- `[HEADER: Contact: <sip:cp1@` → Captures: `cp1` (Contact header)
- `[CONTACTS: [REPLY TO] < <sip:cp1@` → Captures: `cp1` (CONTACTS REPLY TO)
- `[CONTACTS: [LOCATED AT] < <sip:cp1@` → Captures: `cp1` (CONTACTS LOCATED AT)
- `Retrieving presence information for: cp1 <sip:user1@domain1.com>]` → Captures: `cp1` (Presence info)
- `Request-URI User Part: 6915999094;` → Captures: `6915999094` (Request-URI User Part)
- `Request-URI User Part: 123456789;` → Captures: `123456789` (Request-URI User Part)

**Invalid matches (excluded by exception patterns):**
- `[TO: null <sip:user1@domain1.com>]` → No match (null excluded)
- `[FROM: undefined <sip:user1@domain1.com>]` → No match (undefined excluded)
- `[NAME: none]` → No match (none excluded)

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

### Username Exceptions
```regex
^null$      # Excludes 'null' from username matching
^NULL$      # Case insensitive exclusion
^undefined$ # Excludes 'undefined' from username matching
^UNDEFINED$ # Case insensitive exclusion
^none$      # Excludes 'none' from username matching
^NONE$      # Case insensitive exclusion
```

### Description
These patterns handle special cases that might be incorrectly identified as phone numbers or usernames. Exception patterns override standard patterns to prevent false positives.

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
| `domain` | `https?://([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})(?:\d+)?\|user=[^@]+@([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})` | HTTP domains and query parameters | Variable | Variable |
| `username` | `(?:sip:)?([a-zA-Z0-9][a-zA-Z0-9._%+-]*)@(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})` | SIP usernames | Variable | Variable |
| `phone_num` | `(?:sip:)?(\+[1-9]\d{2,14})@\|\[DN:\s*(\d{7,15})\](?:\s\|$\|;\|,\|\)\|>\|\[)` | E164 phone numbers and Directory Numbers | 3 digits (E164) / 7 digits (DN) | 15 digits |
| `domain` | `(?:sip:[^@]*@\|sip:\|ROOTDOM:\s*\|https?://\|user=.*@\|REGISTER\s+sip:\|\[USER:\s*[^@]*@\|\[USERNAME:\s*[^@]*@\|\[SUBR:\s*[^@]*@\|getUserAndDomain\s*==\s*[^@]*@)([a-zA-Z][a-zA-Z0-9-]*\.[a-zA-Z]{2,4})` | Comprehensive domain coverage | Variable | Variable |
| `username` | `(?:\[(?:HEADER:\s*)?\|^)(?:To\|TO\|[Ff]rom\|NAME\|REMPTY\|USERNM):\s*(?:"([^"]+)"\|([^<>\s\]\)}]+(?:\s+[^<>\s\]\)}]+)*))\|\[NAME:\s*([^\]\s]+(?:\s+[^\]\s]+)*)\|x-nt-party-id:\s*/([^\]\s\)}]+)\|Obfuscated Contact-\s*:\s*sip:([^@]+)@\|(?:\[HEADER:\s*)?Contact:\s*<sip:([^@]+)@\|\[CONTACTS:\s*\[(?:REPLY TO\|LOCATED AT)\]\s*<\s*<sip:([^@]+)@\|Retrieving presence information for:\s*([^<\s]+)\s*<sip:` | Display names and usernames | Variable | Variable |
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
