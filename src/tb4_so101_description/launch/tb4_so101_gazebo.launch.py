
import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
    RegisterEventHandler,
    ExecuteProcess,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # --------------------------------------------------
    # Package paths
    # --------------------------------------------------
    pkg = get_package_share_directory(
        'tb4_so101_description'
    )

    gazebo_pkg = get_package_share_directory(
        'turtlebot4_gz_bringup'
    )

    xacro_file = os.path.join(
        pkg, 'urdf', 'tb4_so101.urdf.xacro'
    )

    controller_yaml = os.path.join(
        pkg, 'config', 'so101_controllers.yaml'
    )

    joint_state_yaml = os.path.join(
        pkg, 'config', 'joint_state_broadcaster.yaml'
    )

    # --------------------------------------------------
    # Combined robot description
    # --------------------------------------------------
    robot_description = ParameterValue(
        Command([
            'xacro ',
            xacro_file,
            ' gazebo:=ignition'
        ]),
        value_type=str
    )

    # --------------------------------------------------
    # Gazebo simulation
    # --------------------------------------------------
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gazebo_pkg,
                'launch',
                'sim.launch.py'
            )
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'model': 'lite'
        }.items()
    )

    # --------------------------------------------------
    # Robot state publisher
    # --------------------------------------------------
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )

    # --------------------------------------------------
    # LiDAR sensor TF
    #
    # Fixes missing TF connection:
    #
    # rplidar_link
    #     |
    #     +-- turtlebot4_so101/rplidar_link/rplidar
    #
    # Required for SLAM Toolbox to process /scan.
    # --------------------------------------------------
    lidar_sensor_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='lidar_sensor_tf',
        output='screen',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'rplidar_link',
            '--child-frame-id',
            'turtlebot4_so101/rplidar_link/rplidar'
        ]
    )

    # --------------------------------------------------
    # Spawn combined TurtleBot 4 + SO-ARM101
    # --------------------------------------------------
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_tb4_so101',
        output='screen',
        arguments=[
            '-name', 'turtlebot4_so101',
            '-topic', 'robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.08'
        ]
    )

    # --------------------------------------------------
    # Sequential controller startup
    # --------------------------------------------------
    startup_script = f"""
set -e

echo "Waiting for controller manager..."

until ros2 service list | grep -qx '/controller_manager/list_controllers'; do
    sleep 1
done

echo "Starting joint_state_broadcaster..."

ros2 run controller_manager spawner \
  joint_state_broadcaster \
  --controller-manager /controller_manager \
  --param-file "{joint_state_yaml}"

echo "Starting TurtleBot diffdrive_controller..."

ros2 run controller_manager spawner \
  diffdrive_controller \
  --controller-manager /controller_manager

echo "Registering SO-ARM101 controller types..."

ros2 param set /controller_manager \
  arm_controller.type \
  joint_trajectory_controller/JointTrajectoryController

ros2 param set /controller_manager \
  gripper_controller.type \
  forward_command_controller/ForwardCommandController

echo "Starting SO-ARM101 arm controller..."

ros2 run controller_manager spawner \
  arm_controller \
  --controller-manager /controller_manager \
  --param-file "{controller_yaml}"

echo "Starting SO-ARM101 gripper controller..."

ros2 run controller_manager spawner \
  gripper_controller \
  --controller-manager /controller_manager \
  --param-file "{controller_yaml}"

echo "All four controllers started successfully."
"""

    start_controllers = ExecuteProcess(
        cmd=['bash', '-c', startup_script],
        output='screen'
    )

    # --------------------------------------------------
    # Start controllers after robot is spawned
    # --------------------------------------------------
    controller_startup_event = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_robot,
            on_exit=[start_controllers]
        )
    )

    # --------------------------------------------------
    # Launch description
    # --------------------------------------------------
    return LaunchDescription([

        DeclareLaunchArgument(
            'world',
            default_value='week9_pick_place',
            description='Gazebo simulation world'
        ),

        gazebo,

        robot_state_publisher,

        lidar_sensor_tf,

        controller_startup_event,

        TimerAction(
            period=6.0,
            actions=[spawn_robot]
        )
    ])
