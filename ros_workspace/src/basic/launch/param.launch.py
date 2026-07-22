from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
import os
from launch.actions import DeclareLaunchArgument
from ament_index_python import get_package_share_directory

# ros2 launch basic param.launch.py param_dir:=my_param2.yaml

def generate_launch_description():
    param_dir = LaunchConfiguration('param_dir', default=os.path.join(get_package_share_directory('basic'), 
                                    'param','my_param.yaml'))
    return LaunchDescription([DeclareLaunchArgument('param_dir', default_value=param_dir,
                                                    description='launch parameter save option'),
                                Node(package="basic", executable="my_param",
                                 parameters=[param_dir]),])