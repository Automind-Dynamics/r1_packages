import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Replace 'your_package_name' with your actual package name
    config_file = os.path.join(
        get_package_share_directory('r1_teleop'),
        'config',
        'twist_mux.yaml'
    )

    return LaunchDescription([
        Node(
            package='twist_mux',
            executable='twist_mux',
            name='twist_mux',
            output='screen',
            parameters=[config_file],
            # twist_mux outputs to 'cmd_vel_out' by default. 
            # We remap it here to what your robot is already subscribed to.
            remappings=[('/cmd_vel_out', '/r1001/cmd_vel')]
        )
    ])
