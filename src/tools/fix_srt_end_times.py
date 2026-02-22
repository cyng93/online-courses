#!/usr/bin/env python3
"""
Fix SRT end times: set each block's end_time = next block's start_time.
Last block keeps its original end_time.
"""
import re, sys

def parse_srt(content):
    """Parse SRT into list of (index, start, end, text) tuples."""
    blocks = []
    pattern = re.compile(
        r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\n*$)',
        re.DOTALL
    )
    for m in pattern.finditer(content):
        blocks.append({
            'index': int(m.group(1)),
            'start': m.group(2),
            'end': m.group(3),
            'text': m.group(4).strip(),
        })
    return blocks

def build_srt(blocks):
    """Build SRT string from blocks."""
    lines = []
    for b in blocks:
        lines.append(f"{b['index']}")
        lines.append(f"{b['start']} --> {b['end']}")
        lines.append(b['text'])
        lines.append('')
    return '\n'.join(lines)

for filepath in sys.argv[1:]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = parse_srt(content)
    if not blocks:
        print(f"No blocks found in {filepath}", file=sys.stderr)
        continue

    # Set each block's end_time = next block's start_time
    for i in range(len(blocks) - 1):
        blocks[i]['end'] = blocks[i + 1]['start']

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(build_srt(blocks))

    print(f"Fixed {len(blocks)} blocks in {filepath}")

