#!/usr/bin/env python3
"""
map_loader.launch.py
--------------------
Launches nav2_map_server to serve the pre-built occupancy-grid map of the
testbed environment.  This launch file is intentionally kept minimal so it
can be tested independently before adding localization or navigation.

Usage:
  ros2 launch testbed_navigation map_loader.launch.py

Optional args:
  map_yaml_file:=</path/to/custom_map.yaml>   Override the default map.
  use_sim_time:=true|false                    Use simulated clock (default: true).
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ── Resolve the default map YAML path from the installed share dir ──────
    bringup_share = get_package_share_directory('testbed_bringup')
    default_map_yaml = os.path.join(bringup_share, 'maps', 'testbed_world.yaml')

    # ── Launch arguments ──────────────────────────────────────────────────────
    declare_map_yaml = DeclareLaunchArgument(
        name='map_yaml_file',
        default_value=default_map_yaml,
        description='Full path to the map YAML file to load'
    )

    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulated (Gazebo) clock'
    )

    # ── map_server node ───────────────────────────────────────────────────────
    # nav2_map_server publishes the occupancy grid on /map and provides the
    # /map_server/load_map service.  A lifecycle manager is required to
    # transition it to the ACTIVE state; we include a minimal one here.
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'yaml_filename': LaunchConfiguration('map_yaml_file'),
        }]
    )

    # ── Lifecycle manager for map_server ──────────────────────────────────────
    # Without this the map_server stays in UNCONFIGURED state and never
    # publishes the map.
    lifecycle_manager_map = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,
            'node_names': ['map_server'],
        }]
    )

    return LaunchDescription([
        declare_map_yaml,
        declare_use_sim_time,
        map_server_node,
        lifecycle_manager_map,
    ])
