from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'basic'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob(os.path.join('launch','*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ldh',
    maintainer_email='ldh9632@gmail.com',
    description='knu ROS2 basic library',
    license='Apache 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "simple_pub = basic.simple_pub:main",
            "class_pub = basic.class_pub:main",
            "class_sub = basic.class_sub:main",
            "header_pub = basic.header_pub:main",
            "mpub = basic.mini1.mpub:main",
            "tpub = basic.mini1.tpub:main",
            "msub = basic.mini1.msub:main",
            "m2sub = basic.mini1.m2sub:main",
            "mtsub = basic.mini1.mtsub:main",
            "mv_turtle = basic.mv_turtle:main"
        ],
    },
)
