# ET 5900 — Final Release Add-on (2 November 2026)

This add-on is intended to be copied **on top of** the existing `~/et5900-fsm-assignment` repository. It does NOT contain, overwrite, or reconstruct your tested `tb4_so101_description`, `tb4_so101_moveit_config`, final world/map, gripper patch, or virtual-battery implementation.

## Instructor: apply without touching original workspaces
```bash
unzip ET5900_RELEASE_FINAL_ADDON.zip -d /tmp/et5900-addon
cp -an /tmp/et5900-addon/. ~/et5900-fsm-assignment/
cd ~/et5900-fsm-assignment
bash scripts/release_preflight.sh
```
`cp -an` preserves any identically named files already present. These scripts only execute commands against existing ROS packages. The launcher has no code that changes the original source trees.

## Interactive startup, using instructor's proven ROS commands
```bash
cd ~/et5900-fsm-assignment
bash scripts/start_component.sh menu
```
Choose a component per terminal, in order: `gazebo`, `bridge`, `localization`, `navigation`, `infrastructure`, `rviz`, `battery`, then optionally `moveit`. **Do not run duplicates** of AMCL, Nav2 or velocity bridge. Set initial pose in RViz. The installed world and map must match the current tested machine.

## Student distribution
Use this repository together with the existing `src/` packages, actual `maps/` and `worlds/` assets, and `patches/so101_gripper_dynamics.patch`. Follow `docs/STUDENT_INSTALLATION.md` and `docs/STUDENT_ASSIGNMENT_FINAL.md`. Do not publish `docs/INSTRUCTOR_ACCEPTANCE.md` if you want instructor-only test details private.

## Known limits
- A clean rebuild and isolated runtime have been instructor-tested, but **new wrapper scripts and fresh student-machine installation have not yet been validated**.
- The station values supplied in `src/tb4_fsm_assignment/config/stations.yaml` are candidates until verified from the actual successful goal logs. Do not mark them verified merely because C1 succeeded.
- Student FSM intentionally has no complete task orchestration, preemption or charging logic.
- Reference world packaged earlier is NOT a substitute for your locally verified world.
