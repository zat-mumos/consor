# © 2026 Hochschule Bonn-Rhein-Sieg <https://www.h-brs.de/>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>.

from setuptools import find_packages, setup

package_name = 'movella_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/movella_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Paola Rangel',
    maintainer_email='paola.rangel@smail.inf.h-brs.de',
    description='A ROS2 node that gets data from the Movella sensor and publishes it to a ROS topic using Bluetooth',
    license='GPL-3.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'my_node = movella_pkg.my_node:main',
            'publisher_node_test = movella_pkg.publisher_node_test:main',
            'imu_batch_node = movella_pkg.imu_batch_node:main'
        ],
    },
)
