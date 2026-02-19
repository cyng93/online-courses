#!/usr/bin/env python3
"""Parse SRT files and output structured JSON for HTML/Markdown generation.

Usage: python3 parse_srt.py /path/to/course-dir
  Reads course.json from the course directory for video metadata.
  Reads SRT files from step3-input/subtitles/
  Writes transcripts.json to step3-output/
"""

import json
import re
import sys
from pathlib import Path


def parse_srt(filepath: Path) -> list[str]:
    """Parse SRT file and return list of subtitle text lines (no timestamps/numbers)."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    texts = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Skip sequence number (digit-only lines)
        if re.match(r"^\d+$", line):
            i += 1
            # Skip timestamp line
            if i < len(lines) and "-->" in lines[i]:
                i += 1
            # Read subtitle text (could be multi-line)
            while i < len(lines) and lines[i].strip():
                texts.append(lines[i].strip())
                i += 1
        i += 1

    return texts


def deduplicate(texts: list[str]) -> list[str]:
    """Deduplicate consecutive identical lines and return as list."""
    if not texts:
        return []

    deduped = [texts[0]]
    for t in texts[1:]:
        if t != deduped[-1]:
            deduped.append(t)

    return deduped


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_srt.py /path/to/course-dir", file=sys.stderr)
        sys.exit(1)

    course_dir = Path(sys.argv[1]).resolve()
    config_path = course_dir / "course.json"

    if not config_path.exists():
        print(f"ERROR: course.json not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    subtitle_lang = config.get("subtitle_lang", "zh-TW")
    srt_dir = course_dir / "step3-input" / "subtitles"
    out_dir = course_dir / "step3-output"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for video in config["videos"]:
        video_id = video["id"]
        title = video["title"]
        srt_file = srt_dir / f"{video_id}_{title}_{subtitle_lang}_visual.srt"

        if not srt_file.exists():
            print(f"WARNING: {srt_file.name} not found!", file=sys.stderr)
            continue

        texts = parse_srt(srt_file)
        lines = deduplicate(texts)
        entry_count = len(texts)

        results.append({
            "id": video_id,
            "title": title,
            "full_title": f"{video_id} {title}",
            "entry_count": entry_count,
            "lines": lines,
        })
        print(f"  Parsed {srt_file.name}: {entry_count} entries, {len(lines)} lines", file=sys.stderr)

    # Output JSON
    output = {
        "course_title": config["course_title"],
        "author": config["author"],
        "total_videos": len(results),
        "videos": results,
    }

    json_path = out_dir / "transcripts.json"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {json_path} ({len(results)} videos)", file=sys.stderr)


if __name__ == "__main__":
    main()
