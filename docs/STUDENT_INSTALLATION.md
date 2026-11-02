# ET 5900 — Student setup: Ubuntu 24.04 / ROS 2 Jazzy

## Prerequisites and release boundaries
Use Ubuntu 24.04, ROS 2 Jazzy, Gazebo Sim Harmonic (gz sim 8), TurtleBot 4 Jazzy simulator packages, MoveIt 2, Nav2, ros_gz, ros2_control, and `colcon`. Hardware acceleration is recommended.

The verified TurtleBot 4 packages are taken from the instructor's Jazzy installation; **the repository does not contain the upstream TurtleBot source**. Obtain it using the standard Jazzy apt packages or the instructor-approved pinned TurtleBot simulator commit. Do not mix Humble packages with Jazzy.

## A. Clone assignment
```bash
mkdir -p ~/et5900-course
cd ~/et5900-course
git clone "https://github.com/apandastider/ET5900-Assignment02-FSM.git"
```
The student must replace `YOUR_INSTRUCTOR_GITHUB_URL` with the published address before executing the above command. Check that `src/` contains four custom packages, `maps/` contains YAML+PGM, `worlds/` contains the actual SDF, and `patches/` contains the gripper patch.

## B. Install upstream SO-ARM101 model (tested commit)
```bash
mkdir -p ~/so101_jazzy_ws/src
cd ~/so101_jazzy_ws/src
git clone https://github.com/adoodevv/so101_ros2.git
cd so101_ros2
git checkout 3fb5182614b8e672ab8784b2a10b50656f976c9c
git apply ~/et5900-course/et5900-fsm-assignment/patches/so101_gripper_dynamics.patch
cd ~/so101_jazzy_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```
Patch applies to a **clean clone**. Never apply it blindly to an already-modified tree. Instructor confirmed the patch's contents and licensing before publishing.

## C. Prepare upstream TurtleBot 4 simulator
Install the instructor-approved Jazzy TurtleBot simulator and Nav2 / MoveIt dependencies; exact pinned setup is retained in course environment instructions. Validate:
```bash
source /opt/ros/jazzy/setup.bash
ros2 pkg prefix turtlebot4_gz_bringup
ros2 pkg prefix nav2_bringup
ros2 pkg prefix moveit_ros_move_group
```

## D. Build assignment packages in isolated workspace
```bash
cd ~/et5900-course/et5900-fsm-assignment
bash scripts/release_preflight.sh
# assumes an instructor-provided ~/turtlebot4_ws/install/setup.bash
bash scripts/build_release.sh ~/et5900_release_test
```
If your TurtleBot simulator is installed in a different workspace, source its `install/setup.bash` before building; adapt `scripts/build_release.sh` accordingly.

## E. Install the workcell SDF into the simulator's world location (only if needed)
The tested Gazebo launch uses `world:=week9_pick_place`. On a computer where that world is not already installed, locate the source/installed world lookup used by `tb4_so101_gazebo.launch.py`. Copy `worlds/week9_pick_place.sdf` there, or adapt the launch to accept a full path. **Do not edit root-owned /opt/ros directories**. Do not assume setting `GZ_SIM_RESOURCE_PATH` alone will make a custom ROS launch find the file.

## F. Start components (one terminal each)
Each terminal:
```bash
cd ~/et5900-course/et5900-fsm-assignment
bash scripts/start_component.sh menu
```
Run in order Gazebo → ROS–Gazebo bridge → localization (AMCL, saved map) → navigation (Nav2) → infrastructure (markers and Nav2 Twist converter) → RViz → battery. Start MoveIt separately when designing arm poses. The launcher assumes a `~/et5900_release_test` build. Only launch **one** Nav2 velocity bridge, one AMCL, and one navigation stack.

In RViz set Fixed Frame `map`, add Map `/map` with Transient Local durability, set the robot's initial pose using 2D Pose Estimate, and add MarkerArray `/fsm/station_markers`. Confirm all Nav2 lifecycle nodes are active and the controller has a velocity subscriber.

## G. Student FSM starter
```bash
source /opt/ros/jazzy/setup.bash
source ~/et5900_release_test/install/setup.bash
ros2 run tb4_fsm_assignment student_fsm --ros-args -p use_sim_time:=true
```
This initial skeleton **does not autonomously execute a mission**. Implement TODOs before it can be used for grading. When editing a copied non-symlink workspace, rebuild it to install student changes.

## Known limits
The setup was validated against the instructor's existing ROS/Gazebo dependencies with similar commands.
