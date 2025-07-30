

#!/usr/bin/env python3
import re
import sys
from typing import List, Tuple

import pyperclip
from mdbt.core import Core

class ColumnSorter(Core):
    """Sorts SQL select lines from the clipboard based on alias and data‐type rules."""

    def __init__(self) -> None:
        """Initialize ColumnSorter with the raw lines to sort.

        Args:
            lines: A list of lines (each line is one select‐list entry, typically starting with a comma).
        """
        super().__init__()

    def main(self) -> None:
        """Read lines from the clipboard, sort them, write them back, and print."""
        # 1) Read everything currently on the clipboard
        try:
            clipboard_content = pyperclip.paste()
        except pyperclip.PyperclipException:
            sys.stderr.write('Error: could not access clipboard. Is pyperclip installed and supported?\n')
            sys.exit(1)

        # 2) Split into individual lines
        lines = clipboard_content.splitlines()

        # 3) Sort them
        sorter = ColumnSorter()
        sorted_lines = sorter.sort_lines(lines)

        # 4) Join back together
        result = '\n'.join(sorted_lines)

        # 5) Copy sorted result back to clipboard
        try:
            pyperclip.copy(result)
        except pyperclip.PyperclipException:
            sys.stderr.write('Warning: could not write back to clipboard. Outputting to stdout instead.\n')
            print(result)
            sys.exit(0)

        # 6) Also print to stdout for verification
        print(result)

    def parse_line(self, line: str) -> Tuple[str, str, str]:
        """Split one line into (prefix, full_expression, alias).

        - Prefix is any leading commas/spaces (e.g. ', ' and indentation).
        - full_expression is everything after that prefix, up to the alias (if one exists).
        - alias is the name used for sorting (the part after 'AS', or if no AS, the base column name).

        Args:
            line: A single select‐list line, e.g. ', "FOO"::varchar as foo_id' or ', project_id'.

        Returns:
            A tuple (prefix, full_expression, alias):
            - prefix: leading commas and spaces (e.g. ', '),
            - full_expression: the expression/column + cast (e.g. '"FOO"::varchar'),
            - alias: the alias (e.g. 'foo_id') or base column name if no AS.
        """
        # 1) Extract prefix (leading comma + whitespace), if present
        m = re.match(r'^(\s*,\s*)(.*)$', line)
        if m:
            prefix = m.group(1)
            rest = m.group(2).strip()
        else:
            # No leading comma, treat everything as rest
            prefix = ''
            rest = line.strip()

        # 2) Look for 'AS' (case-insensitive), split into left/right
        #    Use regex to split on whitespace+as+whitespace, max once
        lower_rest = rest.lower()
        if re.search(r'\s+as\s+', lower_rest):
            parts = re.split(r'\s+as\s+', rest, maxsplit=1, flags=re.IGNORECASE)
            expression_part = parts[0].strip()
            alias = parts[1].strip()
        else:
            # No AS: take expression exactly as rest; derive alias from expression
            expression_part = rest
            # If there's a '::', drop the cast and use the part before it
            if '::' in expression_part:
                alias = expression_part.split('::', 1)[0].strip()
            else:
                # If nothing to split, alias is simply the whole rest
                alias = expression_part

        return prefix, expression_part, alias

    def get_group(self, expression: str, alias: str) -> int:
        """Determine sorting group (0..4) for a given line.

        The rules (in order) are:
          0: alias ends with '_id'
          1: alias ends with '_at'
          2: alias starts with 'is_'
          3: anything except variant casts
          4: fields cast as VARIANT (i.e., '::variant' appears)

        Args:
            expression: The full expression (column plus any cast).
            alias: The alias to use for naming rules.

        Returns:
            An integer group (0 through 4), where lower means higher priority.
        """
        a = alias.lower()
        expr_lower = expression.lower()

        if a.endswith('_id'):
            return 0
        if a.endswith('_at'):
            return 1
        if a.startswith('is_'):
            return 2
        # Check for VARIANT cast
        if re.search(r'::\s*variant\b', expr_lower):
            return 4
        # Otherwise, everything else is group 3
        return 3

    def sort_lines(self, lines: List[str]) -> List[str]:
        """Sort all stored lines according to group and alias.

        Returns:
            A new list of lines (with original prefixes) in sorted order.
        """
        parsed: List[Tuple[int, str, str, str]] = []
        # parsed tuples: (group, alias_lower, prefix, full_expression)
        for raw_line in lines:
            # Skip empty lines
            if not raw_line.strip():
                continue
            prefix, expr, alias = self.parse_line(raw_line)
            group = self.get_group(expr, alias)
            parsed.append((group, alias.lower(), prefix, expr))

        # Sort first by group number, then by alias lexicographically
        parsed.sort(key=lambda t: (t[0], t[1]))

        # Reconstruct each line as prefix + expression [ + ' as ' + alias if original had AS ]
        # BUT to preserve the original "AS" style, we’ll just print prefix + expression + ' as ' + alias
        # except if alias exactly equals the expression (i.e. no AS in original), then drop ' as '.
        sorted_lines: List[str] = []
        for group, alias_lower, prefix, expr in parsed:
            # Determine if original expr already contained ' as alias_lower' (case-insensitive)
            # We can check if expr.lower().endswith(alias_lower) but that fails if casting was present.
            # Instead, if alias_lower != expr.split('::')[0].strip().lower(), we assume original used AS.
            base_no_cast = expr.split('::', 1)[0].strip().lower()
            if base_no_cast != alias_lower:
                # original must have had an explicit alias, so we add ' as alias'
                line_text = f'{prefix}{expr} as {alias_lower}'
            else:
                # no AS needed
                line_text = f'{prefix}{expr}'
            sorted_lines.append(line_text)

        return sorted_lines
