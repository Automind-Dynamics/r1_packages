import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # 1. Launch arg for the YAML file
    declare_map_yaml_cmd = DeclareLaunchArgument(
        'yaml_filename',
        default_value='cps.yaml',
        description='Full path to the map YAML file to load'
    )

    yaml_file = LaunchConfiguration('yaml_filename')

    # 2. Map Server Node
    start_map_server_cmd = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': yaml_file}]
    )

    # 3. AMCL Node (from apt-installed nav2)
    start_amcl_cmd = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[{'use_sim_time': False}]  # you can add amcl params here if needed
    )

    # 4. Lifecycle Manager (Handles both map_server + amcl)
    start_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'autostart': True},
            {'node_names': ['map_server', 'amcl']}
        ]
    )

    ld = LaunchDescription()
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(start_map_server_cmd)
    ld.add_action(start_amcl_cmd)
    ld.add_action(start_lifecycle_manager_cmd)

    return ld

