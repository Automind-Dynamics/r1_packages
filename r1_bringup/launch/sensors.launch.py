import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    pkg_rplidar = get_package_share_directory('rplidar_ros')

    # Declare launch arguments

    lidar_port = LaunchConfiguration('lidar_port')

    declare_lidar_port = DeclareLaunchArgument(
        'lidar_port',
        default_value='/dev/rplidar',
        description='Rplidar S2 Serial Port'
    )


    # Include slam_toolbox launch file
    rplidar_s2_launch_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rplidar, 'launch', 'rplidar_s2_launch.py')
        ),
        launch_arguments={
            'serial_port': lidar_port,
        }.items()
    )

    imu_bno055_launch_cmd = Node(
        package='imu_bno055',
        executable='bno055_i2c_node',
        name='bno055_i2c_node',
        output='screen',
        parameters=[{
            'device': '/dev/i2c-1',
            'frame_id': 'imu',
        }],
        remappings=[
            ('raw', 'imu/raw'),
            ('data', 'imu/data'),
            ('mag', 'imu/mag'),
            ('status', 'imu/status'),
            ('temp', 'imu/temp'),
        ]
    )
    

    # Create launch description and add actions
    ld = LaunchDescription()

    ld.add_action(declare_lidar_port)
    ld.add_action(rplidar_s2_launch_cmd)
    ld.add_action(imu_bno055_launch_cmd)


    return ld
