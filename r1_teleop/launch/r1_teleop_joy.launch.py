import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    joy_params = LaunchConfiguration('joy_params')
    joy_vel = LaunchConfiguration('joy_vel')
    publish_stamped_twist = LaunchConfiguration('publish_stamped_twist')
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([

        DeclareLaunchArgument(
            'joy_params',
            default_value=os.path.join(
                get_package_share_directory('r1_teleop'),
                'config',
                'joy.yaml'
            )
        ),

        # Updated default_value to publish to /joy_cmd_vel for twist_mux
        DeclareLaunchArgument(
            'joy_vel',
            default_value='/joy_cmd_vel'
        ),

        DeclareLaunchArgument(
            'publish_stamped_twist',
            default_value='false'
        ),
        
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false'
        ),

        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            parameters=[joy_params],
        ),

        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy_node',
            parameters=[
                joy_params,
                {'publish_stamped_twist': publish_stamped_twist},
            ],
            remappings=[
                ('/cmd_vel', joy_vel),
            ],
        ),
    ])
