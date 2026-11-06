# ET 5900 — Assignment: Event-driven manufacturing mission with fault recovery

**Environment:** ROS 2 Jazzy, Gazebo, one combined TurtleBot 4 Lite + SO-ARM101 mobile manipulator.

## Scenario and objective
Create a robust autonomous manufacturing workflow with four operations in strict order:

**R1 red pickup simulation → R2 red placement simulation → G1 green pickup simulation → G2 green placement simulation → MISSION_COMPLETE.**

At every station, the base navigates using Nav2, stops, and executes an independently selected and collision-checked SO-ARM101 trajectory with MoveIt 2. No physical box grasp/release is required. Students select joint targets from the MoveIt Joints tab and must show plan/execute results.

## Functional requirements
1. Create and implement a finite-state machine or hierarchical FSM. Show state graph, transitions, guard conditions, and entry/exit actions. Do not simply use a blocking sequence of sleeps.
2. Use ROS 2 NavigateToPose actions asynchronously; check goal acceptance, result code, timeouts, failure and cancellation. Do not advance to a station motion until navigation succeeds.
3. Plan and execute four station-specific arm motions using MoveIt 2. Verify joint feasibility at each station. Store and justify selected joint vectors. Report joint, planning and result information.
4. Monitor `/battery_state.percentage` continuously (fraction [0,1]). At ≤15% during mission, safely interrupt the ongoing operation, record a checkpoint specifying current station AND phase, and travel to C1.
5. **Dock at C1 (mandatory).** After navigating to a safe C1 staging/approach pose, perform an explicit docking step. For the supplied visual-marker workcell use a verified *virtual docking maneuver/confirmation* (final map-frame position, heading, stopped odometry, action success). A real Nav2 `DockRobot` action is required only in an environment where the docking server and C1 dock plugin/database are actually configured; do not invent a working dock server. Show docking evidence in the demonstration.
6. Begin charging by publishing `/virtual_charger/docked = true` only after verifying a successful C1 navigation result, robot position/yaw, and stopped velocity independently. The blue SDF marker is not a physical charger.
7. At ≥90%, publish `/virtual_charger/docked = false`, return to the correct task context, and resume without silently skipping or duplicating a completed operation. Document explicitly how in-progress arm motions are handled safely.
8. Support timeouts, bounded retries, and a safe abort. Failure should not lead to automatic erroneous charging or mission completion.
9. All motion must obey workstation and table collision constraints. Test inside Gazebo only.

## Student-provided design details
The repository provides controllers, Nav2 bridge, simulation, battery model, candidate station metadata, and an incomplete FSM skeleton. Students implement transition dispatch, Nav2 and MoveIt action orchestration, charge interruption, checkpoint semantics, dock verification, resumption, recovery, and tests. Instructor will not provide a working reference FSM.

## Demonstration scenarios
- Normal 4-station mission with trajectory execution feedback.
- Low-battery trigger while traveling to a station; after recharge resume the correct interrupted stage.
- Battery event around an arm-operation boundary (students describe or demonstrate safe checkpoint handling).
- Deliberately unreachable Nav2 goal or interrupted action: bounded retry/abort, correct logging, and no false completion.
- Show charge true only after valid docking and false after ≥90%; record `/battery_state` traces. Show explicit C1 DOCKING and UNDOCKING or DEPARTING phases.

## Deliverables
**Code:** ROS 2 package sources, FSM diagram, test/config YAML, README with all launch commands, no `build/`, `install/`, `log/`.

**Individual technical report:** Explain state design, event/guard table, checkpoint representation, ROS 2 action handling, MoveIt arm joint values and validation, docking geometry checks, logs from normal/fault runs, measured metrics, and specific individual contributions. Include failure analysis with at least two concrete log excerpts.

**Video/demo:** Screen recording of Gazebo and RViz showing tasks, charge diversion, recovery, and completion; include visible state and battery telemetry.

**AI-tool disclosure:** List tools used, purpose, generated/adapted code sections, validation performed, and student-authored contributions. Students remain responsible for understanding and defending their code.

## Starter code and learning commands
The `student_fsm.py` provides Nav2, arm, optional DockRobot/UndockRobot action clients, odometry/TF, battery, virtual charger and `/fsm/status` interfaces. Student implementation is required for the full state logic. See **`docs/ROS2_COMMAND_REFERENCE.md`** for precise `ros2 topic pub` base/arm commands, direct arm action testing, RViz MoveIt Joints-tab pose selection, and virtual versus physical docking. Manual CLI commands are for understanding and debugging, not a substitute for automated ROS actions in the FSM.

## Undergraduate vs graduate expectations
**Undergraduate:** Flat FSM with explicit transitions, one battery interruption, all four demonstrated station arm motions, and basic event logs.

**Graduate:** Hierarchical or modular FSM if possible, formal transition/guard table, at least two battery interruption phases, one navigation fault and retry, quantitative results across repeated runs (success rate, duration, charge diversion time), and analysis of race conditions around threshold crossing and action completion.

## Evaluation (100 points)
| Criterion | Points |
|---|---:|
| Correct four-station task sequencing and Nav2 action outcomes | 20 |
| MoveIt 2 pose selection, safety analysis, execution validation | 15 |
| State machine design, readable architecture, guards/events | 20 |
| ≤15% interruption, checkpoint correctness, C1 verification, ≥90% charging and resume | 20 |
| Recovery testing, logging and failure analysis | 5 |
| Reproducibility, report, video, individual contribution and AI disclosure | 10 |
|Bonus points for Successful Recovery Trial or Failure Show after Attempt|10|

The same core outcomes apply to all; graduate-level report and recovery-depth criteria are assessed as well. An implementation that bypasses docking verification or hardcodes charging success does not satisfy the charging criterion.

# AI Tool Usage and Disclosure Policy
Students may use AI tools for understanding ROS 2 concepts, interpreting error messages, debugging, reviewing documentation, and troubleshooting simulation issues. However, generating complete assignment solutions or directly generating FSM implementation code using AI is not permitted. Students must independently design and implement their state transitions, asynchronous action handling, battery interruption, docking, checkpointing, and recovery logic.

Mandatory AI Disclosure: Each student must include a short statement in their project report describing any AI tools used, their purpose, and how the suggestions were applied or verified. If no AI tools were used, explicitly state: “No AI tools were used for this assignment.” Students remain responsible for understanding, explaining, and validating all submitted work.
