import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'physio_sensor'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'scripts'), ['scripts/cmds.sh']),
        (os.path.join('share', package_name, 'scripts'), ['scripts/main.sh']),
        (os.path.join('share', package_name, 'launch'), ['launch/launch.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Swathy Cheruvalath',
    maintainer_email='swathy.cheruvalath@smail.inf.h-brs.de',
    description='A ROS node that gets data from Esense sensors and publishes the acquired data to a ROS topic using Bluetooth.',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "publish_esense_data = physio_sensor.physio_sensor:main"
        ],
    },
)
