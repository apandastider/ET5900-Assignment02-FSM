#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0
for pkg in tb4_so101_description tb4_so101_moveit_config tb4_virtual_battery tb4_fsm_assignment; do
  if [[ -s "$ROOT/src/$pkg/package.xml" ]]; then echo "OK $pkg"; else echo "MISSING src/$pkg"; fail=1; fi
done
for asset in maps/week9_pick_place.yaml maps/week9_pick_place.pgm worlds/week9_pick_place.sdf patches/so101_gripper_dynamics.patch; do
 if [[ -s "$ROOT/$asset" ]]; then echo "OK $asset"; else echo "MISSING $asset";fail=1;fi
done
if [[ -f "$ROOT/maps/week9_pick_place.yaml" ]]; then
 echo 'Map image entry:';grep -E '^image:' "$ROOT/maps/week9_pick_place.yaml" || { echo 'WARNING map YAML missing image key';fail=1; }
fi
if [[ -f "$ROOT/src/tb4_fsm_assignment/config/stations.yaml" ]]; then
 echo 'Station verified flags (must reflect observed navigation runs):'
 grep -E '  (R1|R2|G1|G2|C1):' "$ROOT/src/tb4_fsm_assignment/config/stations.yaml" || true
fi
if [[ $fail -ne 0 ]]; then echo 'PRE-FLIGHT FAILED';exit 1;fi
echo 'FILE PRE-FLIGHT PASSED. Does not establish ROS runtime or new-machine compatibility.'
