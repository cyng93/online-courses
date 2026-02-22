#!/usr/bin/env python3
"""
Segment subtitle frames into groups with the same subtitle text.

This script:
1. Reads individual frame images extracted at 1fps
2. Compares consecutive frames using pixel difference
3. Groups frames with the same subtitle into segments
4. Outputs representative frames and timestamps for OCR

Frame naming: {video_id}_{frame_num:04d}.jpg
Frame timing: frame _NNNN.jpg corresponds to pts_time (NNNN - 1) seconds
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import sys

import numpy as np
from PIL import Image


def load_image_as_array(image_path: Path) -> np.ndarray:
    """Load an image and convert to numpy array."""
    img = Image.open(image_path)
    return np.array(img)


def calculate_frame_difference(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Calculate the mean absolute pixel difference between two frames.

    Returns a value between 0 (identical) and 255 (completely different).
    """
    diff = np.abs(img1.astype(np.float32) - img2.astype(np.float32))
    return np.mean(diff)


def is_blank_frame(img: np.ndarray, blank_threshold: float = 30.0) -> bool:
    """
    Detect if a frame is blank (no subtitle text).

    Blank frames typically have low variance and dark/uniform colors.
    We check if the standard deviation of pixel values is below threshold.
    """
    # Convert to grayscale for simpler analysis
    if len(img.shape) == 3:
        gray = np.mean(img, axis=2)
    else:
        gray = img

    std_dev = np.std(gray)
    return std_dev < blank_threshold


def segment_frames(
    frames_dir: Path,
    video_id: str,
    diff_threshold: float = 15.0,
    blank_threshold: float = 30.0,
    min_segment_duration: int = 1
) -> List[Dict]:
    """
    Segment frames into groups with the same subtitle.

    Args:
        frames_dir: Directory containing frame images
        video_id: Video identifier (e.g., "0-1")
        diff_threshold: Threshold for considering frames different (0-255)
        blank_threshold: Threshold for detecting blank frames
        min_segment_duration: Minimum segment duration in seconds

    Returns:
        List of segment dictionaries with:
        - video_id: str
        - segment_id: int
        - start_time: float (seconds)
        - end_time: float (seconds)
        - frame_count: int
        - representative_frame: str (filename)
    """
    # Find all frames for this video
    pattern = re.compile(rf'^{re.escape(video_id)}_(\d{{4}})\.jpg$')
    frame_files = []

    for filename in sorted(os.listdir(frames_dir)):
        match = pattern.match(filename)
        if match:
            frame_num = int(match.group(1))
            frame_files.append((frame_num, filename))

    if not frame_files:
        raise ValueError(f"No frames found for video_id: {video_id}")

    frame_files.sort()
    print(f"Found {len(frame_files)} frames for video {video_id}")

    segments = []
    current_segment = None
    prev_img = None

    for i, (frame_num, filename) in enumerate(frame_files):
        frame_path = frames_dir / filename
        curr_img = load_image_as_array(frame_path)

        # Calculate timestamp (frame _NNNN corresponds to time NNNN-1)
        timestamp = frame_num - 1

        # Check if current frame is blank
        is_blank = is_blank_frame(curr_img, blank_threshold)

        if is_blank:
            # End current segment if we hit a blank frame
            if current_segment is not None:
                segments.append(current_segment)
                current_segment = None
            prev_img = curr_img
            continue

        # Compare with previous frame (if exists and not blank)
        if prev_img is not None and not is_blank_frame(prev_img, blank_threshold):
            diff = calculate_frame_difference(prev_img, curr_img)
            is_same_subtitle = diff < diff_threshold
        else:
            # First non-blank frame or after blank frame
            is_same_subtitle = False

        if not is_same_subtitle:
            # Save previous segment if it exists
            if current_segment is not None:
                segments.append(current_segment)

            # Start new segment
            current_segment = {
                'video_id': video_id,
                'segment_id': len(segments) + 1,
                'start_time': timestamp,
                'end_time': timestamp,
                'start_frame': frame_num,
                'end_frame': frame_num,
                'frame_count': 1,
                'representative_frame': filename
            }
        else:
            # Continue current segment
            current_segment['end_time'] = timestamp
            current_segment['end_frame'] = frame_num
            current_segment['frame_count'] += 1

        prev_img = curr_img

    # Don't forget the last segment
    if current_segment is not None:
        segments.append(current_segment)

    # Filter out segments that are too short
    filtered_segments = [
        seg for seg in segments
        if (seg['end_time'] - seg['start_time'] + 1) >= min_segment_duration
    ]

    print(f"Created {len(segments)} segments ({len(filtered_segments)} after filtering)")
    return filtered_segments


def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def save_segments_json(segments: List[Dict], output_path: Path):
    """Save segments to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(segments)} segments to {output_path}")


def print_segment_summary(segments: List[Dict]):
    """Print a human-readable summary of segments."""
    print("\n" + "=" * 80)
    print("SEGMENT SUMMARY")
    print("=" * 80)

    for seg in segments:
        duration = seg['end_time'] - seg['start_time'] + 1
        print(f"\nSegment {seg['segment_id']:3d}: "
              f"{format_timestamp(seg['start_time'])} --> {format_timestamp(seg['end_time'])} "
              f"({duration}s, {seg['frame_count']} frames)")
        print(f"  Representative: {seg['representative_frame']}")

    total_duration = sum(seg['end_time'] - seg['start_time'] + 1 for seg in segments)
    print("\n" + "=" * 80)
    print(f"Total segments: {len(segments)}")
    print(f"Total subtitle duration: {total_duration}s ({total_duration/60:.1f} minutes)")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Segment subtitle frames into groups with same text"
    )
    parser.add_argument(
        'video_id',
        help='Video identifier (e.g., "0-1", "1-2")'
    )
    parser.add_argument(
        '--frames-dir',
        type=Path,
        default=Path('step1-output/subtitle_frames_for_ocr'),
        help='Directory containing frame images (default: step1-output/subtitle_frames_for_ocr)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('step2-output/segments'),
        help='Output directory for segment JSON (default: step2-output/segments)'
    )
    parser.add_argument(
        '--diff-threshold',
        type=float,
        default=15.0,
        help='Pixel difference threshold for detecting subtitle changes (default: 15.0)'
    )
    parser.add_argument(
        '--blank-threshold',
        type=float,
        default=30.0,
        help='Threshold for detecting blank frames (default: 30.0)'
    )
    parser.add_argument(
        '--min-duration',
        type=int,
        default=1,
        help='Minimum segment duration in seconds (default: 1)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print detailed segment summary'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.frames_dir.exists():
        print(f"Error: Frames directory not found: {args.frames_dir}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Segment frames
    print(f"\nSegmenting frames for video: {args.video_id}")
    print(f"Frames directory: {args.frames_dir}")
    print(f"Difference threshold: {args.diff_threshold}")
    print(f"Blank threshold: {args.blank_threshold}")
    print(f"Min duration: {args.min_duration}s\n")

    segments = segment_frames(
        frames_dir=args.frames_dir,
        video_id=args.video_id,
        diff_threshold=args.diff_threshold,
        blank_threshold=args.blank_threshold,
        min_segment_duration=args.min_duration
    )

    # Save to JSON
    output_path = args.output_dir / f"{args.video_id}_segments.json"
    save_segments_json(segments, output_path)

    # Print summary if requested
    if args.summary:
        print_segment_summary(segments)
    else:
        print(f"\nCreated {len(segments)} segments")
        print(f"Use --summary flag to see detailed breakdown")


if __name__ == '__main__':
    main()
