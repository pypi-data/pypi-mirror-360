"""Regexes used to parse markdown."""

import re


# regex to extract code blocks from markdown text
CODE_BLOCK_REGEX = re.compile(
    pattern=r"\`\`\`(\w*)\n(.*?)(?:\`\`\`|$)",
    flags=re.DOTALL,
)
