from setuptools import find_packages, setup
import os

package_name = 'esense_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/launch.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Swathy Cheruvalath',
    maintainer_email='swathy.cheruvalath@smail.inf.h-brs.de',
    description='A ROS2 node that gets data from the Esense sensor and publishes it to a ROS topic using Lab Streaming Layer (LSL).',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'publish_esense_data_via_lsl = esense_pkg.esense_pkg:main'
        ],
    },
)
