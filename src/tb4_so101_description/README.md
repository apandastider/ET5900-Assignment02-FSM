# TurtleBot4 Lite + SO101 first-stage Gazebo visual preview

## Prerequisites
ROS 2 Jazzy + Gazebo Harmonic, `turtlebot4_gz_bringup`, `turtlebot4_description`, `so101_description`, `xacro`, `ros_gz_sim` must be available through sourced ROS environments.

## Install
Copy this folder into `~/turtlebot4_ws/src/`, then in the container:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ufactory_lite6_ws/install/setup.bash  # adjust if your real install prefix differs
cd ~/turtlebot4_ws
colcon build --symlink-install --packages-select tb4_so101_description
source install/setup.bash
```

## Validate before running
```bash
ros2 pkg prefix so101_description
ros2 pkg prefix turtlebot4_gz_bringup
xacro $(ros2 pkg prefix tb4_so101_description)/share/tb4_so101_description/urdf/tb4_so101.urdf.xacro gazebo:=ignition > /tmp/tb4_so101.urdf
check_urdf /tmp/tb4_so101.urdf
```

## Launch
```bash
ros2 launch tb4_so101_description tb4_so101_gazebo.launch.py world:=depot
```

**Limitations:** This is not a tested completed robot integration. Geometry clearances and SO101 orientation must be checked visually. The plate is 29 cm across, 1 cm thick, centered 19 cm above the base_link ground frame; arm attaches 5.5 cm above the plate frame. It is a prototype, not an engineering mounting dimension. The Gazebo-only launcher does not include the dock, Nav2, Create3 command bridges, or the arm's ROS 2 controllers. The arm's unactuated joints can droop under gravity; inspect model quickly or pause Gazebo for visual comparison. Later add SO101 ros2_control into a combined controller configuration, not a second conflicting control plugin. Do not run the normal `turtlebot4_gz.launch.py` simultaneously or you'll spawn a separate stock robot.
