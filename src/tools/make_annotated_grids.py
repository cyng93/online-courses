#!/usr/bin/env python3
"""
Create annotated grid composites from individual subtitle frames.

Each row in the grid is labeled with:
  - Frame number (e.g., _0002)
  - Corresponding second (e.g., 1s)
  - SRT timestamp (e.g., 00:00:01)

Also generates a sidecar TSV file ({video_id}_timestamps.tsv) that maps
each grid row to its exact SRT timestamp. The OCR agent should read
subtitle TEXT from images but look up timestamps from this TSV file,
eliminating vision-to-timestamp transcription errors entirely.

Usage:
    python3 make_annotated_grids.py <frames_dir> <video_id> [--output-dir <dir>] [--batch 10]

Example:
    python3 make_annotated_grids.py step1-output/subtitle_frames_for_ocr 0-1 \\
        --output-dir step1-output/subtitle_frames_for_ocr
"""

import argparse
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def format_srt_time(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def find_frames(frames_dir: Path, video_id: str) -> list[tuple[int, Path]]:
    """Find all individual frame files (not grids) for a video, sorted by frame number."""
    pattern = re.compile(rf"^{re.escape(video_id)}_(\d{{4}})\.jpg$")
    frames = []
    for f in os.listdir(frames_dir):
        match = pattern.match(f)
        if match:
            frame_num = int(match.group(1))
            frames.append((frame_num, frames_dir / f))
    frames.sort()
    return frames


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a good monospace font, fall back to default."""
    font_paths = [
        "/System/Library/Fonts/Menlo.ttc",          # macOS
        "/System/Library/Fonts/SFMono-Regular.otf",  # macOS
        "/System/Library/Fonts/Courier.dfont",       # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def create_annotated_grid(
    frames: list[tuple[int, Path]],
    output_path: Path,
    label_width: int = 280,
    font_size: int = 28,
):
    """
    Create a single annotated grid image from a list of frames.

    Each row gets a label on the left side showing:
      _NNNN | Xs | HH:MM:SS
    """
    if not frames:
        return

    font = get_font(font_size)

    # Load first frame to get dimensions
    sample = Image.open(frames[0][1])
    frame_w, frame_h = sample.size

    grid_w = label_width + frame_w
    grid_h = frame_h * len(frames)

    grid = Image.new("RGB", (grid_w, grid_h), color=(0, 0, 0))
    draw = ImageDraw.Draw(grid)

    for i, (frame_num, frame_path) in enumerate(frames):
        # Load frame
        frame_img = Image.open(frame_path)
        y_offset = i * frame_h

        # Draw label background
        draw.rectangle(
            [(0, y_offset), (label_width - 1, y_offset + frame_h - 1)],
            fill=(30, 30, 30),
        )

        # Draw label text
        sec = frame_num - 1
        srt_time = format_srt_time(sec)
        label = f"_{frame_num:04d}\n{sec}s\n{srt_time}"

        # Center text vertically in the row
        draw.text(
            (10, y_offset + 8),
            label,
            fill=(0, 255, 0),  # green text on dark bg
            font=font,
        )

        # Draw separator line
        draw.line(
            [(0, y_offset), (grid_w, y_offset)],
            fill=(80, 80, 80),
            width=1,
        )

        # Paste frame image
        grid.paste(frame_img, (label_width, y_offset))

    grid.save(output_path, quality=90)


def main():
    parser = argparse.ArgumentParser(
        description="Create annotated grid composites with frame numbers and timestamps"
    )
    parser.add_argument("frames_dir", type=Path, help="Directory containing frame images")
    parser.add_argument("video_id", help='Video ID prefix (e.g., "0-1", "1-1")')
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Output directory for grids (default: same as frames_dir)",
    )
    parser.add_argument("--batch", type=int, default=10, help="Frames per grid (default: 10)")
    parser.add_argument(
        "--label-width", type=int, default=280,
        help="Width of the label column in pixels (default: 280)",
    )
    parser.add_argument("--font-size", type=int, default=28, help="Font size for labels (default: 28)")
    args = parser.parse_args()

    if not args.frames_dir.exists():
        print(f"Error: frames directory not found: {args.frames_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = args.output_dir or args.frames_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = find_frames(args.frames_dir, args.video_id)
    if not frames:
        print(f"No frames found for video '{args.video_id}' in '{args.frames_dir}'", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(frames)} frames for video '{args.video_id}'")

    # Split into batches
    total_grids = (len(frames) + args.batch - 1) // args.batch
    grid_fmt = "%03d" if total_grids > 99 else "%02d"

    for grid_idx in range(total_grids):
        start = grid_idx * args.batch
        end = min(start + args.batch, len(frames))
        batch_frames = frames[start:end]

        grid_num = grid_idx + 1
        output_path = output_dir / f"{args.video_id}_annotated_grid_{grid_num:{grid_fmt.replace('%', '').replace('d', '')}}.jpg"
        # Simpler approach for formatting
        if total_grids > 99:
            fname = f"{args.video_id}_annotated_grid_{grid_num:03d}.jpg"
        else:
            fname = f"{args.video_id}_annotated_grid_{grid_num:02d}.jpg"
        output_path = output_dir / fname

        create_annotated_grid(
            batch_frames,
            output_path,
            label_width=args.label_width,
            font_size=args.font_size,
        )
        frame_range = f"_{batch_frames[0][0]:04d} to _{batch_frames[-1][0]:04d}"
        print(f"  Grid {grid_num:>{len(str(total_grids))}}/{total_grids}: {fname} ({frame_range})")

    # Generate sidecar TSV: maps each grid row to its exact SRT timestamp
    tsv_path = output_dir / f"{args.video_id}_timestamps.tsv"
    with open(tsv_path, "w", encoding="utf-8") as tsv:
        tsv.write("grid_file\trow\tframe\tsecond\tsrt_timestamp\n")
        for grid_idx in range(total_grids):
            start = grid_idx * args.batch
            end = min(start + args.batch, len(frames))
            batch_frames = frames[start:end]

            grid_num = grid_idx + 1
            if total_grids > 99:
                fname = f"{args.video_id}_annotated_grid_{grid_num:03d}.jpg"
            else:
                fname = f"{args.video_id}_annotated_grid_{grid_num:02d}.jpg"

            for row_idx, (frame_num, _) in enumerate(batch_frames, 1):
                sec = frame_num - 1
                srt_time = format_srt_time(sec)
                tsv.write(f"{fname}\t{row_idx}\t_{frame_num:04d}\t{sec}\t{srt_time}\n")

    print(f"\nCreated {total_grids} annotated grids in {output_dir}")
    print(f"Sidecar timestamp file: {tsv_path}")


if __name__ == "__main__":
    main()
