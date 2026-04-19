#!/bin/bash
# Renames _MG_*.jpg files to IMG_*.jpg to avoid Jekyll ignoring underscore-prefixed files.
# Run this script on any server/machine that holds the source assets.

for f in \
  "projects/savior/_MG_6105.jpg" \
  "projects/savior/_MG_6105_med.jpg" \
  "projects/butoh/_MG_6415.jpg" \
  "projects/butoh/_MG_6265.jpg" \
  "projects/butoh/_MG_6455.jpg" \
  "projects/butoh/_MG_6286.jpg" \
  "projects/butoh/_MG_6387.jpg" \
  "projects/butoh/_MG_6397.jpg"
do
  dir=$(dirname "$f")
  base=$(basename "$f")
  newbase="${base/#_MG_/IMG_}"
  mv "$f" "$dir/$newbase"
  echo "Renamed $f -> $dir/$newbase"
done
