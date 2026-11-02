# ET 5900 — Multi-robot workflow FSM, instructor bundle

This release is an **infrastructure + incomplete student FSM starter**, not a solution. It assumes the separately tested TurtleBot4+SO101 world, ROS 2 Jazzy workspace, robot controllers, saved map and virtual battery package.

## Layout
- `tb4_fsm_assignment/`: ready-to-build ROS 2 `ament_python` package containing the tested-message-type velocity bridge, station RViz labels and intentionally incomplete FSM.
- `tb4_virtual_battery/`: existing standalone student battery simulator with its own tests.
- `week9_pick_place.sdf`: uploaded SDF workcell sample; compare with installed working world.
- `RUNBOOK_INSTRUCTOR.md`: terminal-by-terminal exact startup sequence, verification and troubleshooting.
- `GITHUB_RELEASE_CHECKLIST.md`: publishing and dependency checks.

**Critical:** Copy your actual saved `week9_pick_place.yaml` + `.pgm` into `tb4_fsm_assignment/maps/` and replace the station pose placeholders with the *verified map-frame poses*. Those local files were never available here. No simulation integration execution was possible in this environment; test on Ubuntu before release.
