#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-$HOME/et5900-fsm-assignment}"
mkdir -p "$DEST/maps" "$DEST/worlds" "$DEST/patches" "$DEST/src/tb4_fsm_assignment/maps"
for ext in yaml pgm; do
 map="$HOME/turtlebot4_ws/maps/week9_pick_place.$ext"
 if [[ -f "$map" ]]; then
   cp "$map" "$DEST/maps/"
   cp "$map" "$DEST/src/tb4_fsm_assignment/maps/"
   echo "Copied real map $map"
 else
   echo "MISSING real map $map"
 fi
done
SO="$HOME/so101_jazzy_ws/src/so101_ros2"
if [[ -d "$SO/.git" ]]; then
 (cd "$SO" && git diff -- so101_description/urdf/so101_robot.urdf.xacro) > "$DEST/patches/so101_gripper_dynamics.patch"
 if [[ -s "$DEST/patches/so101_gripper_dynamics.patch" ]]; then
   echo "Saved local SO-ARM101 Xacro patch"
 else
   echo "WARNING: SO-ARM101 patch empty; the local change may have been committed or removed"
 fi
 (cd "$SO" && git remote -v && git rev-parse HEAD && git status --short)
else echo "SO-ARM101 work tree not found at $SO"; fi
printf '\nCandidate local worlds (choose the exact WORKING one):\n'
find "$HOME/turtlebot4_ws/src" "$HOME/tb4_so101_ws/src" -type f -name 'week9_pick_place.sdf' -print 2>/dev/null || true
printf '\nCopy your VERIFIED world manually, e.g.:\n cp /actual/path/week9_pick_place.sdf "%s/worlds/week9_pick_place.sdf"\n' "$DEST"
printf '\nDo not overwrite working tb4_so101_description or tb4_so101_moveit_config.\n'
