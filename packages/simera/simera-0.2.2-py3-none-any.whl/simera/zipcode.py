import re
import pandas as pd
from simera.utils import DataInputError
from functools import lru_cache
from typing import Callable, List, Set


class MixedRadixZipKey:
    """
    Callable class to map a zipcode string into a unique integer key
    using a mixed-radix system based on allowed characters per position.
    Added for multiprocessing. Previously funcKey was not pickleable.
    """
    def __init__(self, sorted_lists: List[List[str]], multipliers: List[int]):
        self.sorted_lists = sorted_lists
        self.multipliers = multipliers

    def __call__(self, zipcode: str) -> int:
        if len(zipcode) != len(self.sorted_lists):
            raise ValueError(f"Zip length mismatch: expected {len(self.sorted_lists)} chars")
        total = 0
        for i, ch in enumerate(zipcode):
            idx = self.sorted_lists[i].index(ch)
            total += idx * self.multipliers[i]
        return total


class ZipcodeManager:
    _ZIPCODE_PATTERNS = {
        'pattern_3_digits': {
            'country': ['IS'],
            'regex_official': r'^\d{3}$',
            'regex_clean': r'^\d{3}$',
        },
        'pattern_4_digits': {
            'country': ['BE', 'LU', 'AL', 'AM', 'BG', 'GE', 'HU', 'LV', 'MD', 'MK', 'SI', 'AT', 'CH', 'LI', 'CY', 'DK', 'NO'],
            'regex_official': r'^\d{4}$',
            'regex_clean': r'^\d{4}$',
        },
        'pattern_5_digits': {
            'country': ['BA', 'EE', 'HR', 'IC', 'LT', 'ME', 'RS', 'UA', 'XK', 'DE', 'FR', 'MC', 'ES', 'IT', 'SM', 'VA', 'FI', 'TR'],
            'regex_official': r'^\d{5}$',
            'regex_clean': r'^\d{5}$',
        },
        'pattern_6_digits': {
            'country': ['BY', 'KG', 'KZ', 'RO', 'RU', 'UZ'],
            'regex_official': r'^\d{6}$',
            'regex_clean': r'^\d{6}$',
        },
        'pattern_7_digits': {
            'country': ['IL'],
            'regex_official': r'^\d{7}$',
            'regex_clean': r'^\d{7}$',
        },
        'pattern_5-3-2_digits': {
            'country': ['CZ', 'SK', 'GR', 'SE'],
            'regex_official': r'^\d{3} \d{2}$',
            'regex_clean': r'^\d{5}$',
        },
        'pattern_az': {
            'country': ['AZ'],
            'regex_official': r'^AZ \d{4}$',
            'regex_clean': r'^\d{4}$',
        },
        'pattern_nl': {
            'country': ['NL'],
            'regex_official': r'^\d{4} [A-Z]{2}$',
            'regex_clean': r'^\d{4}[A-Z]{2}$',
        },
        'pattern_pl': {
            'country': ['PL'],
            'regex_official': r'^\d{2}-\d{3}$',
            'regex_clean': r'^\d{5}$',
        },
        'pattern_ad': {
            'country': ['AD'],
            'regex_official': r'^AD\d{3}$',
            'regex_clean': r'^\d{3}$',
        },
        'pattern_pt': {
            'country': ['PT'],
            'regex_official': r'^\d{4}-\d{3}$',
            'regex_clean': r'^\d{7}$',
        },
        'pattern_mt': {
            'country': ['MT'],
            'regex_official': r'^[A-Z]{3} \d{4}$',
            'regex_clean': r'^[A-Z]{3}\d{4}$',
        },
        # Individual countries
        'pattern_uk': {
            'country': ['GB', 'IM', 'JE'],
            'regex_official': r'^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$',
            'regex_clean': r'^[A-Z][0-9A-Z]{6}$',
            # Actual: r'^(GIR ?0AA|[A-PR-UWYZ][0-9][0-9]? ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9][0-9]? ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][0-9][A-HJKSTUW]? ?[0-9][ABD-HJLNP-UW-Z]{2}|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV-Y]? ?[0-9][ABD-HJLNP-UW-Z]{2})$'
        },
        'pattern_ie': {
            'country': ['IE'],
            'regex_official': r'^[A-Z]\d{2}\s?[A-Z0-9]{4}$',
            'regex_clean': r'^[A-Z][0-9A-Z]{6}$',
            # Actual: r'^(?:D6W|[AC-FHKNPRTV-Y]\d{2})\s?[0-9AC-FHKNPRTV-Y]{4}$'
        },
        'pattern_ca': {
            'country': ['CA'],
            'regex_official': r'^[A-Z]\d[A-Z] \d[A-Z]\d$',
            'regex_clean': r'^[A-Z]\d[A-Z]\d[A-Z]\d$',
            # Actual: r'^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z] ?\d[ABCEGHJ-NPRSTV-Z]\d$'
        },
        'pattern_us': {
            'country': ['US'],
            'regex_official': r'^\d{5}(?:-\d{4})?$',
            'regex_clean': r'^\d{5}$',
        },
    }

    def __init__(self):
        self._REGEX_OFFICIAL_UNIQUE = self._set_regex_attributes(regex='regex_official')
        self._REGEX_CLEAN_UNIQUE = self._set_regex_attributes(regex='regex_clean')
        self.country = self._set_country_attributes()
        self.zipcode_clean_first = self._set_zipcode_clean_first_per_country()
        self.zipcode_clean_last = self._set_zipcode_clean_last_per_country()
        self._add_first_last_to_zipcode_patterns()

    def __repr__(self):
        return 'ZipcodeManager'

    def _set_country_attributes(self):
        countries = {}
        for pattern, pattern_details in self._ZIPCODE_PATTERNS.items():
            pattern_countries = pattern_details.get('country').copy()
            if pattern_countries:
                for country in pattern_countries:
                    pattern_details_without_country = {k: v for k, v in pattern_details.items() if k not in ['country']}
                    countries.update({country: pattern_details_without_country})
                    first, last = self._generate_first_last_zipcode(pattern_details.get('regex_clean'))
                    countries.get(country).update({'zipcode_clean_first': first, 'zipcode_clean_last': last})
                    first, last = self._generate_first_last_zipcode(pattern_details.get('regex_official'))
                    countries.get(country).update({'zipcode_official_first': first, 'zipcode_official_last': last})
        return countries

    def _set_zipcode_clean_first_per_country(self):
        return {ctry: v.get('zipcode_clean_first') for ctry, v in self.country.items()}

    def _set_zipcode_clean_last_per_country(self):
        return {ctry: v.get('zipcode_clean_last') for ctry, v in self.country.items()}

    def _add_first_last_to_zipcode_patterns(self):
        # Extend _ZIPCODE_PATTERNS with first and last clean zipcode
        for k, v in self._ZIPCODE_PATTERNS.items():
            first, last = self._generate_first_last_zipcode(v.get('regex_clean'))
            v.update({'zipcode_clean_first': first, 'zipcode_clean_last': last})

    def _set_regex_attributes(self, regex='regex_official'):
        return list(set([v[regex] for k, v in self._ZIPCODE_PATTERNS.items()]))

    def is_valid_zipcode(self, country_code: str, zipcode: str, regex: str) -> bool:
        """
        Validate a zipcode based on the country's regex pattern ('regex_official' or 'regex_clean').

        Args:
            country_code (str): The ISO country code (e.g., 'US', 'DE').
            zipcode (str): The postal code to validate.
            regex (str): The key for the regex pattern to use (e.g., 'regex_official', 'regex_clean').

        Returns:
            bool: True if the zipcode is valid for the given country and regex type, False otherwise.

        Raises:
            ValueError: If the given country code is not supported or the regex key is not found.

        Notes:
            The regex patterns should be defined in `self.country`, which is expected to be a dictionary
            mapping country codes to their associated regex patterns.
        """
        country_code = country_code.upper()

        if country_code not in self.country:
            raise ValueError(f"Country '{country_code}' is not supported.")

        country_patterns = self.country[country_code]

        if regex not in country_patterns:
            raise ValueError(f"Regex key '{regex}' not found for country '{country_code}'.")

        pattern = country_patterns[regex]
        return bool(re.match(pattern, str(zipcode)))

    @staticmethod
    def _generate_first_last_zipcode(pattern: str):
        """
        Parses a regex pattern for a fixed-length postal code (or similar string)
        and returns a tuple (first, last) representing the lexicographically
        smallest and largest valid strings.

        Supported constructs:
          - Character classes, e.g. [A-Z] or [0-9A-Z]
          - Escaped sequences: \\d (treated as [0-9]), \\s (converted to a space ' ')
          - Literal characters
          - Groups (capturing or non-capturing, e.g. (?:...))
          - Quantifiers: fixed {n}, variable {min,max} (max is used), and the optional operator (?).

        For optional groups (or tokens) such as (?:-\\d{4})? or \\s? the function assumes the "max variant"
        (i.e. that the token appears once).
        """
        # Remove leading ^ and trailing $ if present.
        if pattern.startswith("^"):
            pattern = pattern[1:]
        if pattern.endswith("$"):
            pattern = pattern[:-1]

        def parse_quantifier(i: int, token):
            """
            Given an index i and a token (which can be a tuple (min, max) or a list of such tuples),
            check if there's a quantifier following. Supported quantifiers:
              - Curly braces: {n} or {min,max} (using max value)
              - Optional operator: ?
            Returns a list of tokens (flattened) and the new index.
            """
            if i < len(pattern) and pattern[i] == '{':
                j = i + 1
                while j < len(pattern) and pattern[j] != '}':
                    j += 1
                if j >= len(pattern) or pattern[j] != '}':
                    raise ValueError("Invalid pattern: unterminated quantifier")
                quant_text = pattern[i+1:j].strip()
                if ',' in quant_text:
                    parts = quant_text.split(',')
                    max_quant = int(parts[-1].strip())
                else:
                    max_quant = int(quant_text)
                if isinstance(token, list):
                    result = []
                    for _ in range(max_quant):
                        result.extend(token)
                else:
                    result = [token] * max_quant
                return result, j + 1
            elif i < len(pattern) and pattern[i] == '?':
                # Optional token: assume presence (once)
                return (token if isinstance(token, list) else [token]), i + 1
            return (token if isinstance(token, list) else [token]), i

        def parse_sequence(i: int, end_char=None):
            """
            Parses tokens from the pattern starting at index i until an ending character is found,
            or until the end of the pattern if end_char is None.
            Returns a list of tokens (each token is a tuple (min_char, max_char)) and the new index.
            """
            tokens = []
            while i < len(pattern):
                # If we reached the expected end (like a closing parenthesis), break out.
                if end_char is not None and pattern[i] == end_char:
                    return tokens, i + 1

                ch = pattern[i]

                if ch == '(':
                    # Beginning of a group.
                    # Check for non-capturing group (e.g. (?:...))
                    if i + 2 < len(pattern) and pattern[i+1:i+3] == "?:":
                        inner_tokens, i = parse_sequence(i + 3, end_char=')')
                    else:
                        inner_tokens, i = parse_sequence(i + 1, end_char=')')
                    # Process any quantifier attached to the group.
                    group_tokens, i = parse_quantifier(i, inner_tokens)
                    tokens.extend(group_tokens)

                elif ch == '\\':
                    # Escaped sequence.
                    if i + 1 >= len(pattern):
                        raise ValueError("Invalid pattern: ends with backslash")
                    esc_char = pattern[i + 1]
                    if esc_char == 'd':
                        token = ('0', '9')
                    elif esc_char == 's':
                        token = (' ', ' ')
                    else:
                        token = (esc_char, esc_char)
                    i += 2
                    new_tokens, i = parse_quantifier(i, token)
                    tokens.extend(new_tokens)

                elif ch == '[':
                    # Process a character class.
                    j = pattern.find(']', i)
                    if j == -1:
                        raise ValueError("Invalid pattern: unterminated character class")
                    char_class = pattern[i+1:j]
                    allowed_chars = []
                    k = 0
                    while k < len(char_class):
                        # Handle ranges like A-Z.
                        if k + 2 < len(char_class) and char_class[k+1] == '-':
                            start, end = char_class[k], char_class[k+2]
                            allowed_chars.extend(chr(c) for c in range(ord(start), ord(end) + 1))
                            k += 3
                        else:
                            allowed_chars.append(char_class[k])
                            k += 1
                    allowed_chars = sorted(set(allowed_chars))
                    token = (allowed_chars[0], allowed_chars[-1])
                    i = j + 1
                    new_tokens, i = parse_quantifier(i, token)
                    tokens.extend(new_tokens)

                else:
                    # Literal character.
                    token = (ch, ch)
                    i += 1
                    new_tokens, i = parse_quantifier(i, token)
                    tokens.extend(new_tokens)
            if end_char is not None:
                raise ValueError("Expected closing " + end_char)
            return tokens, i

        tokens, _ = parse_sequence(0)
        first = "".join(t[0] for t in tokens)
        last = "".join(t[1] for t in tokens)
        return first, last

    def clean_zipcode(self, country, zipcode, variant='first'):
        """
        Cleans and formats a zipcode for the given country following a set of rules.
        Works with the cleaning regex under 'regex_clean'.

        Parameters:
          country (str): The country key used to retrieve configuration.
          zipcode (str, int, float): The zipcode to be cleaned.
          variant (str): Either 'first' or 'last'. Determines which zipcode template to use.
                         - 'first' (default): Uses 'zipcode_clean_first'. Missing or empty zipcode
                           returns the 'zipcode_clean_first' value. In per-position enforcement,
                           disallowed digits are replaced with '0' and letters with 'A'.
                         - 'last': Uses 'zipcode_clean_last'. Missing or empty zipcode returns the
                           'zipcode_clean_last' value. If the zipcode is too short, it is extended using
                           the tail of 'zipcode_clean_last'. In per-position enforcement, disallowed
                           digits are replaced with '9' and letters with 'Z'.

        Processing steps:
          1. Retrieve country-specific configuration:
               - zipcode_clean_first or zipcode_clean_last (depending on variant) as the template.
               - regex cleaning pattern (under key 'regex_clean').
          2. If the zipcode is missing or empty, return the template.
          3. Normalize the zipcode:
               - Convert non-string types to string.
               - Convert to uppercase.
               - Remove any characters except digits and uppercase letters.
          4. Use a shortcut: if the normalized zipcode fully matches the original regex pattern,
             return it immediately.
          5. Remove '^' and '$' anchors from the regex cleaning pattern.
          6. If the regex indicates a digits-only pattern, remove nondigit characters.
          7. If cleaning yields an empty zipcode, return the template.
          8. Adjust the zipcode's length to match the target length (based on the template):
               - If too long, first remove the country prefix (if present), then iteratively remove
                 trailing zeros and then leading zeros, and finally truncate if needed.
               - If too short, extend it by appending the missing tail of the template.
          9. Enforce allowed characters per position (only if the zipcode does not already match
             the original regex pattern). A helper function parses the regex (without anchors) into a
             list of allowed-character sets. For each position:
                 • If the current character is already allowed, keep it.
                 • Else, if the allowed set is digits-only, replace with:
                       - '0' if variant == 'first'
                       - '9' if variant == 'last'
                 • Else, if the allowed set is letters-only, replace with:
                       - 'A' if variant == 'first'
                       - 'Z' if variant == 'last'
                 • Otherwise (if mixed) choose the lexicographically smallest allowed character.

        Returns:
          str: The cleaned and adjusted zipcode.
        """
        # --- Helper: parse regex pattern into allowed sets for each position ---
        def parse_regex_pattern(pattern):
            """
            Parses a simplified fixed-length regex pattern (without anchors) into a list where
            each element is a set of allowed characters for that position.

            Supports:
              - Escaped sequences: \\d (digits), \\s (space)
              - Character classes: e.g., [A-Z]
              - Literal characters
              - Quantifiers of the form {n} or {min,max} (using the max value)
              - Optional operator (assumes token appears once)

            This parser is simplified and assumes the regex is well-formed.
            """
            allowed_sets = []
            i = 0
            while i < len(pattern):
                token_set = None
                if pattern[i] == '\\':
                    # Escaped sequence.
                    if i + 1 < len(pattern):
                        esc = pattern[i+1]
                        if esc == 'd':
                            token_set = set("0123456789")
                        elif esc == 's':
                            token_set = set(" ")
                        else:
                            token_set = {esc}
                        i += 2
                    else:
                        raise ValueError("Invalid pattern: ends with backslash")
                elif pattern[i] == '[':
                    # Character class.
                    j = pattern.find(']', i)
                    if j == -1:
                        raise ValueError("Invalid pattern: unterminated character class")
                    char_class = pattern[i+1:j]
                    token_set = set()
                    k = 0
                    while k < len(char_class):
                        if k + 2 < len(char_class) and char_class[k+1] == '-':
                            start = char_class[k]
                            end = char_class[k+2]
                            token_set.update(chr(c) for c in range(ord(start), ord(end)+1))
                            k += 3
                        else:
                            token_set.add(char_class[k])
                            k += 1
                    i = j + 1
                elif pattern[i] in "().?":
                    # Skip grouping and optional markers.
                    i += 1
                    continue
                else:
                    # Literal character.
                    token_set = {pattern[i]}
                    i += 1

                # Check for a following quantifier.
                if i < len(pattern) and pattern[i] == '{':
                    j = pattern.find('}', i)
                    if j == -1:
                        raise ValueError("Invalid pattern: unterminated quantifier")
                    quant_text = pattern[i+1:j].strip()
                    if ',' in quant_text:
                        parts = quant_text.split(',')
                        count = int(parts[-1].strip())
                    else:
                        count = int(quant_text)
                    allowed_sets.extend([token_set] * count)
                    i = j + 1
                elif i < len(pattern) and pattern[i] == '?':
                    # Optional: assume token appears once.
                    allowed_sets.append(token_set)
                    i += 1
                else:
                    allowed_sets.append(token_set)
            return allowed_sets

        # --- Main Cleaning Process ---
        regex = 'regex_clean'
        country_data = self.country.get(country)
        if country_data is None:
            raise DataInputError(f"Country '{country}' not found in ZipcodeManager.ZIPCODE_PATTERNS.",
                                 solution=f"Add '{country}' to existing ZIPCODE_PATTERNS or create new one.",
                                 values=f"'{country}'")

        # Select zipcode template and defaults based on variant.
        if variant == 'last':
            zipcode_template = country_data.get('zipcode_clean_last', '')
            default_digit = '9'
            default_letter = 'Z'
        else:
            zipcode_template = country_data.get('zipcode_clean_first', '')
            default_digit = '0'
            default_letter = 'A'

        # Step 0: If the zipcode is missing/empty, return the appropriate template.
        if pd.isna(zipcode) or zipcode == '':
            return zipcode_template

        # Step 1: Normalize the zipcode.
        if not isinstance(zipcode, str):
            zipcode = str(zipcode)
        zipcode = re.sub(r'[^0-9A-Z]', '', zipcode.upper())

        # ---- Shortcut: if the zipcode already matches the regex, return it.
        regex_pattern_raw = country_data.get(regex, '')
        if re.fullmatch(regex_pattern_raw, zipcode):
            return zipcode

        # Step 2: Remove regex anchors from the cleaning pattern.
        regex_pattern = regex_pattern_raw.lstrip('^').rstrip('$')

        # Step 3: If the regex indicates a digits-only pattern, remove nondigit characters.
        allowed_for_digits = set('\\d{}0123456789,')
        if set(regex_pattern) <= allowed_for_digits:
            zipcode = re.sub(r'\D+', '', zipcode)

        # Step 4: If cleaning yields an empty zipcode, return the appropriate template.
        if zipcode == '':
            return zipcode_template

        # Step 5: Adjust the zipcode's length.
        target_length = len(zipcode_template)
        # If too long, shorten it.
        if len(zipcode) > target_length:
            if zipcode.startswith(country):
                zipcode = zipcode[len(country):]
            while len(zipcode) > target_length and zipcode.endswith("0"):
                zipcode = zipcode[:-1]
            while len(zipcode) > target_length and zipcode.startswith("0"):
                zipcode = zipcode[1:]
            if len(zipcode) > target_length:
                zipcode = zipcode[:target_length]
        # If too short, extend it.
        if len(zipcode) < target_length:
            zipcode = zipcode + zipcode_template[len(zipcode):]

        # Step 6: Enforce allowed character types per position only if zipcode doesn't match the regex.
        if not re.fullmatch(regex_pattern_raw, zipcode):
            allowed_sets = parse_regex_pattern(regex_pattern)
            final_length = min(target_length, len(allowed_sets))
            adjusted_chars = []
            for i in range(final_length):
                current_char = zipcode[i]
                allowed = allowed_sets[i]
                if current_char in allowed:
                    adjusted_chars.append(current_char)
                else:
                    if allowed.issubset(set("0123456789")):
                        adjusted_chars.append(default_digit)
                    elif allowed.issubset(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")):
                        adjusted_chars.append(default_letter)
                    else:
                        adjusted_chars.append(sorted(allowed)[0])
            if len(zipcode) > final_length:
                adjusted_chars.append(zipcode[final_length:])
            zipcode = "".join(adjusted_chars)

        return zipcode


    def adjacent_zipcode(self, country, zipcode, direction='next'):
        """
        Returns the previous or next zipcode within the fixed range [first_zipcode, last_zipcode],
        using regex_clean to compute per-position allowed sets and dynamically sized bases.
        """
        cfg = self.country.get(country)
        if not cfg:
            raise ValueError(f"No config for country '{country}'")
        first_zip = cfg['zipcode_clean_first']
        last_zip  = cfg['zipcode_clean_last']
        raw_regex = cfg['regex_clean']

        # 1) Build per-position allowed sets from regex_clean
        pattern = raw_regex.lstrip('^').rstrip('$')
        allowed_sets = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '\\':                       # \d or \s or literal
                esc = pattern[i+1]
                token = set('0123456789') if esc == 'd' else \
                    set(' ')            if esc == 's' else {esc}
                i += 2
            elif pattern[i] == '[':                     # character class
                j = pattern.index(']', i)
                token = set()
                cls = pattern[i+1:j]
                k = 0
                while k < len(cls):
                    if k+2 < len(cls) and cls[k+1]=='-':
                        for c in range(ord(cls[k]), ord(cls[k+2])+1):
                            token.add(chr(c))
                        k += 3
                    else:
                        token.add(cls[k]); k += 1
                i = j+1
            elif pattern[i] in '().?':                  # skip grouping/optional
                i += 1; continue
            else:                                       # literal
                token = {pattern[i]}
                i += 1

            # quantifier {n} or {min,max}
            if i< len(pattern) and pattern[i]=='{':
                j = pattern.index('}', i)
                txt = pattern[i+1:j]
                count = int(txt.split(',',1)[-1])
                allowed_sets += [token]*count
                i = j+1
            elif i< len(pattern) and pattern[i]=='?':   # optional => assume once
                allowed_sets.append(token)
                i += 1
            else:
                allowed_sets.append(token)

        # 2) clamp if already at a boundary
        if direction=='previous' and zipcode==first_zip: return first_zip
        if direction=='next'     and zipcode==last_zip:  return last_zip

        # 3) length check
        if len(zipcode)!=len(allowed_sets):
            raise ValueError("Zipcode length mismatch")

        # 4) map input chars to numeric values and bases
        values, bases = [], []
        for idx, ch in enumerate(zipcode):
            aset = allowed_sets[idx]
            if ch not in aset:
                raise ValueError(f"Invalid char {ch!r} at pos {idx}")
            sorted_list = sorted(aset)  # e.g. ['0','1',...,'9','A',...,'Z'] or ['A',...,'Z']
            base = len(sorted_list)
            val  = sorted_list.index(ch)
            values.append(val)
            bases.append((base, sorted_list))

        # 5) add or subtract 1 with carry/borrow
        delta = 1 if direction=='next' else -1
        carry = delta
        for i in range(len(values)-1, -1, -1):
            base, _ = bases[i]
            newv = values[i] + carry
            if newv >= base:
                values[i] = 0
                carry = 1
            elif newv < 0:
                values[i] = base - 1
                carry = -1
            else:
                values[i] = newv
                carry = 0
                break

        # 6) if overflow/underflow, clamp
        if carry!=0:
            return last_zip if direction=='next' else first_zip

        # 7) rebuild string
        out = []
        for val, (base, sorted_list) in zip(values, bases):
            out.append(sorted_list[val])
        result = ''.join(out)

        # 8) final clamp
        if direction=='next'     and result> last_zip: result = last_zip
        if direction=='previous' and result< first_zip: result = first_zip

        return result

    # ===== This part is to introduce fast lookup for
    @staticmethod
    def _parse_regex_to_allowed_sets(pattern: str) -> list[set[str]]:
        """
        Strips ^/$ anchors and turns a fixed‐length regex_clean pattern
        into, for each position, the set of allowed characters.
        """
        allowed_sets = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '\\':            # \d, \s, or literal
                esc = pattern[i+1]
                if esc == 'd':
                    token_set = set('0123456789')
                elif esc == 's':
                    token_set = {' '}
                else:
                    token_set = {esc}
                i += 2

            elif pattern[i] == '[':          # character class
                j = pattern.find(']', i)
                char_class = pattern[i+1:j]
                token_set = set()
                k = 0
                while k < len(char_class):
                    if k+2 < len(char_class) and char_class[k+1] == '-':
                        start, end = char_class[k], char_class[k+2]
                        token_set.update(chr(c) for c in range(ord(start), ord(end)+1))
                        k += 3
                    else:
                        token_set.add(char_class[k]); k += 1
                i = j+1

            elif pattern[i] in '().?':       # skip grouping/optional markers
                i += 1
                continue

            else:                            # literal
                token_set = {pattern[i]}
                i += 1

            # see if there's a '{n}' quantifier or '?' right after
            if i < len(pattern) and pattern[i] == '{':
                j = pattern.find('}', i)
                quant = pattern[i+1:j]
                count = int(quant.split(',',1)[-1])
                allowed_sets.extend([token_set] * count)
                i = j+1
            elif i < len(pattern) and pattern[i] == '?':
                allowed_sets.append(token_set)
                i += 1
            else:
                allowed_sets.append(token_set)

        return allowed_sets

    @lru_cache(maxsize=None)
    def get_zipcode_key_fn(self, country_code: str) -> Callable[[str], int]:
        """
        Returns a picklable callable that maps a *clean* zipcode string for `country_code`
        into a unique integer key.
        """
        country = country_code.upper()
        if country not in self.country:
            raise ValueError(f"Unknown country {country!r}")

        raw = self.country[country]['regex_clean']
        pattern = raw.lstrip('^').rstrip('$')
        allowed_sets = self._parse_regex_to_allowed_sets(pattern)
        sorted_lists = [sorted(s) for s in allowed_sets]

        # Precompute positional multipliers:
        multipliers = []
        prod = 1
        for s in reversed(sorted_lists):
            multipliers.insert(0, prod)
            prod *= len(s)

        # Return an instance of MixedRadixZipKey, which is picklable
        return MixedRadixZipKey(sorted_lists, multipliers)


    def generate_country_all_zipcodes(self, country):
        # Generates all possible zipcodes for a country.
        first = self.zipcode_clean_first.get(country)
        last = self.zipcode_clean_last.get(country)
        current = first
        if first is None or last is None:
            raise DataInputError(f"Country {country} not not in _ZIPCODE_PATTERNS",
                                 solution='Please update ZipcodeManager._ZIPCODE_PATTERNS')
        while True:
            yield current
            if current == last:
                break
            current = self.adjacent_zipcode(country, current)

if __name__ == '__main__':
    zm = ZipcodeManager()

    # zipcodes = zm.generate_country_all_zipcodes('PL')
    # while True:
    #     try:
    #         print(next(zipcodes))
    #     except StopIteration:
    #         print('No more zipcodes')
    #         break

    # zm.get_zipcode_key_fn('NL')('1234AB')  # This is how to translate key into int_key
    # zm.is_valid_zipcode('NL', '123112', 'regex_official')
    # zm.is_valid_zipcode('NL', '1231AA', 'regex_official')
    # zm.is_valid_zipcode('NL', '1231 AA', 'regex_official')
    # zm.is_valid_zipcode('NL', '1231AA', 'regex_clean')
    # zm.clean_zipcode('PL', 'AB134e43')
    # zm.adjacent_zipcode('GB', 'AB00000', direction='previous')

    # # Zipcode validity (official vs clean pattern)
    # zm.is_valid_zipcode('PL', '12-345', 'regex_official')
    # zm.is_valid_zipcode('PL', '12345', 'regex_official')
    # zm.is_valid_zipcode('PL', '12345', 'regex_clean')
    #
    # # Generate first/last zipcode per pattern
    # zm._generate_first_last_zipcode(r'\d{1,3}')
    # zm._generate_first_last_zipcode(zm.country['NL']['regex_official'])
    #
    # # Clean zipcode (fill varint first/last)
    # zm.clean_zipcode('NL', '001234KK')  # variant='first'
    # zm.clean_zipcode('NL', '10')  # variant='first'
    # zm.clean_zipcode('NL', '10', variant='last')
    # zm.clean_zipcode('GB', 'B1')  # variant='first'
    # zm.clean_zipcode('GB', 'B1', variant='last')  # variant='first'
    #
    # # Adjacent zipcode next/previous
    # zm.adjacent_zipcode('GB', 'AB00000', direction='next')
    # zm.adjacent_zipcode('GB', 'AB00000', direction='previous')
    #
    # # future - make a proper testing module
    # def runtest(test_dict):
    #     for ctry in test_dict.get('ctry'):
    #         for variant in test_dict.get('variant'):
    #             print(ctry, variant)
    #             for zipcode in test_dict.get('zipcode'):
    #                 print(f'{zipcode:10} -> {zm.clean_zipcode(ctry, zipcode, variant)}')
    #
    # test = {
    #     'ctry': ['PL', 'NL', 'GB'],
    #     'variant': ['first', 'last'],
    #     'zipcode': ['', '0', '00', '10', 10, '1110', '10001', 'AA23-3'],
    # }
    # runtest(test)
    #
    # # Examples how to apply on DataFrame, use proper regex!
    # path_zips = r'Postal_codes_EU_in_SAP.xlsx'
    # df = pd.read_excel(path_zips, engine='calamine', usecols='A:C', names=['ctry', 'ctrytext', 'zipcode'], dtype='str')
    # df['regex_official'] = df.ctry.map({ctry: v['regex_official'] for ctry, v in zm.country.items()})
    # df['check_official'] = df.apply(lambda row: zm.is_valid_zipcode(row['ctry'], row['zipcode'], 'regex_official'), axis=1)
    # print(df['check_official'].value_counts())
    # df['zipcode_clean'] = df.apply(lambda row: zm.clean_zipcode(row['ctry'], row['zipcode']), axis=1)
    # df['check_clean'] = df.apply(lambda row: zm.is_valid_zipcode(row['ctry'], row['zipcode_clean'], regex='regex_clean'), axis=1)
    # print(df['check_clean'].value_counts())
