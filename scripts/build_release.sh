#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="${1:-$HOME/et5900_release_test}"
if [[ "$WS" == "$HOME/turtlebot4_ws" || "$WS" == "$HOME/tb4_so101_ws" || "$WS" == "$HOME/so101_jazzy_ws" ]]; then
 echo 'Refusing to rebuild original working workspace';exit 2
fi
mkdir -p "$WS/src"
for pkg in tb4_so101_description tb4_so101_moveit_config tb4_virtual_battery tb4_fsm_assignment;do
 [[ -d "$ROOT/src/$pkg" ]] || { echo "Missing $pkg";exit 1; }
 if [[ ! -e "$WS/src/$pkg" ]]; then cp -a "$ROOT/src/$pkg" "$WS/src/";else echo "Exists; not overwriting: $WS/src/$pkg";fi
done
source /opt/ros/jazzy/setup.bash
for s in "$HOME/turtlebot4_ws/install/setup.bash" "$HOME/so101_jazzy_ws/install/setup.bash";do [[ ! -f "$s" ]] || source "$s";done
(cd "$WS" && colcon build --symlink-install --packages-up-to tb4_so101_description tb4_so101_moveit_config tb4_virtual_battery tb4_fsm_assignment)
echo "Build finished. In each terminal, source $WS/install/setup.bash"
