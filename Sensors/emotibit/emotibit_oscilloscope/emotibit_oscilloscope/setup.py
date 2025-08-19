from setuptools import find_packages, setup
import os

package_name = 'emotibit_oscilloscope'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/launch.py']),
        (os.path.join('share', package_name, 'config'), ['config/emotibit_params.yaml'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='swathy',
    maintainer_email='swathy.cheruvalath@smail.inf.h-brs.de',
    description='This ROS2 package uses pylsl to publish EmotiBit data (requires EmotiBit Oscilloscope)',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'publish_emotibit_data_with_oscilloscope = emotibit_oscilloscope.emotibit_osc:main'
        ],
    },
)
