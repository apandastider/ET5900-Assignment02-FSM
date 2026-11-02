#!/usr/bin/env bash
set -eo pipefail
# Usage: bash scripts/start_component.sh gazebo|bridge|localization|navigation|infrastructure|rviz|battery|moveit|menu
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/jazzy/setup.bash
# Prefer the standalone release installation, fall back to the original custom-workspace installation.
for setup in "$HOME/turtlebot4_ws/install/setup.bash" "$HOME/so101_jazzy_ws/install/setup.bash" "$HOME/et5900_release_test/install/setup.bash";do
 [[ ! -f "$setup" ]] || source "$setup"
done
if ! ros2 pkg prefix tb4_so101_description >/dev/null 2>&1 && [[ -f "$HOME/tb4_so101_ws/install/setup.bash" ]]; then
 source "$HOME/tb4_so101_ws/install/setup.bash"
fi
component="${1:-menu}"
if [[ "$component" == menu ]];then
 printf '\nOpen one terminal per component; Ctrl+C stops that component.\n'
 printf '1 gazebo\n2 bridge\n3 localization\n4 navigation\n5 infrastructure\n6 rviz\n7 battery\n8 moveit\n'
 read -r -p 'Choose [1-8]: ' choice
 case "$choice" in 1)component=gazebo;;2)component=bridge;;3)component=localization;;4)component=navigation;;5)component=infrastructure;;6)component=rviz;;7)component=battery;;8)component=moveit;;*) echo 'Invalid selection';exit 2;;esac
fi
case "$component" in
 gazebo)
   echo 'Starting Gazebo. The world must already be installed where the tested launch can find it.'
   exec ros2 launch tb4_so101_description tb4_so101_gazebo.launch.py world:=week9_pick_place ;;
 bridge)
   exec ros2 launch turtlebot4_gz_bringup ros_gz_bridge.launch.py model:=lite robot_name:=turtlebot4_so101 world:=week9_pick_place ;;
 localization)
   MAP="$ROOT/maps/week9_pick_place.yaml"
   [[ -s "$MAP" ]] || { echo "Missing map: $MAP";exit 1; }
   exec ros2 launch nav2_bringup localization_launch.py "map:=$MAP" use_sim_time:=True autostart:=True ;;
 navigation)
   exec ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True autostart:=True use_composition:=False ;;
 infrastructure)
   echo 'Do not run the old standalone nav2_twist_bridge simultaneously.'
   exec ros2 launch tb4_fsm_assignment infrastructure.launch.py ;;
 rviz)
   RVIZ_CONFIG="$(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz"
   exec rviz2 -d "$RVIZ_CONFIG" --ros-args -p use_sim_time:=true ;;
 battery)
   exec ros2 run tb4_virtual_battery battery_sim --ros-args -p use_sim_time:=true -p initial_percent:=16.0 -p idle_drain_percent_per_min:=6.0 -p moving_drain_percent_per_min:=12.0 -p charge_percent_per_min:=60.0 ;;
 moveit)
   exec ros2 launch tb4_so101_moveit_config moveit.launch.py ;;
 *)echo "Unknown component: $component";exit 2;;
esac
