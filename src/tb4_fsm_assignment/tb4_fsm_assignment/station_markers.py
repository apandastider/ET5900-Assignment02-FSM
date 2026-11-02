"""Optional RViz visualization only. Stations are NOT validated collision-free goals."""
import os, yaml
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
class StationMarkers(Node):
    def __init__(self):
        super().__init__('station_markers')
        path=os.path.join(get_package_share_directory('tb4_fsm_assignment'),'config','stations.yaml')
        with open(path,encoding='utf8') as f:self.stations=yaml.safe_load(f)['stations']
        self.pub=self.create_publisher(MarkerArray,'/fsm/station_markers',10)
        self.timer=self.create_timer(1.0,self.publish)
    def publish(self):
        out=MarkerArray();stamp=self.get_clock().now().to_msg()
        for idx,(name,pose) in enumerate(self.stations.items()):
            m=Marker();m.header.frame_id='map';m.header.stamp=stamp;m.ns='fsm_stations';m.id=idx
            m.type=Marker.TEXT_VIEW_FACING;m.action=Marker.ADD
            m.pose.position.x=float(pose['x']);m.pose.position.y=float(pose['y']);m.pose.position.z=0.8
            m.pose.orientation.w=1.0;m.scale.z=0.18;m.color.a=1.0
            m.color.r=1.0;m.color.g=0.95;m.color.b=0.2
            m.text=name+' (candidate)' if not pose['verified'] else name
            out.markers.append(m)
        self.pub.publish(out)
def main():
    rclpy.init();node=StationMarkers()
    try:rclpy.spin(node)
    except KeyboardInterrupt:pass
    finally:node.destroy_node();rclpy.shutdown()
if __name__=='__main__':main()
