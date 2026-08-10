import re

def parse_bibtex(text):
    entries = []
    entry_pattern = re.compile(r'@(\w+)\s*\{\s*([^,]+),', re.IGNORECASE)

    def read_braced_value(s, i):
        """s[i] == '{'; return (value, index_after_closing_brace)."""
        depth = 0
        start = i
        while i < len(s):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    return s[start + 1:i], i + 1
            i += 1
        return s[start + 1:i], i  # unterminated, best effort

    for m in entry_pattern.finditer(text):
        entry_type, entry_id = m.group(1), m.group(2).strip()

        # locate matching closing brace of the whole entry
        block_start = text.index('{', m.start())
        _, block_end = read_braced_value(text, block_start)
        block = text[block_start + 1:block_end - 1]

        # parse fields within the block
        fields = {}
        i = 0
        field_re = re.compile(r'(\w+)\s*=\s*', re.IGNORECASE)
        while True:
            fm = field_re.search(block, i)
            if not fm:
                break
            key = fm.group(1).lower()
            j = fm.end()
            if j < len(block) and block[j] == '{':
                value, i = read_braced_value(block, j)
            elif j < len(block) and block[j] == '"':
                end = block.index('"', j + 1)
                value, i = block[j + 1:end], end + 1
            else:
                end = block.find(',', j)
                end = end if end != -1 else len(block)
                value, i = block[j:end].strip(), end
            fields[key] = value.strip()

        entries.append({"type": entry_type, "id": entry_id, "fields": fields})

    return entries
