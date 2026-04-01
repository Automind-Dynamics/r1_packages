from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([

        # --- BNO055 IMU Node (100 Hz internal) ---
        Node(
            package='imu_bno055',
            executable='bno055_i2c_node',
            name='bno055_imu',
            output='screen',
            parameters=[{
                'device': '/dev/i2c-1',
                'frame_id': 'imu',
                'topic': '/imu_bno055/data'
            }],
            remappings=[
                ('data', '/imu_bno055/data')
            ]
        ),

        # --- Throttle IMU from 100 Hz → 5 Hz ---
        Node(
            package='topic_tools',
            executable='throttle',
            name='imu_throttle',
            arguments=[
                'messages',               # throttle type
                '/imu_bno055/data',       # input
                '5.0',                    # output rate (Hz)
                '/imu_bno055/data_slow'    # output topic
            ]
        ),

        # --- Static TF ---
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_imu',
            arguments=[
                '0.07215', '0.0', '0.07730',
                '0', '0', '0',
                'base_link', 'imu'
            ]
        ),
    ])
