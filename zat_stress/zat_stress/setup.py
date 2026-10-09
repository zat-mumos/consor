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
from glob import glob
import os

package_name = 'zat_stress'

datafiles=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ]


for path in glob('vendor/**/*', recursive=True):
    install_dir = os.path.join('share', package_name, os.path.dirname(path))
    if os.path.isfile(path):
        datafiles.append((install_dir, [path]))

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=datafiles,
    py_modules=['vendor/CNN_UQ', 'vendor/dialogue_manager', 'vendor/eda_features'],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Swathy Cheruvalath',
    maintainer_email='swathy.cheruvalath@smail.inf.h-brs.de',
    description='This is a package that extracts features, infers labels and provides responses based on these predictions.',
    license='GPL-3.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'extract_features = zat_stress.extract_features:main',
            'predict_labels = zat_stress.predict_labels:main',
            'get_responses = zat_stress.get_response:main'
        ],
    },
)
