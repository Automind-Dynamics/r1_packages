import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node

def generate_launch_description():
    pkg_r1_bringup = get_package_share_directory('r1_bringup')
    pkg_r1_teleop = get_package_share_directory('r1_teleop')
    pkg_r1_localization = get_package_share_directory('r1_localization')

    enable_teleop_arg = DeclareLaunchArgument(
        'enable_teleop',
        default_value='true',
        description='Enable joystick teleoperation'
    )
    enable_sensors_arg = DeclareLaunchArgument(
        'enable_sensors',
        default_value='true',
        description='Enable sensors (IMU, LiDAR, RealSense, etc.)'
    )
    enable_localization_arg = DeclareLaunchArgument(
        'enable_localization',
        default_value='false',
        description='Enable localization (robot_state_publisher + SLAM/AMCL)'
    )

    enable_teleop       = LaunchConfiguration('enable_teleop')
    enable_sensors      = LaunchConfiguration('enable_sensors')
    enable_localization = LaunchConfiguration('enable_localization')


    launch_microros_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_bringup, 'launch', 'microros.launch.py')
        ),
    )
    launch_twist_mux_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_teleop, 'launch', 'twist_mux_launch.py')
        ),
    )

    launch_teleop_joy_cmd = GroupAction(
        condition=IfCondition(enable_teleop),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_r1_teleop, 'launch', 'r1_teleop_joy.launch.py')
                ),
            )
        ]
    )

    launch_sensors_cmd = GroupAction(
        condition=IfCondition(enable_sensors),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_r1_bringup, 'launch', 'sensors.launch.py')
                ),
            )
        ]
    )

    launch_localization_cmd = GroupAction(
        condition=IfCondition(enable_localization),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_r1_localization, 'launch', 'r1_localization.launch.py')
                ),
            )
        ]
    )

    ld = LaunchDescription()

    ld.add_action(enable_teleop_arg)
    ld.add_action(enable_sensors_arg)
    ld.add_action(enable_localization_arg)

    ld.add_action(launch_microros_cmd)
    ld.add_action(launch_twist_mux_cmd)
    ld.add_action(launch_teleop_joy_cmd)
    ld.add_action(launch_sensors_cmd)
    ld.add_action(launch_localization_cmd)

    return ld