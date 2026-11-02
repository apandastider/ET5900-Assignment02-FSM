"""Run only after Gazebo+Nav2 are live. Starts command bridge and station markers.
Battery simulator is intentionally launched separately for deterministic test setup.
"""
from launch import LaunchDescription
from launch_ros.actions import Node
def generate_launch_description():
    return LaunchDescription([
        Node(package='tb4_fsm_assignment',executable='nav2_twist_bridge',
             name='nav2_twist_bridge',output='screen',parameters=[{'use_sim_time':True}]),
        Node(package='tb4_fsm_assignment',executable='station_markers',
             name='station_markers',output='screen',parameters=[{'use_sim_time':True}]),
    ])
