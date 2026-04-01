import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_r1_bringup = get_package_share_directory('r1_bringup')
    pkg_r1_teleop = get_package_share_directory('r1_teleop')
    pkg_r1_localization = get_package_share_directory('r1_localization')


    # Include microros launch file
    launch_microros_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_bringup, 'launch', 'microros.launch.py')
        ),
    )


    # Include twist_mux launch file
    launch_twist_mux_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_teleop, 'launch', 'twist_mux_launch.py')
        ),
    )


    # Include teleop joy launch file
    launch_teleop_joy_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_teleop, 'launch', 'r1_teleop_joy.launch.py')
        ),
    )

    
    # Include sensors launch file
    launch_sensors_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_bringup, 'launch', 'sensors.launch.py')
        ),
    )


    # Include localization launch file including rsp
    launch_localization_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1_localization, 'launch', 'r1_localization.launch.py')
        ),
    )

    

    
    

    # Create launch description and add actions
    ld = LaunchDescription()

    ld.add_action(launch_microros_cmd)
    ld.add_action(launch_twist_mux_cmd)
    ld.add_action(launch_teleop_joy_cmd)
    ld.add_action(launch_sensors_cmd)
    # ld.add_action(launch_localization_cmd)

    return ld
