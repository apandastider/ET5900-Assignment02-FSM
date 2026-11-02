#!/usr/bin/env python3
"""MoveIt 2 and RViz for the already running TurtleBot4 Lite + SO-ARM101 Gazebo robot.

This launch file does not start Gazebo, Nav2, a map server, or controllers.
"""

import os
import subprocess
import xml.etree.ElementTree as ET

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

ARM_JOINTS = [
    'so101_shoulder_pan',
    'so101_shoulder_lift',
    'so101_elbow_flex',
    'so101_wrist_flex',
    'so101_wrist_roll',
]


def build_semantic_description(urdf_xml):
    """Build an SRDF matching the exact combined URDF link and joint names."""
    robot = ET.fromstring(urdf_xml)
    joint_map = {joint.attrib['name']: joint for joint in robot.findall('joint')}
    missing = [name for name in ARM_JOINTS + ['so101_gripper'] if name not in joint_map]
    if missing:
        raise RuntimeError(f'Missing SO101 joints in combined URDF: {missing}')

    tip = joint_map['so101_wrist_roll'].find('child').attrib['link']
    base = 'so101_base_link'
    links = {link.attrib['name'] for link in robot.findall('link')}
    if base not in links or tip not in links:
        raise RuntimeError(f'Missing MoveIt arm chain endpoint: {base} or {tip}')

    semantic = ET.Element('robot', {'name': robot.attrib.get('name', 'turtlebot4_so101')})
    arm = ET.SubElement(semantic, 'group', {'name': 'arm'})
    ET.SubElement(arm, 'chain', {'base_link': base, 'tip_link': tip})
    gripper = ET.SubElement(semantic, 'group', {'name': 'gripper'})
    ET.SubElement(gripper, 'joint', {'name': 'so101_gripper'})

    for joint in joint_map.values():
        parent = joint.find('parent')
        child = joint.find('child')
        if parent is not None and child is not None:
            ET.SubElement(semantic, 'disable_collisions', {
                'link1': parent.attrib['link'],
                'link2': child.attrib['link'],
                'reason': 'Adjacent',
            })

    # Additional known mechanical collision pairs.
    # Only exclude pairs after verifying they represent
    # intended overlap in the simulated robot geometry.
    additional_disabled_collisions = [
        ('base_link', 'left_wheel'),
        ('base_link', 'right_wheel'),
        ('so101_moving_jaw_so101_v1_link', 'so101_wrist_link'),
    ]

    for link1, link2 in additional_disabled_collisions:
        if link1 not in links or link2 not in links:
            raise RuntimeError(
                f'Collision exemption references missing links: '
                f'{link1}, {link2}'
            )

        ET.SubElement(semantic, 'disable_collisions', {
            'link1': link1,
            'link2': link2,
            'reason': 'Default',
        })

    # return ET.tostring(semantic, encoding='unicode')
    return ET.tostring(semantic, encoding='unicode')


def setup(context, *args, **kwargs):
    description_pkg = get_package_share_directory('tb4_so101_description')
    moveit_pkg = get_package_share_directory('tb4_so101_moveit_config')

    xacro_file = os.path.join(description_pkg, 'urdf', 'tb4_so101.urdf.xacro')
    result = subprocess.run(
        ['xacro', xacro_file, 'gazebo:=ignition'],
        capture_output=True, text=True, check=True,
    )
    urdf = result.stdout
    srdf = build_semantic_description(urdf)

    def load_yaml(filename):
        path = os.path.join(moveit_pkg, 'config', filename)
        with open(path, encoding='utf-8') as stream:
            data = yaml.safe_load(stream)
        if not isinstance(data, dict):
            raise RuntimeError(f'{path} must contain a YAML dictionary')
        return data

    controllers = load_yaml('moveit_controllers.yaml')
    kinematics = load_yaml('kinematics.yaml')
    ompl = load_yaml('ompl_planning.yaml')
    joint_limits = load_yaml('joint_limits.yaml')

    # Jazzy expects OMPL planning_plugins, request_adapters and response_adapters
    # to be string arrays, not whitespace-delimited strings. Normalize older YAML.
    if 'ompl' in ompl and isinstance(ompl['ompl'], dict):
        ompl = ompl['ompl']
    plugin = ompl.pop('planning_plugin', None)
    plugins = ompl.get('planning_plugins', plugin)
    if isinstance(plugins, str):
        plugins = [plugins]
    if not plugins:
        plugins = ['ompl_interface/OMPLPlanner']
    if not isinstance(plugins, list) or not all(isinstance(p, str) for p in plugins):
        raise RuntimeError('OMPL planning_plugins must be a list of strings')
    ompl['planning_plugins'] = plugins

    for key in ('request_adapters', 'response_adapters'):
        value = ompl.get(key)
        if isinstance(value, str):
            ompl[key] = value.split()
        elif value is not None and not isinstance(value, list):
            raise RuntimeError(f'OMPL {key} must be a list of strings')

    print(f'[tb4_so101_moveit] OMPL plugins: {ompl["planning_plugins"]}', flush=True)

    shared = [
        {'robot_description': ParameterValue(urdf, value_type=str)},
        {'robot_description_semantic': ParameterValue(srdf, value_type=str)},
        {'robot_description_kinematics': kinematics},
        {'use_sim_time': True},
    ]
    pipeline = {
        'planning_pipelines': ['ompl'],
        'default_planning_pipeline': 'ompl',
        'ompl': ompl,
    }

    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        name='move_group',
        output='screen',
        parameters=shared + [
            {'robot_description_planning': {
                **joint_limits,
                'default_velocity_scaling_factor': 0.15,
                'default_acceleration_scaling_factor': 0.15,
            }},
            pipeline,
            controllers,
            {
                'planning_scene_monitor_options': {
                    'name': 'planning_scene_monitor',
                    'robot_description': 'robot_description',
                    'joint_state_topic': '/joint_states',
                },
                'publish_robot_description_semantic': True,
                'publish_planning_scene': True,
                'publish_geometry_updates': True,
                'publish_state_updates': True,
                'publish_transforms_updates': True,
                'trajectory_execution.allowed_execution_duration_scaling': 1.5,
                'trajectory_execution.allowed_goal_duration_margin': 1.0,
                'trajectory_execution.allowed_start_tolerance': 0.05,
                'moveit_manage_controllers': False,
            },
        ],
    )

    rviz_config = os.path.join(moveit_pkg, 'config', 'moveit.rviz')
    rviz_arguments = ['-d', rviz_config] if os.path.isfile(rviz_config) else []
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz')),
        arguments=rviz_arguments,
        parameters=shared + [pipeline],
    )
    return [move_group, rviz]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        OpaqueFunction(function=setup),
    ])