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


# --------------------------------------------------------------
#  EKF Topic Waiter
# --------------------------------------------------------------
def wait_for_ekf_topics(context):
    """
    Wait for wheel_odom + IMU /data before launching EKF.
    """

    rclpy.init()
    node = rclpy.create_node("ekf_topic_waiter")

    required_topics = ['/wheel_odom', '/data']
    print("[EKF LAUNCH] Waiting for topics:", required_topics)

    while rclpy.ok():
        topics = [t[0] for t in node.get_topic_names_and_types()]
        if all(req in topics for req in required_topics):
            print("[EKF LAUNCH] ✓ EKF required topics found")
            break
        rclpy.spin_once(node, timeout_sec=0.2)

    node.destroy_node()
    rclpy.shutdown()

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


# --------------------------------------------------------------
#  SLAM Toolbox Topic Waiter
# --------------------------------------------------------------
def wait_for_slam_topics(context):
    """
    Wait for SLAM topics: /odometry/filtered + /scan
    """

    rclpy.init()
    node = rclpy.create_node("slam_topic_waiter")

    required_topics = ['/odometry/filtered', '/scan']
    print("[SLAM LAUNCH] Waiting for topics:", required_topics)

    while rclpy.ok():
        topics = [t[0] for t in node.get_topic_names_and_types()]
        if all(req in topics for req in required_topics):
            print("[SLAM LAUNCH] ✓ SLAM required topics found")
            break
        rclpy.spin_once(node, timeout_sec=0.2)

    node.destroy_node()
    rclpy.shutdown()

    slam_file = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    return [
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_file),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time')
            }.items()
        )
    ]


# --------------------------------------------------------------
#  MAIN LAUNCH DESCRIPTION
# --------------------------------------------------------------
def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    rplidar_launch_file = os.path.join(
        get_package_share_directory('rplidar_ros'),
        'launch',
        'rplidar_s2_launch.py'
    )

    return LaunchDescription([

        # --------------------------------------------------
        # 0️⃣ Launch args
        # --------------------------------------------------
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),

        # --------------------------------------------------
        # 1️⃣ IMU FIRST
        # --------------------------------------------------
        Node(
            package='imu_bno055',
            executable='bno055_i2c_node',
            name='bno055_i2c_node',
            output='screen',
            parameters=[{
                'device': '/dev/i2c-1',
                'frame_id': 'imu',
                'topic': '/data'
            }]
        ),

        # --------------------------------------------------
        # 2️⃣ LIDAR SECOND
        # --------------------------------------------------
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rplidar_launch_file),
            launch_arguments={'use_sim_time': use_sim_time}.items()
        ),

        # --------------------------------------------------
        # 3️⃣ STATIC TF THIRD
        # --------------------------------------------------
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_laser',
            arguments=[
                '0.07215', '0.0', '0.13340',
                '0.0', '3.14159', '-3.14159',
                'base_link', 'laser'
            ]
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_imu',
            arguments=[
                '0.07215', '0.0', '0.07730',
                '0.0', '0.0', '0.0',
                'base_link', 'imu'
            ]
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera',
            arguments=[
                '0.15065', '0.0', '0.08505',
                '0.0', '0.0', '0.0',
                'base_link', 'camera_link'
            ]
        ),

        # --------------------------------------------------
        # 4️⃣ EKF (wait for wheel_odom + /data)
        # --------------------------------------------------
        TimerAction(
            period=2.0,
            actions=[
                OpaqueFunction(function=wait_for_ekf_topics)
            ]
        ),

        # --------------------------------------------------
        # 5️⃣ SLAM Toolbox (wait for /odometry/filtered + /scan)
        # --------------------------------------------------
        TimerAction(
            period=5.0,  # give EKF time to start publishing
            actions=[
                OpaqueFunction(function=wait_for_slam_topics)
            ]
        ),
    ])

