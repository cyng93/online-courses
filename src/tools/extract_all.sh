#!/bin/bash
# Extract subtitle frames (1fps) and create grid composites for all videos
# Uses dynamic crop based on course config via course.json
#
# Usage: ./extract_all.sh /path/to/course-dir
#   e.g. ./extract_all.sh /path/to/break-inner-conflict-loop
#
# Requires: ffmpeg, python3 (for JSON parsing)

set -euo pipefail

COURSE_DIR="${1:?Usage: $0 /path/to/course-dir}"
COURSE_DIR="$(cd "$COURSE_DIR" && pwd)"  # resolve to absolute path

CONFIG="$COURSE_DIR/course.json"
if [ ! -f "$CONFIG" ]; then
  echo "ERROR: course.json not found at $CONFIG"
  exit 1
fi

VIDDIR="$COURSE_DIR/step0-input"
FDIR="$COURSE_DIR/step1-output/subtitle_frames_for_ocr"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GRIDSCRIPT="$SCRIPT_DIR/make_grids.sh"

mkdir -p "$FDIR"

# Read crop params from config
CROP_H=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['crop']['height'])")
SCALE_W=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['crop']['scale_width'])")
SCALE_H=$(python3 -c "import json; c=json.load(open('$CONFIG')); print(c['crop']['scale_height'])")

echo "Course dir: $COURSE_DIR"
echo "Crop: bottom ${CROP_H}px, scale to ${SCALE_W}x${SCALE_H}"
echo ""

# Read video list from config as tab-separated: id\tfilename
VIDEO_LIST=$(python3 -c "
import json
c = json.load(open('$CONFIG'))
for v in c['videos']:
    print(v['id'] + '\t' + v['filename'])
")

TOTAL_VIDEOS=0
ALL_PREFIXES=""

process_video() {
  local PREFIX="$1"
  local FILENAME="$2"

  if [ ! -f "$VIDDIR/$FILENAME" ]; then
    echo "[$PREFIX] WARNING: File not found: $FILENAME"
    echo "---"
    return
  fi

  # Check if frames already exist
  local EXISTING
  EXISTING=$(ls "$FDIR"/${PREFIX}_[0-9][0-9][0-9].jpg "$FDIR"/${PREFIX}_[0-9][0-9][0-9][0-9].jpg 2>/dev/null | wc -l | tr -d ' ')
  if [ "$EXISTING" -gt 0 ]; then
    echo "[$PREFIX] $EXISTING frames already exist, skipping extraction."
  else
    echo "[$PREFIX] Extracting frames from: $FILENAME ..."
    # Use dynamic crop: crop bottom N px of whatever the video size is
    ffmpeg -y -i "$VIDDIR/$FILENAME" \
      -vf "fps=1,crop=iw:${CROP_H}:0:ih-${CROP_H},scale=${SCALE_W}:${SCALE_H}" \
      -q:v 2 "$FDIR/${PREFIX}_%04d.jpg" 2>/dev/null
    EXISTING=$(ls "$FDIR"/${PREFIX}_[0-9][0-9][0-9][0-9].jpg 2>/dev/null | wc -l | tr -d ' ')
    echo "[$PREFIX] Extracted $EXISTING frames."
  fi

  # Check if grids already exist
  local GRID_EXISTING
  GRID_EXISTING=$(ls "$FDIR"/${PREFIX}_grid_[0-9][0-9].jpg "$FDIR"/${PREFIX}_grid_[0-9][0-9][0-9].jpg 2>/dev/null | wc -l | tr -d ' ')
  if [ "$GRID_EXISTING" -gt 0 ]; then
    echo "[$PREFIX] $GRID_EXISTING grids already exist, skipping grid creation."
  else
    echo "[$PREFIX] Creating grids ($EXISTING frames)..."
    bash "$GRIDSCRIPT" "$PREFIX" "$EXISTING" "$FDIR"
    GRID_EXISTING=$(ls "$FDIR"/${PREFIX}_grid_[0-9][0-9].jpg "$FDIR"/${PREFIX}_grid_[0-9][0-9][0-9].jpg 2>/dev/null | wc -l | tr -d ' ')
    echo "[$PREFIX] Created $GRID_EXISTING grids."
  fi

  echo "[$PREFIX] DONE. Frames=$EXISTING, Grids=$GRID_EXISTING"
  echo "---"
}

# Process each video from config
while IFS=$'\t' read -r PREFIX FILENAME; do
  process_video "$PREFIX" "$FILENAME"
  TOTAL_VIDEOS=$((TOTAL_VIDEOS + 1))
  ALL_PREFIXES="$ALL_PREFIXES $PREFIX"
done <<< "$VIDEO_LIST"

echo ""
echo "========================================="
echo "ALL $TOTAL_VIDEOS VIDEOS PROCESSED"
echo "========================================="
echo ""
echo "Summary:"
for PREFIX in $ALL_PREFIXES; do
  FRAMES=$(ls "$FDIR"/${PREFIX}_[0-9][0-9][0-9].jpg "$FDIR"/${PREFIX}_[0-9][0-9][0-9][0-9].jpg 2>/dev/null | wc -l | tr -d ' ')
  GRIDS=$(ls "$FDIR"/${PREFIX}_grid_[0-9][0-9].jpg "$FDIR"/${PREFIX}_grid_[0-9][0-9][0-9].jpg 2>/dev/null | wc -l | tr -d ' ')
  echo "  $PREFIX: $FRAMES frames, $GRIDS grids"
done
