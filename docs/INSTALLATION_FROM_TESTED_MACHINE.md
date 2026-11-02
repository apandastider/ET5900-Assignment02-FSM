# Installation and build notes

## Tested machine source inventory

Keep these directories **as-is**:

- `~/tb4_so101_ws/src/tb4_so101_description` → `~/et5900-fsm-assignment/src/`
- `~/tb4_so101_ws/src/tb4_so101_moveit_config` → `~/et5900-fsm-assignment/src/`
- `~/turtlebot4_ws/maps/week9_pick_place.yaml` and `.pgm` → repository `maps/` and FSM package `maps/`
- Working `week9_pick_place.sdf` → repository `worlds/`
- Git diff of local SO-ARM101 URDF Xacro → `patches/so101_gripper_dynamics.patch`

## Upstream SO-ARM101

```bash
mkdir -p ~/so101_jazzy_ws/src
cd ~/so101_jazzy_ws/src
git clone https://github.com/adoodevv/so101_ros2.git
cd so101_ros2
git checkout 3fb5182614b8e672ab8784b2a10b50656f976c9c
git apply ~/et5900-fsm-assignment/patches/so101_gripper_dynamics.patch
cd ~/so101_jazzy_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

The git patch command is for a fresh clone, NOT for the already modified instructor working tree.

## Source packages

Do not delete your working ROS workspaces. For a clean student workspace, prefer to put all custom packages under one `src` after installing SO-101 and TurtleBot dependencies; adjust the source order according to your verified setup. The prepared `tb4_fsm_assignment` package provides `nav2_twist_bridge`, `station_markers`, and an intentionally incomplete `student_fsm`. Its `infrastructure.launch.py` starts the bridge and station markers only; Gazebo, bridge sensors, AMCL, Nav2 and MoveIt must be launched separately.

## Critical release checks

- Inspect local modifications and package dependencies with `ros2 pkg list` and `rosdep`.
- Make Gazebo world resolution point to installed assignment world or document tested world install location; DO NOT assume this has already been integrated.
- Record safe robot-center navigation goal poses in `src/tb4_fsm_assignment/config/stations.yaml`.
- Check that the virtual battery has only one publisher on `/battery_state`.
- Stop any duplicate velocity bridge before running new bridge.
- Students select safe arm poses using MoveIt 2 Joints tab and prove collision-free planning/execution; direct trajectory goals do not collision-check.
