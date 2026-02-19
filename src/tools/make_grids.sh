#!/bin/bash
# Create grid composites for a given video prefix
# Usage: ./make_grids.sh <prefix> <total_frames> <frames_dir>
# Supports both %03d and %04d frame naming

PREFIX="$1"
TOTAL="$2"
FDIR="${3:?Usage: $0 <prefix> <total_frames> <frames_dir>}"
BATCH=10
GRID_NUM=1

# Detect naming pattern: check if %04d files exist
if [ -f "${FDIR}/${PREFIX}_0001.jpg" ]; then
  FMT="%04d"
elif [ -f "${FDIR}/${PREFIX}_001.jpg" ]; then
  FMT="%03d"
else
  echo "No frames found for ${PREFIX}"
  exit 1
fi

# Detect grid naming: use %03d if >99 grids possible
TOTAL_GRIDS=$(( (TOTAL + BATCH - 1) / BATCH ))
if [ "$TOTAL_GRIDS" -gt 99 ]; then
  GRID_FMT="%03d"
else
  GRID_FMT="%02d"
fi

i=1
while [ $i -le $TOTAL ]; do
  END=$((i + BATCH - 1))
  if [ $END -gt $TOTAL ]; then
    END=$TOTAL
  fi
  COUNT=$((END - i + 1))

  # Build input args
  INPUTS=""
  for j in $(seq $i $END); do
    INPUTS="$INPUTS -i ${FDIR}/${PREFIX}_$(printf "$FMT" $j).jpg"
  done

  # Build filter
  FILTER=""
  for k in $(seq 0 $((COUNT - 1))); do
    FILTER="${FILTER}[$k]"
  done
  FILTER="${FILTER}vstack=inputs=${COUNT}"

  ffmpeg -y $INPUTS -filter_complex "$FILTER" -q:v 2 "${FDIR}/${PREFIX}_grid_$(printf "$GRID_FMT" $GRID_NUM).jpg" 2>/dev/null

  GRID_NUM=$((GRID_NUM + 1))
  i=$((END + 1))
done

echo "Created $((GRID_NUM - 1)) grids for ${PREFIX}"
