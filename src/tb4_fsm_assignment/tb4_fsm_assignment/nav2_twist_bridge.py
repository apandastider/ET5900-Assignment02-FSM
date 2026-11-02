"""Instructor infrastructure: final Nav2 /cmd_vel (Twist) to diffdrive TwistStamped.
WARNING: use only one command bridge; keep collision_monitor upstream.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy
class Bridge(Node):
    def __init__(self):
        super().__init__('nav2_twist_bridge')
        self.pub=self.create_publisher(TwistStamped,'/diffdrive_controller/cmd_vel',
             QoSProfile(depth=10,reliability=ReliabilityPolicy.BEST_EFFORT))
        self.sub=self.create_subscription(Twist,'/cmd_vel',self.on_twist,10)
        self.get_logger().info('Nav2 /cmd_vel Twist -> /diffdrive_controller/cmd_vel TwistStamped')
    def on_twist(self,msg):
        output=TwistStamped()
        output.header.stamp=self.get_clock().now().to_msg()
        output.header.frame_id='base_link'
        output.twist=msg
        self.pub.publish(output)
def main():
    rclpy.init(); node=Bridge()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.shutdown()
if __name__=='__main__':main()
