import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    pkg_slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    pkg_r1slam = get_package_share_directory('r1_slam')
    pkg_r1teleop = get_package_share_directory('r1_teleop')

    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='False')
    autostart = LaunchConfiguration('autostart', default='True')
    
    slam_toolbox_params = os.path.join(pkg_r1slam, 'config', 'mapper_params_online_async.yaml')
    slam_rviz_config = os.path.join(pkg_r1slam, 'config', 'slam_default.rviz')
    teleop_joy_params = os.path.join(pkg_r1slam, 'config', 'slam_teleop_joy.yaml')

    run_teleop_joy = LaunchConfiguration('run_teleop_joy')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically start the slam_toolbox stack'
    )

    declare_teleop_joy = DeclareLaunchArgument(
        'run_teleop_joy',
        default_value='False',
        description='Enable Teleop Joy Node with limited Velocity'
    )


    # Include slam_toolbox launch file
    slam_toolbox_launch_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox_dir, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_toolbox_params,
        }.items()
    )
    
    teleop_joy_launch_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_r1teleop, 'launch', 'r1_teleop_joy.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'joy_params': teleop_joy_params,
        }.items(),
        condition=IfCondition(run_teleop_joy)
    )

    # Launch RViz
    rviz_launch_cmd = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=[
            '-d', slam_rviz_config
        ]
    )

    # Static transform publisher
    static_transform_publisher_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )

    # Create launch description and add actions
    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_autostart)
    ld.add_action(declare_teleop_joy)
    ld.add_action(slam_toolbox_launch_cmd)
    ld.add_action(teleop_joy_launch_cmd)
    ld.add_action(rviz_launch_cmd)
    ld.add_action(static_transform_publisher_node)

    return ld
