#!/usr/bin/env python3
"""
navigation.launch.py
---------------------
Launches the complete Nav2 navigation stack for the Testbed-T1.0.0 WITHOUT
using nav2_bringup — each plugin node is started individually so the pipeline
is explicit and easy to debug component by component.

Nodes launched here (all managed by a single lifecycle_manager):
  • map_server          — serves the pre-built occupancy-grid
  • amcl                — particle-filter localisation
  • planner_server      — global path planning (NavFn/Dijkstra)
  • controller_server   — local trajectory tracking (DWB)
  • bt_navigator        — NavigateToPose action server
  • behavior_server     — recovery behaviours (Spin, BackUp, Wait)
  • smoother_server     — path smoothing
  • velocity_smoother   — smooth velocity commands
  • collision_monitor   — safety stop layer

Prerequisites (must already be running):
  ros2 launch testbed_bringup testbed_full_bringup.launch.py

Usage:
  ros2 launch testbed_navigation navigation.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ── Package paths ─────────────────────────────────────────────────────────
    nav_share     = get_package_share_directory('testbed_navigation')
    bringup_share = get_package_share_directory('testbed_bringup')

    default_map_yaml    = os.path.join(bringup_share, 'maps', 'testbed_world.yaml')
    default_nav_params  = os.path.join(nav_share, 'config', 'nav2_params.yaml')
    default_amcl_params = os.path.join(nav_share, 'config', 'amcl_params.yaml')

    # ── Launch arguments ──────────────────────────────────────────────────────
    declare_map_yaml = DeclareLaunchArgument(
        'map_yaml_file',
        default_value=default_map_yaml,
        description='Full path to the map YAML'
    )
    declare_nav_params = DeclareLaunchArgument(
        'nav2_params_file',
        default_value=default_nav_params,
        description='Full path to nav2 params YAML'
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

    # ── Helper: merge shared params into each node ────────────────────────────
    sim_time_param = {'use_sim_time': LaunchConfiguration('use_sim_time')}

    # ── map_server ────────────────────────────────────────────────────────────
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            LaunchConfiguration('nav2_params_file'),
            sim_time_param,
            {'yaml_filename': LaunchConfiguration('map_yaml_file')},
        ]
    )

    # ── AMCL ─────────────────────────────────────────────────────────────────
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            LaunchConfiguration('amcl_params_file'),
            sim_time_param,
        ]
    )

    # ── planner_server ────────────────────────────────────────────────────────
    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param]
    )

    # ── controller_server ─────────────────────────────────────────────────────
    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param],
        remappings=[('cmd_vel', 'cmd_vel_nav')]   # send to smoother first
    )

    # ── smoother_server ───────────────────────────────────────────────────────
    smoother_server_node = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param]
    )

    # ── behavior_server ───────────────────────────────────────────────────────
    behavior_server_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param]
    )

    # ── bt_navigator ──────────────────────────────────────────────────────────
    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param]
    )

    # ── velocity_smoother ─────────────────────────────────────────────────────
    velocity_smoother_node = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param],
        remappings=[
            ('cmd_vel', 'cmd_vel_nav'),        # input from controller
            ('cmd_vel_smoothed', 'cmd_vel'),   # output to robot / collision monitor
        ]
    )

    # ── collision_monitor ─────────────────────────────────────────────────────
    collision_monitor_node = Node(
        package='nav2_collision_monitor',
        executable='collision_monitor',
        name='collision_monitor',
        output='screen',
        parameters=[LaunchConfiguration('nav2_params_file'), sim_time_param]
    )

    # ── Lifecycle manager — activates all nav2 nodes in order ─────────────────
    lifecycle_manager_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,
            'node_names': [
                'map_server',
                'amcl',
                'planner_server',
                'controller_server',
                'smoother_server',
                'behavior_server',
                'bt_navigator',
                'velocity_smoother',
                'collision_monitor',
            ],
        }]
    )

    return LaunchDescription([
        declare_map_yaml,
        declare_nav_params,
        declare_amcl_params,
        declare_use_sim_time,
        # Nodes
        map_server_node,
        amcl_node,
        planner_server_node,
        controller_server_node,
        smoother_server_node,
        behavior_server_node,
        bt_navigator_node,
        velocity_smoother_node,
        collision_monitor_node,
        # Lifecycle last (it will configure + activate the above)
        lifecycle_manager_navigation,
    ])
