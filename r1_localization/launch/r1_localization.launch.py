#!/usr/bin/env python3

from os.path import join
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    # Set the path to different files and folders.
    localization_pkg = get_package_share_directory("r1_localization")
    ekf_params_path = join(localization_pkg, 'config', 'ekf.yaml')

    use_sim_time = LaunchConfiguration("use_sim_time",)
    
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use Simulation Time"
    )

    
    launch_ekf_cmd = Node(
        package='robot_localization',
        executable='ekf_node',
        name="ekf_filter_node",
        output='screen',
        parameters=[ekf_params_path, {"use_sim_time": use_sim_time}],
        remappings=[("odometry/filtered", "odometry/filtered")],
    )

    # Include rsp launch file
    launch_rsp_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(localization_pkg, 'launch', 'r1_rsp.launch.py')
        ),
    )

    
    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time)
    
    # Add any actions
    ld.add_action(launch_ekf_cmd)
    ld.add_action(launch_rsp_cmd)

    return ld
