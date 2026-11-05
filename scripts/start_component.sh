#!/usr/bin/env bash
# ET 5900 Assignment 02 — start one ROS 2 component per terminal.
# Usage: bash scripts/start_component.sh [gazebo|bridge|localization|navigation|infrastructure|rviz|battery|moveit|menu]
set -eo pipefail

# Find the cloned repository, independent of the current working directory.
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
WORLD_FILE="$ROOT/worlds/week9_pick_place.sdf"
MAP_FILE="$ROOT/maps/week9_pick_place.yaml"
WORLD_NAME="week9_pick_place"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

# Follow docs/STUDENT_INSTALLATION.md exactly:
# repository clone: ~/et5900-fsm-assignment
# built ROS packages: ~/et5900_student_ws/src
STUDENT_WS="$HOME/et5900_student_ws"

[[ -f /opt/ros/jazzy/setup.bash ]] || fail 'ROS 2 Jazzy not found.'
source /opt/ros/jazzy/setup.bash

# TurtleBot 4 and SO-ARM101 are installed separately as prerequisites.
for dependency in turtlebot4_ws so101_jazzy_ws; do
  setup="$HOME/$dependency/install/setup.bash"
  [[ -f "$setup" ]] || fail "Missing prerequisite: $setup. Follow docs/STUDENT_INSTALLATION.md."
  source "$setup"
done

[[ -f "$STUDENT_WS/install/setup.bash" ]] || fail \
  "Missing $STUDENT_WS/install/setup.bash. Build the student workspace as instructed first."
source "$STUDENT_WS/install/setup.bash"

# Require the package to resolve from the student's built workspace,
# not a similarly named package in an old instructor workspace.
actual_prefix="$(ros2 pkg prefix tb4_so101_description 2>/dev/null || true)"
case "$actual_prefix" in
  "$STUDENT_WS/install/tb4_so101_description"|"$STUDENT_WS/install") ;;
  *) fail "Incorrect tb4_so101_description package: ${actual_prefix:-not found}. Expected $STUDENT_WS/install." ;;
esac

component="${1:-menu}"
if [[ "$component" == menu ]]; then
  printf '\nET 5900 Assignment 02 — start ONE component per terminal.\n'
  printf 'Keep previously started components running; Ctrl+C stops this one.\n\n'
  printf '1 gazebo\n2 bridge\n3 localization\n4 navigation\n5 infrastructure\n6 rviz\n7 battery\n8 moveit (optional)\n'
  read -r -p 'Choose [1-8]: ' choice
  case "$choice" in
    1) component=gazebo ;;
    2) component=bridge ;;
    3) component=localization ;;
    4) component=navigation ;;
    5) component=infrastructure ;;
    6) component=rviz ;;
    7) component=battery ;;
    8) component=moveit ;;
    *) fail "Invalid selection: $choice" ;;
  esac
fi

case "$component" in
  gazebo)
    [[ -s "$WORLD_FILE" ]] || fail "Missing GitHub world: $WORLD_FILE"
    # TurtleBot 4's sim.launch.py appends .sdf itself. NEVER pass .sdf here.
    echo "Starting Gazebo using: $WORLD_FILE"
    exec ros2 launch tb4_so101_description tb4_so101_gazebo.launch.py \
      "world:=${WORLD_FILE%.sdf}"
    ;;
  bridge)
    exec ros2 launch turtlebot4_gz_bringup ros_gz_bridge.launch.py \
      model:=lite robot_name:=turtlebot4_so101 "world:=$WORLD_NAME"
    ;;
  localization)
    [[ -s "$MAP_FILE" ]] || fail "Missing map: $MAP_FILE"
    exec ros2 launch nav2_bringup localization_launch.py \
      "map:=$MAP_FILE" use_sim_time:=True autostart:=True
    ;;
  navigation)
    exec ros2 launch nav2_bringup navigation_launch.py \
      use_sim_time:=True autostart:=True use_composition:=False
    ;;
  infrastructure)
    echo 'Do not start a second standalone nav2_twist_bridge.'
    exec ros2 launch tb4_fsm_assignment infrastructure.launch.py
    ;;
  rviz)
    rviz_config="$(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz"
    [[ -f "$rviz_config" ]] || fail "Missing RViz configuration: $rviz_config"
    exec rviz2 -d "$rviz_config" --ros-args -p use_sim_time:=true
    ;;
  battery)
    exec ros2 run tb4_virtual_battery battery_sim --ros-args \
      -p use_sim_time:=true \
      -p initial_percent:=16.0 \
      -p idle_drain_percent_per_min:=6.0 \
      -p moving_drain_percent_per_min:=12.0 \
      -p charge_percent_per_min:=60.0
    ;;
  moveit)
    exec ros2 launch tb4_so101_moveit_config moveit.launch.py
    ;;
  *) fail "Unknown component: $component" ;;
esac
