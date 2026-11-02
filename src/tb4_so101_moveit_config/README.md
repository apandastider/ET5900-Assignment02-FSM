# TurtleBot 4 Lite + SO-ARM101 — MoveIt 2 (ROS 2 Jazzy)

This package ONLY runs `move_group` and RViz. It does not spawn the robot, run Gazebo, publish duplicate TF, or start controllers. The combined robot and its four controllers must already be running.

## Install on Ubuntu host

Unzip `tb4_so101_moveit_config` into `~/turtlebot4_ws/src/`.

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4_ws/install/setup.bash
source ~/ufactory_lite6_ws/install/setup.bash
source ~/tb4_so101_host_install/local_setup.bash
cd ~/turtlebot4_ws
colcon --log-base ~/tb4_so101_moveit_log build \
  --symlink-install \
  --build-base ~/tb4_so101_moveit_build \
  --install-base ~/tb4_so101_moveit_install \
  --packages-select tb4_so101_moveit_config
source ~/tb4_so101_moveit_install/local_setup.bash
```

## Launch order

Terminal 1: launch your working `tb4_so101_gazebo.launch.py` (with automatic controllers).

Terminal 2: optionally start the separate TurtleBot 4 sensor bridge.

Terminal 3:
```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4_ws/install/setup.bash
source ~/ufactory_lite6_ws/install/setup.bash
source ~/tb4_so101_host_install/local_setup.bash
source ~/tb4_so101_moveit_install/local_setup.bash
ros2 control list_controllers
ros2 action list -t | grep follow_joint_trajectory
ros2 launch tb4_so101_moveit_config moveit.launch.py
```

In RViz set Fixed Frame to `base_link`, Add > MotionPlanning display, choose planning group `arm`, use joint-space goals first, Plan then Execute.

## Notes

- Generates arm SRDF at launch from the real combined Xacro; the five-joint chain ends at the link attached by `so101_wrist_roll`.
- Keeps robot mobile base fixed during arm planning/execution (do not drive during a MoveIt plan).
- Only arm group is executed by MoveIt; gripper remains on `/gripper_controller/commands`.
- Position-only KDL IK is a starting point; exact full 6-DOF Cartesian pose constraints are infeasible for a five-DOF arm.
- Only directly adjacent links are disabled from collision checks; inspect self-collision before planning.
- If RViz starts empty, set fixed frame `base_link` and add the MotionPlanning display manually.
- Do not use the standalone SO101 MoveIt launch for this combined robot: it has different URDF/joint names.
- Check and match `/robot_description` Gazebo URDF and MoveIt Xacro; changes to the combined model require restarting Gazebo and MoveIt.
