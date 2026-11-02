# TB4 virtual battery — student infrastructure (ROS 2 Jazzy)

Publishes `sensor_msgs/msg/BatteryState` on `/battery_state`. `percentage` ranges from **0.0 to 1.0**, so 15% is `0.15`. Subscribes to `/odom` to detect motion and `/virtual_charger/docked` (`std_msgs/msg/Bool`) to toggle virtual charging. The latter is **not evidence of physical docking**; students should only publish `true` after their navigation/docking success condition, and `false` when leaving.

This package intentionally **does not provide** a coordinator, FSM, Nav2 action client, docking detector, or task checkpoint/resume code. Students must implement these in their own packages.

## Install

Extract the zip. Place its `tb4_virtual_battery` directory inside `~/turtlebot4_ws/src/` (or another colcon workspace `src/`).

```bash
source /opt/ros/jazzy/setup.bash
cd ~/turtlebot4_ws
colcon build --packages-select tb4_virtual_battery --symlink-install
source install/setup.bash
ros2 pkg executables tb4_virtual_battery
```

## Run fast demonstration (no Nav2 required)

```bash
ros2 run tb4_virtual_battery battery_sim --ros-args -p use_sim_time:=true -p initial_percent:=16.0 -p moving_drain_percent_per_min:=60.0 -p charge_percent_per_min:=120.0
```

Run in a separate terminal:

```bash
ros2 topic echo /battery_state --field percentage
ros2 topic pub --once /virtual_charger/docked std_msgs/msg/Bool '{data: true}'
ros2 topic pub --once /virtual_charger/docked std_msgs/msg/Bool '{data: false}'
```

If `use_sim_time:=true`, Gazebo must be running and `/clock` advancing, otherwise the battery timer does not tick. In the fast demo, moving drain still depends on `/odom`. Idle drain defaults to 0.03%/min. To test without a robot, provide `-p idle_drain_percent_per_min:=60.0` instead.

For class demonstrations, a single `--once` charge message latches charging internally until another command arrives. This intentionally simple interface is a virtual charger switch, **not a secure or physical docking sensor**.

## Tests

```bash
cd ~/turtlebot4_ws/src/tb4_virtual_battery
python3 -m pytest -q test/test_battery_math.py
```

## FSM contract

At `percentage <= 0.15`, save progress, cancel or pause current task and navigate to the blue charging waypoint. Start virtual charging **only after verified docking**. At `percentage >= 0.90`, publish `false`, undock/depart, and resume from the saved checkpoint. Add failure/retry/recovery states. The workcell visual blue marker is not a real dock. Verify dock pose in the navigation map before commanding Nav2.

## Troubleshooting

- `ros2 topic info /battery_state -v` confirms exactly which simulator publishes it; avoid competing publishers from the TurtleBot's own battery driver / bridges. If another publisher exists, use a renamed topic for this lab and change student subscriptions accordingly.
- If battery percentage is frozen, check `/clock`, `/odom`, and `use_sim_time`.
- Keep only one `battery_sim` node per robot/namespace, with an appropriately namespaced battery and charger topic for multiple robots.
- This version uses a fixed 1-s timer period in simulated time; it is intended for assignment control logic, not physical battery or electrochemical modeling.
