from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Declare launch arguments
    device = LaunchConfiguration('device', default='/dev/ttyACM0')
    baudrate = LaunchConfiguration('baudrate', default='115200')

    return LaunchDescription([
        # Declare device argument
        DeclareLaunchArgument(
            'device',
            default_value='/dev/ttyACM0',
            description='Serial device for micro-ROS agent (e.g., /dev/ttyACM0)'
        ),
        # Declare baudrate argument
        DeclareLaunchArgument(
            'baudrate',
            default_value='115200',
            description='Baud rate for serial communication'
        ),
        # micro-ROS agent node
        ExecuteProcess(
            cmd=['ros2', 'run', 'micro_ros_agent', 'micro_ros_agent', 'serial', '--dev', device, '-b', baudrate],
            output='screen'
        )
    ])
