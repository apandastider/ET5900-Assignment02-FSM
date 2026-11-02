#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-$HOME/et5900-fsm-assignment}"
for pkg in tb4_so101_description tb4_so101_moveit_config tb4_virtual_battery tb4_fsm_assignment; do
 [[ -f "$DEST/src/$pkg/package.xml" ]] && echo "OK package $pkg" || echo "MISSING package $pkg"
done
for f in maps/week9_pick_place.yaml maps/week9_pick_place.pgm worlds/week9_pick_place.sdf patches/so101_gripper_dynamics.patch; do
 [[ -s "$DEST/$f" ]] && echo "OK $f" || echo "MISSING/EMPTY $f"
done
python3 -m compileall -q "$DEST/src/tb4_fsm_assignment" "$DEST/src/tb4_virtual_battery"
echo "Python syntax checked; not a Gazebo/ROS integration test"
