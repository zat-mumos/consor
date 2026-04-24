from setuptools import find_packages, setup
import os

package_name = 'emotibit_sdk'

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
    maintainer='Swathy Cheruvalath',
    maintainer_email='swathy.cheruvalath@smail.inf.h-brs.de',
    description='This ROS2 package uses BrainFlow SDK to publish the EmotiBit data',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'publish_emotibit_data_with_sdk = emotibit_sdk.emotibit_sdk:main',
            'combine_emotibit_modalities = emotibit_sdk.combine_emotibit:main'
        ],
    },
)
