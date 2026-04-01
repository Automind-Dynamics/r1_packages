from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os

def generate_launch_description():
    # ------------------------------------------------------------------
    # 1.  Where your database lives (change the path if you moved it)
    # ------------------------------------------------------------------
    db_path = os.path.expanduser('~/.ros/rtabmap.db')   # default location
    # db_path = '/full/path/to/your/stereo_map.db'      # <-- edit if needed

    # ------------------------------------------------------------------
    # 2.  Parameters – same as mapping, but with localization flags
    # ------------------------------------------------------------------
    parameters = [{
        'frame_id': 'camera_link',
        'subscribe_stereo': True,
        'subscribe_odom_info': True,
        'wait_imu_to_init': True,

        # --- localization-only switches ---
        'database_path':  db_path,
        'Mem/IncrementalMemory': 'false',    # do NOT add new nodes to map
        'Mem/InitWMWithAllNodes': 'true',    # load entire map into WM
    }]

    # ------------------------------------------------------------------
    # 3.  Remappings – identical to the mapping launch file
    # ------------------------------------------------------------------
    remappings = [
        ('imu', '/imu/data'),
        ('left/image_rect',  '/camera/camera/infra1/image_rect_raw'),
        ('left/camera_info', '/camera/camera/infra1/camera_info'),
        ('right/image_rect', '/camera/camera/infra2/image_rect_raw'),
        ('right/camera_info','/camera/camera/infra2/camera_info'),
        ('depth/image',      '/camera/camera/aligned_depth_to_color/image_raw')
    ]

    return LaunchDescription([
        # ------------- IMU filter (unchanged) -------------
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

        # ------------- Stereo odometry (unchanged) -------------
        Node(
            package='rtabmap_odom',
            executable='stereo_odometry',
            name='stereo_odometry',
            output='screen',
            parameters=parameters,
            remappings=remappings
        ),

        # ------------- RTAB-Map in localization mode -------------
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=parameters,
            remappings=remappings,
            # *** NO arguments=['-d'] ***
        ),

        # ------------- RTAB-Map visualizer (optional) -------------
        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            name='rtabmap_viz',
            output='screen',
            parameters=parameters,
            remappings=remappings
        ),
    ])
