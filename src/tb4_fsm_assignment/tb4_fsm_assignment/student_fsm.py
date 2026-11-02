"""ET 5900 student FSM starter: ROS interfaces only, no mission solution.

Students design transition guards, asynchronous action callbacks, docking,
preemption, checkpoint/recovery and charging logic. Running this starts no motion.
"""
from enum import Enum, auto
import os
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
        path = os.path.join(get_package_share_directory('tb4_fsm_assignment'),
                            'config', 'stations.yaml')
        with open(path, encoding='utf-8') as stream:
            self.stations = yaml.safe_load(stream)['stations']

        # Provided interfaces; STUDENTS implement asynchronous goal behavior.
        self.nav = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.arm = ActionClient(self, FollowJointTrajectory,
                                '/arm_controller/follow_joint_trajectory')
        # Only usable if a correctly configured Nav2 docking server exists.
        self.dock_action = ActionClient(self, DockRobot, '/dock_robot')
        self.undock_action = ActionClient(self, UndockRobot, '/undock_robot')

        self.dock_pub = self.create_publisher(Bool, '/virtual_charger/docked', 10)
        self.status_pub = self.create_publisher(String, '/fsm/status', 10)
        self.battery_sub = self.create_subscription(
            BatteryState, '/battery_state', self.on_battery, 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.on_odom, 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.battery_percent = None
        self.odom = None
        self.state = MissionState.IDLE
        self.checkpoint = None
        self.get_logger().warning(
            'STUDENT SKELETON: no autonomous commands; implement FSM TODOs')
        self.timer = self.create_timer(0.5, self.tick)

    def on_battery(self, msg):
        # BatteryState.percentage is 0..1; student decides threshold guards.
        self.battery_percent = float(msg.percentage) * 100.0
        # TODO-STUDENT: low battery event, debounce/hysteresis, preemption.

    def on_odom(self, msg):
        self.odom = msg

    def tick(self):
        # TODO-STUDENT: state transitions, nonblocking goal dispatch,
        # cancellation results, stale sensor and timeout checks.
        pass

    def start_navigation(self, station_key):
        # TODO-STUDENT: async Nav2 goal acceptance, result, cancellation,
        # and checkpoint-safe transition. NEVER issue concurrent base goals.
        raise NotImplementedError('Student implements navigation action handling')

    def perform_station_motion(self, station_key):
        # TODO-STUDENT: independently plan and validate station-safe arm poses
        # using MoveIt Joints tab; execute and check completion/failure.
        raise NotImplementedError('Student implements arm action handling')

    def dock_at_c1(self):
        # TODO-STUDENT: stop at C1 staging pose, then dock.
        # If an actual configured DockRobot server is available, use it and
        # check its outcome. In the supplied virtual C1 marker workcell,
        # implement/verify an explicit pose-based virtual docking stage.
        # NEVER interpret NavigateToPose success alone as docking success.
        raise NotImplementedError('Student implements C1 docking')

    def verify_docking(self):
        # TODO-STUDENT: validate map->base_link pose, yaw and zero base
        # velocity, plus appropriate navigation/docking success evidence.
        raise NotImplementedError('Student implements independent dock checks')

    def interrupt_and_save(self):
        # TODO-STUDENT: safely cancel/finish in-flight actions, store exact
        # mission station and phase; handle cancellation/action races.
        raise NotImplementedError('Student implements checkpointing')

    def begin_charging(self):
        # TODO-STUDENT: publish True ONLY after independently verified dock.
        raise NotImplementedError('Student implements charging')

    def undock_and_resume(self):
        # TODO-STUDENT: at >=90% publish False; undock safely, then
        # restore mission phase without duplicating or omitting operations.
        # Use UndockRobot only if a real configured dock plugin is available.
        raise NotImplementedError('Student implements undock/resume')

    def recover(self, cause):
        # TODO-STUDENT: bounded retries, safe abort, consistent status.
        raise NotImplementedError('Student implements recovery')


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
