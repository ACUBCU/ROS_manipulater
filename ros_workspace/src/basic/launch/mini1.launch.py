from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([Node(package="basic", executable="mpub"), 
                                Node(package="basic", executable="tpub"), 
                                Node(package="basic", executable="msub"),
                                Node(package="basic", executable="m2sub"),
                                Node(package="basic", executable="mtsub")])