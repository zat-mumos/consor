from setuptools import find_packages, setup

package_name = 'zat_consor_sync'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Oviya Rajavel, Swathy Cheruvalath',
    maintainer_email='oviya.rajavel@smail.inf.h-brs.de, swathy.cheruvalath@smail.inf.h-brs.de',
    description='A ROS2 package for synchronising and publishing multiple consor wearable sensors.',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'zat_consor=zat_consor_sync.zat_consor_subscriber:main'
        ],
    },
)
