"""Instructor-provided virtual battery. Students implement the fleet FSM."""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from .battery_math import advance

class VirtualBattery(Node):
    def __init__(self):
        super().__init__('virtual_battery')
        for name, default in (
            ('initial_percent', 16.0),
            ('idle_drain_percent_per_min', 0.03),
            ('moving_drain_percent_per_min', 2.0),
            ('charge_percent_per_min', 12.0),
        ):
            self.declare_parameter(name, default)
        self.percent = max(0.0, min(100.0, float(self.get_parameter('initial_percent').value)))
        self.moving = False
        self.charging = False
        self.period = 1.0
        self.pub = self.create_publisher(BatteryState, '/battery_state', 10)
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)
        self.create_subscription(Bool, '/virtual_charger/docked', self.dock_cb, 10)
        self.create_timer(self.period, self.tick)
        self.get_logger().info('Virtual battery started; BatteryState.percentage uses [0,1].')

    def odom_cb(self, msg):
        twist = msg.twist.twist
        self.moving = abs(twist.linear.x) > 0.01 or abs(twist.angular.z) > 0.02

    def dock_cb(self, msg):
        self.charging = bool(msg.data)

    def tick(self):
        def param(key):
            return float(self.get_parameter(key).value)
        try:
            self.percent = advance(
                self.percent, self.period, self.moving, self.charging,
                param('idle_drain_percent_per_min'),
                param('moving_drain_percent_per_min'),
                param('charge_percent_per_min'),
            )
        except ValueError as exc:
            self.get_logger().error(str(exc))
            return
        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.percentage = self.percent / 100.0
        msg.present = True
        msg.power_supply_status = (
            BatteryState.POWER_SUPPLY_STATUS_CHARGING if self.charging
            else BatteryState.POWER_SUPPLY_STATUS_DISCHARGING
        )
        msg.power_supply_health = BatteryState.POWER_SUPPLY_HEALTH_GOOD
        msg.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_UNKNOWN
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = VirtualBattery()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
