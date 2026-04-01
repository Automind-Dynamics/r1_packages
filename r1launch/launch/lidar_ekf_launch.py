#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

import rclpy
import os


def wait_for_topics(context):
    """
    Wait for wheel_odom + IMU /data before launching EKF.
    Called AFTER TimerAction delay.
    """
    rclpy.init()
    node = rclpy.create_node("ekf_topic_waiter")

    required_topics = ['/wheel_odom', '/imu/data']
    print("[EKF LAUNCH] Waiting for topics:", required_topics)

    while rclpy.ok():
        topics = [t[0] for t in node.get_topic_names_and_types()]
        if all(req in topics for req in required_topics):
            print("[EKF LAUNCH] All required topics available ✓")
            break
        rclpy.spin_once(node, timeout_sec=0.2)

    node.destroy_node()
    rclpy.shutdown()

    # Once topics exist → launch EKF
    ekf_launch_file = os.path.join(
        get_package_share_directory('robot_localization'),
        'launch',
        'ekf.launch.py'
    )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(ekf_launch_file),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time')
            }.items()
        )
    ]


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    rplidar_launch_file = os.path.join(
        get_package_share_directory('rplidar_ros'),
        'launch',
        'rplidar_s2_launch.py'
    )

    return LaunchDescription([

        # --------------------------------------------------
        # 0️⃣ LAUNCH ARGUMENTS
        # --------------------------------------------------
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulated time'
        ),

        # --------------------------------------------------
        # 1️⃣ LIDAR FIRST
        # --------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rplidar_launch_file),
            launch_arguments={'use_sim_time': use_sim_time}.items()
        ),

        # --------------------------------------------------
        # 2️⃣ IMU SECOND
        # --------------------------------------------------
        Node(
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
        ),

        # --------------------------------------------------
        # 3️⃣ STATIC TF THIRD
        # --------------------------------------------------
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_laser',
            arguments=['0.07215', '0.0', '0.13340',
                       '0.0', '3.14159', '-3.14159',
                       'base_link', 'laser']
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_imu',
            arguments=['0.07215', '0.0', '0.07730',
                       '0.0', '0.0', '0.0',
                       'base_link', 'imu']
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera',
            arguments=['0.15065', '0.0', '0.08505',
                       '0.0', '0.0', '0.0',
                       'base_link', 'camera_link']
        ),

        # --------------------------------------------------
        # 4️⃣ EKF LAST (Run only after topics exist)
        #    Add delay → Prevent blocking
        # --------------------------------------------------
        TimerAction(
            period=2.0,   # wait 2 seconds before checking
            actions=[
                OpaqueFunction(function=wait_for_topics)
            ]
        ),
    ])

