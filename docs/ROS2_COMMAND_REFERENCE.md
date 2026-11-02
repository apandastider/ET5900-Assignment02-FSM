# Student ROS 2 command reference — ET 5900

**Only in Gazebo.** All commands below describe the combined TurtleBot 4 Lite + SO-ARM101 setup used in the course; check the exact active endpoints before moving. Open terminals with:

```bash
source /opt/ros/jazzy/setup.bash
source ~/turtlebot4_ws/install/setup.bash
source ~/so101_jazzy_ws/install/setup.bash
source ~/et5900_release_test/install/setup.bash  # or your student build install/setup.bash
```

## 1. Start and inspect

Run each component in its own terminal (Gazebo → ROS/GZ bridge → AMCL → Nav2 → assignment infrastructure → RViz → battery → MoveIt), following `docs/STUDENT_INSTALLATION.md`. Verify:

```bash
ros2 control list_controllers
ros2 action list -t
ros2 topic list -t
ros2 topic info /diffdrive_controller/cmd_vel -v
ros2 topic info /arm_controller/joint_trajectory -v
ros2 topic info /gripper_controller/commands -v
```

The base controller here expects **geometry_msgs/msg/TwistStamped** at `/diffdrive_controller/cmd_vel`. The arm controller exposes a `FollowJointTrajectory` action and generally a `/arm_controller/joint_trajectory` input. Controller availability and topic type must be checked before publishing.

## 2. Manual base movement — topic publication

**Stop any active Nav2 goal and any teleoperation process first.** Use a clear Gazebo area, low speed, and Ctrl+C immediately if unexpected motion occurs. A stamped command is not an autonomous navigation goal.

```bash
ros2 topic pub -r 5 /diffdrive_controller/cmd_vel \
  geometry_msgs/msg/TwistStamped \
  "{header: {frame_id: base_link}, twist: {linear: {x: 0.05}, angular: {z: 0.0}}}"
```

Press `Ctrl+C` after a short test. Explicit stop:

```bash
ros2 topic pub --once /diffdrive_controller/cmd_vel \
  geometry_msgs/msg/TwistStamped \
  "{header: {frame_id: base_link}, twist: {linear: {x: 0.0}, angular: {z: 0.0}}}"
```

For rotation in place use `linear.x: 0.0`, `angular.z: 0.15`, and **stop afterward**. Some controllers reject stale timestamps; if motion does not occur, use the already-tested keyboard teleoperation below or publish continuously with freshly stamped messages from a Python node.

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p stamped:=true \
  -r cmd_vel:=/diffdrive_controller/cmd_vel
```

Do not publish commands in parallel with Nav2. The FSM should use Nav2 action goals for station-to-station travel rather than direct velocity publishing.

## 3. Manual arm motion — JointTrajectory topic

First verify `arm_controller` is active and `/arm_controller/joint_trajectory` accepts `trajectory_msgs/msg/JointTrajectory`. **Use only a pose independently checked in MoveIt and confirmed clear of tables**; the numerical example is illustrative, *not* a certified safe pose.

```bash
ros2 topic pub --once /arm_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: [so101_shoulder_pan, so101_shoulder_lift, so101_elbow_flex, so101_wrist_flex, so101_wrist_roll], points: [{positions: [0.15, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 3}}]}"
```

The preferred way for the FSM to receive acceptance and execution results is the **action**, not the raw topic:

```bash
ros2 action send_goal /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [so101_shoulder_pan, so101_shoulder_lift, so101_elbow_flex, so101_wrist_flex, so101_wrist_roll], points: [{positions: [0.15, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 3}}]}}" \
  --feedback
```

Check whether the controller result is successful before counting a station operation as complete. Direct trajectory actions/topics **do not replace MoveIt's collision planning**; students must discover safe station-specific configurations in the MoveIt MotionPlanning Joints tab.

## 4. Optional gripper test

No physical grasp is required for this assignment. The working gripper controller is separate:

```bash
ros2 topic info /gripper_controller/commands -v
# If type is std_msgs/msg/Float64MultiArray and clear of obstacles:
ros2 topic pub --once /gripper_controller/commands \
  std_msgs/msg/Float64MultiArray "{data: [0.0]}"
```

Confirm the current joint state and limit before commanding the gripper. This topic has no action completion result by itself.

## 5. Navigate using an action

Confirm AMCL pose and a collision-free map-frame goal in RViz before execution:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: -2.3, y: 0.0, z: 0.0}, orientation: {z: 1.0, w: 0.0}}}}" \
  --feedback
```

This is the previously tested C1 *navigation candidate*. Navigation success alone does **not** count as docking.

## 6. C1 docking: required student behavior

The delivered `week9_pick_place.sdf` has a **visual blue marker**, not a working physical dock. Students MUST explicitly implement a docking stage at C1 following their navigation action, verify final `map → base_link` distance/yaw and near-zero odometry velocity, then enable the virtual charger. Use the course thresholds if assigned (suggested position ≤0.12 m, yaw ≤15°). Do not mark docking based solely on having requested a C1 navigation goal.

The ROS 2 Nav2 `DockRobot` API is **only applicable if a docking server, dock plugin, and C1 dock entry are properly configured and tested**; the provided workcell does not establish these prerequisites. Check first:

```bash
ros2 action list -t | grep -E 'dock_robot|undock_robot'
ros2 node list | grep docking_server
```

If a real `/dock_robot` server is configured and C1 is registered with `dock_id: C1`, the action pattern is:

```bash
ros2 action send_goal /dock_robot nav2_msgs/action/DockRobot \
  "{use_dock_id: true, dock_id: C1, navigate_to_staging_pose: false}" --feedback
```

**Do not run that goal unless the server and the C1 dock configuration exist.** Students using the current visual-marker workcell should implement the verified virtual docking stage instead. For physical/plugin docking, also implement `UndockRobot` (use `ros2 interface show nav2_msgs/action/UndockRobot` for fields) before leaving C1.

## 7. Battery and manual virtual charging check

```bash
ros2 topic echo /battery_state --field percentage
ros2 topic info /virtual_charger/docked -v
# Only AFTER successful docking verification:
ros2 topic pub --once /virtual_charger/docked std_msgs/msg/Bool "{data: true}"
# At >=90%, before leaving C1:
ros2 topic pub --once /virtual_charger/docked std_msgs/msg/Bool "{data: false}"
```

The `/battery_state.percentage` field is in `[0,1]`. `0.15` is 15%; `0.90` is 90%. Students implement these decisions in code rather than manually publishing during the final demonstration.

## 8. ROS interfaces students should use

- `rclpy.action.ActionClient(NavigateToPose, '/navigate_to_pose')`
- `rclpy.action.ActionClient(FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')`
- `/battery_state` (`sensor_msgs/msg/BatteryState`)
- `/odom` (`nav_msgs/msg/Odometry`) and `tf2_ros` for final `map → base_link` pose
- `/virtual_charger/docked` (`std_msgs/msg/Bool`) only when safely docked
- `/fsm/status` (`std_msgs/msg/String`) for machine-readable state transitions

All requests should be asynchronous and handle goal acceptance, progress/results, cancellation and failure. The provided `student_fsm.py` intentionally does not implement any transition logic.
