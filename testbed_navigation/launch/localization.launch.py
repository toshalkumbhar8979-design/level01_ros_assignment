#!/usr/bin/env python3
"""
localization.launch.py
----------------------
Launches AMCL (Adaptive Monte Carlo Localization) for the Testbed-T1.0.0.

This file:
  1. Starts nav2_map_server (map must be active before AMCL can use it).
  2. Starts nav2_amcl with the tuned parameter file.
  3. Brings both nodes to ACTIVE via a lifecycle manager.

Run AFTER the simulation is up:
  ros2 launch testbed_navigation localization.launch.py

Verify in Rviz:
  - Add a "Map" display → should show the occupancy grid.
  - Add a "PoseArray" display on topic /particlecloud → particles around robot.
  - Use "2D Pose Estimate" tool to set an initial pose if particles are scattered.
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ── Package share directories ─────────────────────────────────────────────
    nav_share    = get_package_share_directory('testbed_navigation')
    bringup_share = get_package_share_directory('testbed_bringup')

    default_map_yaml   = os.path.join(bringup_share, 'maps', 'testbed_world.yaml')
    default_amcl_params = os.path.join(nav_share, 'config', 'amcl_params.yaml')

    # ── Launch arguments ──────────────────────────────────────────────────────
    declare_map_yaml = DeclareLaunchArgument(
        'map_yaml_file',
        default_value=default_map_yaml,
        description='Full path to the map YAML'
    )

    declare_amcl_params = DeclareLaunchArgument(
        'amcl_params_file',
        default_value=default_amcl_params,
        description='Full path to AMCL params YAML'
    )

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo simulated clock'
    )

    # ── map_server ────────────────────────────────────────────────────────────
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

    # ── AMCL ─────────────────────────────────────────────────────────────────
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            LaunchConfiguration('amcl_params_file'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    # ── Lifecycle manager (manages map_server + amcl) ─────────────────────────
    lifecycle_manager_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }]
    )

    return LaunchDescription([
        declare_map_yaml,
        declare_amcl_params,
        declare_use_sim_time,
        map_server_node,
        amcl_node,
        lifecycle_manager_localization,
    ])
