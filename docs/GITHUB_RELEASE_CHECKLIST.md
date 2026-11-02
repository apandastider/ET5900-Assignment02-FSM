# Pre-release and GitHub checklist

1. Copy the verified occupancy `.yaml` + `.pgm` into `tb4_fsm_assignment/maps/`; verify YAML image relative path and map-frame origin.
2. Compare included `week9_pick_place.sdf` to working installed workcell and use the truly tested version.
3. Fill `config/stations.yaml` with five actual successful robot CENTER poses and yaw, mark `verified: true`. Avoid treating visual mat centers as guaranteed safe.
4. Record four collision-free arm motions in `config/arm_poses_TEMPLATE.yaml`; do not require grasp or object attachment.
5. Ensure one single final Nav2 Twist -> diffdrive TwistStamped bridge; retire the ad-hoc standalone bridge.
6. Confirm students have original `tb4_so101_description`, `so101_description`, `turtlebot4_*` Gazebo packages; this bundle does not repackage those sources.
7. Build `colcon build --packages-select tb4_virtual_battery tb4_fsm_assignment --symlink-install` on Ubuntu 24.04/Jazzy.
8. Run `python3 -m pytest -q tb4_fsm_assignment/test` and `python3 -m pytest -q tb4_virtual_battery/test`.
9. Test `ros2 launch tb4_fsm_assignment infrastructure.launch.py`; verify RViz station markers and bridge. Verify map, localization, Nav2, battery, C1 manual charge.
10. Document which packages are student prerequisites and explicit course policy for AI use/code disclosure.
11. Keep an instructor-only full FSM solution/test harness in a separate private repository; don't publish it with the scaffold.
12. After check: `git init && git add . && git commit -m 'ET5900 FSM scaffold and instructor runbook'` then `gh repo create et5900-fsm-assignment --private --source=. --remote=origin --push` (instructor may change visibility deliberately).

Do not commit secrets, machine login credentials, IP addresses, or locally generated maps with sensitive facility layouts unless authorized for distribution.
