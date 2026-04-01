from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get the launch directory for realsense2_camera
    realsense_launch_dir = os.path.join(
        get_package_share_directory('realsense2_camera'), 'launch'
    )

    # RTAB-Map parameters
    parameters = [{
        'frame_id': 'camera_link',
        'subscribe_stereo': True,
        'subscribe_odom_info': True,
        'wait_imu_to_init': True
    }]

    # RTAB-Map remappings
    remappings = [
        ('imu', '/imu/data'),
        ('left/image_rect', '/camera/camera/infra1/image_rect_raw'),
        ('left/camera_info', '/camera/camera/infra1/camera_info'),
        ('right/image_rect', '/camera/camera/infra2/image_rect_raw'),
        ('right/image_rect', '/camera/camera/color/image_raw'),
        ('depth/image', '/camera/camera/aligned_depth_to_color/image_raw'),
        ('right/camera_info', '/camera/camera/infra2/camera_info')
    ]

    return LaunchDescription([
        # Declare arguments
        DeclareLaunchArgument(
            'unite_imu_method',
            default_value='2',
            description='0-None, 1-copy, 2-linear_interpolation.'
        ),

        # Launch RealSense camera with specified parameters
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(realsense_launch_dir, 'rs_launch.py')
            ),
            launch_arguments={
                'enable_gyro': 'true',
                'enable_accel': 'true',
                'unite_imu_method': '1',
                'enable_infra1': 'true',
                'enable_infra2': 'true',
                'enable_sync': 'true'
            }.items()
        ),

        # RTAB-Map stereo odometry node
        Node(
            package='rtabmap_odom',
            executable='stereo_odometry',
            name='stereo_odometry',
            output='screen',
            parameters=parameters,
            remappings=remappings
        ),

        # RTAB-Map SLAM node
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=parameters,
            remappings=remappings,
            arguments=['-d']  # Delete database on start
        ),

        # RTAB-Map visualization node
        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            name='rtabmap_viz',
            output='screen',
            parameters=parameters,
            remappings=remappings
        ),

        # IMU filter node
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            name='imu_filter_madgwick_node',
            output='screen',
            parameters=[{
                'use_mag': False,
                'world_frame': 'enu',
                'publish_tf': False
            }],
            remappings=[('imu/data_raw', '/camera/camera/imu')]
        ),
    ])
