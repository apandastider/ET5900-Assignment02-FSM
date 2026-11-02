# ET 5900: Student FSM implementation contract

**Goal:** Autonomous R1 red pick motion -> R2 red place motion -> G1 green pick motion -> G2 green place motion, while managing battery and charging at C1. The arm performs a demonstrative, collision-safe motion; no grasp/release or Gazebo attachment is required.

## Provided interfaces
- Nav2 action `/navigate_to_pose` (`nav2_msgs/action/NavigateToPose`).
- Arm action `/arm_controller/follow_joint_trajectory` (`control_msgs/action/FollowJointTrajectory`).
- Battery topic `/battery_state` (`sensor_msgs/BatteryState`, percentage in 0..1).
- Virtual charger command `/virtual_charger/docked` (`std_msgs/Bool`).
- Station candidate poses in `config/stations.yaml`; confirm verified goals with instructor.

## Student-owned intellectual work
1. FSM state inventory, transition diagram, transition guards and exception paths.
2. Asynchronous Nav2 action handling; success, cancel, abort, timeout.
3. Station arm action sequencing and completion checks.
4. Low battery detection (<=15%) with safe action preemption.
5. Checkpoint definition: current station, task phase, and whether operation finished.
6. Navigation to C1 and independent docking verification; do not publish `true` on arrival alone.
7. Charge until >=90%; stop charging; restore task and resume without skipping/duplicating steps.
8. Recovery cases: navigation unavailable, navigation failure, dock verification failure, interruption while arm action active, unexpected battery message.
9. Structured transition/event logging and a brief design justification.

Starter functions intentionally raise `NotImplementedError`; they are design prompts, not prebuilt solutions.

## Test evidence
Submit source, transition diagram, log showing 4 stations and arm actions, interruption at/below 15%, navigation to C1, verified charging, recovery at/above 90%, and resume at saved task stage. No physical object grasp evaluation.
