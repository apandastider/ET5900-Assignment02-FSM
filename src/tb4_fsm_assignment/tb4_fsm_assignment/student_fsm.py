
"""ET 5900 — Assignment 02: Student FSM Starter.

ROS 2 interfaces and programming structure are provided.

STUDENTS MUST IMPLEMENT:
- FSM transition guards and mission sequencing
- Asynchronous navigation and arm action handling
- Battery-triggered interruption and checkpointing
- Virtual docking verification and charging
- Safe task resumption and failure recovery

Running this starter does not command robot movement.
"""

from enum import Enum, auto
import os
import math
import yaml

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from ament_index_python.packages import get_package_share_directory

from sensor_msgs.msg import BatteryState
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool, String
from tf2_ros import Buffer, TransformListener

from nav2_msgs.action import NavigateToPose, DockRobot, UndockRobot
from control_msgs.action import FollowJointTrajectory


class MissionState(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    ARM_EXECUTING = auto()
    INTERRUPTING = auto()
    DOCKING = auto()
    CHARGING = auto()
    UNDOCKING = auto()
    RESUMING = auto()
    RECOVERY = auto()
    COMPLETE = auto()
    FAILED = auto()


class MissionFSM(Node):

    def __init__(self):
        super().__init__('student_mission_fsm')

        # ============================================================
        # 1. Load station configurations
        # ============================================================

        package_share = get_package_share_directory(
            'tb4_fsm_assignment'
        )

        station_path = os.path.join(
            package_share,
            'config',
            'stations.yaml'
        )

        with open(station_path, encoding='utf-8') as stream:
            station_config = yaml.safe_load(stream)

        self.stations = station_config['stations']

        # ============================================================
        # 2. Load student-defined arm configurations
        # ============================================================

        arm_path = os.path.join(
            package_share,
            'config',
            'arm_poses_TEMPLATE.yaml'
        )

        with open(arm_path, encoding='utf-8') as stream:
            self.arm_config = yaml.safe_load(stream)

        # ============================================================
        # 3. ROS 2 action clients
        # ============================================================

        self.nav = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

        self.arm = ActionClient(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )

        # Optional: requires a configured Nav2 docking server.
        # The supplied C1 workcell uses virtual docking.
        self.dock_action = ActionClient(
            self,
            DockRobot,
            '/dock_robot'
        )

        self.undock_action = ActionClient(
            self,
            UndockRobot,
            '/undock_robot'
        )

        # ============================================================
        # 4. Publishers and subscriptions
        # ============================================================

        self.dock_pub = self.create_publisher(
            Bool,
            '/virtual_charger/docked',
            10
        )

        self.status_pub = self.create_publisher(
            String,
            '/fsm/status',
            10
        )

        self.battery_sub = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.on_battery,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.on_odom,
            10
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self
        )

        # ============================================================
        # 5. Sensor information
        # ============================================================

        self.battery_percent = None
        self.odom = None

        # ============================================================
        # 6. FSM state and mission tracking
        # ============================================================

        self.state = MissionState.IDLE

        # Required mission order.
        self.mission = ['R1', 'R2', 'G1', 'G2']

        # Students update these after successful operations.
        self.mission_index = 0
        self.current_phase = None

        # ============================================================
        # 7. Asynchronous action tracking
        # ============================================================

        # Students store action goal handles after acceptance.
        self.nav_goal_handle = None
        self.arm_goal_handle = None

        # Students manage dispatch and completion flags.
        self.nav_pending = False
        self.arm_pending = False

        # ============================================================
        # 8. Interruptions, docking, and checkpointing
        # ============================================================

        self.interrupt_requested = False
        self.docking_verified = False

        # Students define the checkpoint representation.
        self.checkpoint = None

        # ============================================================
        # 9. FSM timer
        # ============================================================

        self.get_logger().warning(
            'STUDENT SKELETON: Autonomous behavior is not implemented.'
        )

        self.timer = self.create_timer(
            0.5,
            self.tick
        )

    # ================================================================
    # Helper: Publish FSM status
    # ================================================================

    def publish_status(self, message):
        """
        Publish mission status for debugging and evaluation.

        Example:
            self.publish_status("Navigating to R1")
        """
        status_msg = String()
        status_msg.data = str(message)

        self.status_pub.publish(status_msg)
        self.get_logger().info(str(message))

    # ================================================================
    # ROS 2 subscription callbacks
    # ================================================================

    def on_battery(self, msg):
        """
        Receives battery updates.

        BatteryState.percentage ranges from 0.0 to 1.0.
        Internally, battery_percent is stored as 0–100.
        """

        if not math.isfinite(msg.percentage):
            self.get_logger().warning(
                'Received non-finite battery percentage.'
            )
            return

        self.battery_percent = (
            float(msg.percentage) * 100.0
        )

        # TODO-STUDENT:
        # 1. Identify low-battery events (<=15%).
        # 2. Set appropriate interruption requests.
        # 3. Avoid repeated interruptions during charging.
        # 4. Decide how to handle stale or invalid data.

    def on_odom(self, msg):
        """Store latest odometry for monitoring and docking."""
        self.odom = msg

    # ================================================================
    # Main FSM dispatcher
    # ================================================================

    def tick(self):
        """
        Periodic FSM dispatcher.

        Automatically called by ROS 2 approximately every 0.5 seconds.

        IMPORTANT:
        - Do not block inside this method.
        - Do not repeatedly send the same action goal.
        - Use asynchronous action callbacks.
        - Check action outcomes before advancing mission states.
        """

        if self.state == MissionState.IDLE:

            # TODO-STUDENT:
            # Check sensor/action-server readiness.
            # Start the first station navigation exactly once.
            pass

        elif self.state == MissionState.NAVIGATING:

            # TODO-STUDENT:
            # Monitor Nav2 navigation results.
            # Respond to low-battery interruption requests.
            pass

        elif self.state == MissionState.ARM_EXECUTING:

            # TODO-STUDENT:
            # Monitor arm trajectory execution.
            # Define a safe interruption policy.
            pass

        elif self.state == MissionState.INTERRUPTING:

            # TODO-STUDENT:
            # Preserve mission station and execution phase.
            # Cancel or safely finish the active action.
            # Await confirmation before navigating to C1.
            pass

        elif self.state == MissionState.DOCKING:

            # TODO-STUDENT:
            # Complete virtual docking at C1.
            # Verify the final pose and zero velocity.
            pass

        elif self.state == MissionState.CHARGING:

            # TODO-STUDENT:
            # Monitor battery level.
            # Continue charging until >=90%.
            pass

        elif self.state == MissionState.UNDOCKING:

            # TODO-STUDENT:
            # Stop virtual charging.
            # Safely depart C1.
            pass

        elif self.state == MissionState.RESUMING:

            # TODO-STUDENT:
            # Restore saved checkpoint.
            # Navigate back to interrupted station if needed.
            # Resume without skipping or duplicating operations.
            pass

        elif self.state == MissionState.RECOVERY:

            # TODO-STUDENT:
            # Implement bounded retries or safe mission abort.
            pass

        elif self.state == MissionState.COMPLETE:

            # Mission completion behavior is student-defined.
            pass

        elif self.state == MissionState.FAILED:

            # Safe terminal failure behavior is student-defined.
            pass

    # ================================================================
    # Navigation action
    # ================================================================

    def start_navigation(self, station_key):
        """
        Navigate asynchronously to a named station.

        Supported:
            R1, R2, G1, G2, C1
        """

        if station_key not in self.stations:
            self.get_logger().error(
                f'Unknown navigation station: {station_key}'
            )
            return

        # TODO-STUDENT:
        # 1. Read x, y, yaw from self.stations[station_key].
        # 2. Construct NavigateToPose.Goal in the map frame.
        # 3. Check action-server readiness.
        # 4. Send the goal using send_goal_async().
        # 5. Store the accepted goal handle.
        # 6. Register goal-result and feedback callbacks.
        # 7. Handle SUCCEEDED, ABORTED, and CANCELED.
        # 8. Prevent overlapping navigation goals.

        raise NotImplementedError(
            'Student implements asynchronous navigation.'
        )

    # ================================================================
    # SO-ARM101 motion action
    # ================================================================

    def perform_station_motion(self, station_key):
        """
        Execute a station-specific arm operation.

        Supported:
            R1, R2, G1, G2

        Students identify safe joint targets using MoveIt 2.
        """

        pose_config = self.arm_config.get('poses', {})

        if station_key not in pose_config:
            self.get_logger().error(
                f'No arm pose defined for station {station_key}.'
            )
            return

        joint_names = self.arm_config['arm_joints']

        joint_targets = pose_config[
            station_key
        ]['joint_positions']

        if len(joint_targets) != len(joint_names):
            self.get_logger().error(
                f'Invalid pose for {station_key}: '
                f'expected {len(joint_names)} joint values, '
                f'got {len(joint_targets)}.'
            )
            return

        # Validate that joint targets are finite numbers.
        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in joint_targets
        ):
            self.get_logger().error(
                f'Invalid or non-finite joint values for {station_key}.'
            )
            return

        # TODO-STUDENT:
        # 1. Confirm chosen joint targets respect joint limits.
        # 2. Validate collision-free motion using MoveIt 2.
        # 3. Construct JointTrajectory with joint_names and points.
        # 4. Construct FollowJointTrajectory.Goal.
        # 5. Send goal asynchronously.
        # 6. Handle acceptance, execution result, and failure.
        # 7. Advance the FSM only after successful completion.

        raise NotImplementedError(
            'Student implements asynchronous arm execution.'
        )

    # ================================================================
    # C1 docking
    # ================================================================

    def dock_at_c1(self):
        """
        Complete docking at charging station C1.

        The provided Gazebo workcell uses virtual docking.
        """

        # TODO-STUDENT:
        # 1. Navigate to a validated C1 staging/approach pose.
        # 2. Complete a safe docking maneuver or virtual dock stage.
        # 3. Independently verify robot alignment and stopped motion.
        # 4. Store docking result.
        #
        # DockRobot may only be used if a compatible dock plugin
        # has been configured and verified.

        raise NotImplementedError(
            'Student implements docking.'
        )

    def verify_docking(self):
        """
        Verify docking using robot pose and motion information.
        """

        # TODO-STUDENT:
        # 1. Obtain the map -> base_link transform from TF.
        # 2. Compare position to verified C1 docking pose.
        # 3. Check heading/yaw tolerance.
        # 4. Check odometry velocity is sufficiently small.
        # 5. Require successful navigation/docking evidence.
        # 6. Reject stale TF or odometry information.

        raise NotImplementedError(
            'Student implements independent docking verification.'
        )

    # ================================================================
    # Battery interruption and checkpointing
    # ================================================================

    def interrupt_and_save(self):
        """
        Safely interrupt an active mission operation.
        """

        # TODO-STUDENT:
        # 1. Identify current mission station and phase.
        # 2. Save a consistent checkpoint.
        # 3. Request safe cancellation or completion.
        # 4. Await the terminal action result.
        # 5. Confirm the base and arm are safe to move.
        # 6. Initiate navigation to C1.

        raise NotImplementedError(
            'Student implements interruption and checkpointing.'
        )

    def begin_charging(self):
        """
        Start virtual charging only after docking succeeds.
        """

        # TODO-STUDENT:
        # 1. Verify docking conditions.
        # 2. Publish Bool(data=True) to /virtual_charger/docked.
        # 3. Enter charging state.
        # 4. Handle charging anomalies and timeout.

        raise NotImplementedError(
            'Student implements charging control.'
        )

    def undock_and_resume(self):
        """
        Stop charging and resume the interrupted mission.
        """

        # TODO-STUDENT:
        # 1. Require battery >=90%.
        # 2. Publish Bool(data=False) to stop charging.
        # 3. Safely depart C1.
        # 4. Restore checkpoint station and phase.
        # 5. Return to the required station if needed.
        # 6. Avoid skipped or duplicated operations.

        raise NotImplementedError(
            'Student implements undocking and mission resumption.'
        )

    # ================================================================
    # Failure recovery
    # ================================================================

    def recover(self, cause):
        """
        Handle navigation, arm, docking, or charging failures.
        """

        # TODO-STUDENT:
        # 1. Log the failure cause.
        # 2. Classify recoverable vs. terminal failures.
        # 3. Apply a bounded retry policy.
        # 4. Preserve checkpoint correctness.
        # 5. Transition safely to FAILED if necessary.

        raise NotImplementedError(
            'Student implements recovery.'
        )


def main():
    rclpy.init()

    node = MissionFSM()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
