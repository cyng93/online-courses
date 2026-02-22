#!/usr/bin/env python3
"""
Validate and fix common SRT timestamp issues:
  1. Invalid timestamps where seconds >= 60 (e.g., 00:02:75,000 → 00:03:15,000)
  2. Out-of-order / overlapping blocks (start_time < previous block's start_time)
  3. Duplicate consecutive blocks (same text, adjacent timestamps)

Usage:
  python3 validate_srt.py <srt_file> [--fix]

Without --fix, only reports issues. With --fix, writes corrected file in-place.
"""
import re
import sys


def ts_to_ms(ts: str) -> int:
    """Convert SRT timestamp (HH:MM:SS,mmm) to milliseconds.
    Handles invalid seconds >= 60 by carrying over to minutes."""
    h, m, rest = ts.split(':')
    s, ms = rest.split(',')
    total_seconds = int(h) * 3600 + int(m) * 60 + int(s)
    return total_seconds * 1000 + int(ms)


def ms_to_ts(ms: int) -> str:
    """Convert milliseconds to SRT timestamp (HH:MM:SS,mmm)."""
    if ms < 0:
        ms = 0
    total_s, millis = divmod(ms, 1000)
    total_m, s = divmod(total_s, 60)
    h, m = divmod(total_m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{millis:03d}"


def is_valid_ts(ts: str) -> bool:
    """Check if a timestamp has valid HH:MM:SS,mmm where SS < 60."""
    m = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})', ts)
    if not m:
        return False
    return int(m.group(3)) < 60


def normalize_ts(ts: str) -> str:
    """Normalize a potentially invalid timestamp (seconds >= 60) to valid SRT format."""
    return ms_to_ts(ts_to_ms(ts))


def parse_srt_raw(content: str):
    """Parse SRT content into blocks, preserving raw timestamps."""
    blocks = []
    pattern = re.compile(
        r'(\d+)\n(\d{2}:\d{2}:\d{2,},\d{3}) --> (\d{2}:\d{2}:\d{2,},\d{3})\n(.+?)(?=\n\n|\n*$)',
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


def validate_and_fix(filepath: str, fix: bool = False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = parse_srt_raw(content)
    if not blocks:
        print(f"  ERROR: No blocks found in {filepath}", file=sys.stderr)
        return False

    issues = []
    fixed_count = 0

    # Pass 1: Fix invalid timestamps (seconds >= 60)
    for b in blocks:
        if not is_valid_ts(b['start']):
            old = b['start']
            b['start'] = normalize_ts(b['start'])
            issues.append(f"  Block {b['index']}: invalid start {old} → {b['start']}")
            fixed_count += 1
        if not is_valid_ts(b['end']):
            old = b['end']
            b['end'] = normalize_ts(b['end'])
            issues.append(f"  Block {b['index']}: invalid end {old} → {b['end']}")
            fixed_count += 1

    # Pass 2: Check for out-of-order blocks
    for i in range(1, len(blocks)):
        prev_start = ts_to_ms(blocks[i - 1]['start'])
        curr_start = ts_to_ms(blocks[i]['start'])
        if curr_start < prev_start:
            issues.append(
                f"  Block {blocks[i]['index']}: out-of-order "
                f"(start {blocks[i]['start']} < prev start {blocks[i-1]['start']})"
            )

    # Pass 3: Check for overlapping blocks (start < previous end)
    for i in range(1, len(blocks)):
        prev_end = ts_to_ms(blocks[i - 1]['end'])
        curr_start = ts_to_ms(blocks[i]['start'])
        if curr_start < prev_end:
            issues.append(
                f"  Block {blocks[i]['index']}: overlap "
                f"(start {blocks[i]['start']} < prev end {blocks[i-1]['end']})"
            )

    # Pass 4: Check for duplicate consecutive blocks (same text)
    for i in range(1, len(blocks)):
        if blocks[i]['text'] == blocks[i - 1]['text']:
            issues.append(
                f"  Block {blocks[i]['index']}: duplicate text with block {blocks[i-1]['index']} "
                f"(\"{blocks[i]['text'][:30]}...\")"
            )

    # Report
    print(f"\n{'='*60}")
    print(f"File: {filepath}")
    print(f"Total blocks: {len(blocks)}")
    if issues:
        print(f"Issues found: {len(issues)}")
        for issue in issues:
            print(issue)
    else:
        print("No issues found. ✓")

    if fix and fixed_count > 0:
        # Re-number blocks sequentially
        for i, b in enumerate(blocks, 1):
            b['index'] = i
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(build_srt(blocks))
        print(f"\n  → Fixed {fixed_count} timestamp issues and saved.")

    return len(issues) == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <srt_file> [--fix]", file=sys.stderr)
        sys.exit(1)

    fix_mode = '--fix' in sys.argv
    files = [f for f in sys.argv[1:] if f != '--fix']

    all_ok = True
    for fp in files:
        ok = validate_and_fix(fp, fix=fix_mode)
        if not ok:
            all_ok = False

    sys.exit(0 if all_ok else 1)
