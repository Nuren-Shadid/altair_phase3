import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'altair_phase3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nuren',
    maintainer_email='nuren@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        	'telemetry_pub = altair_phase3.telemetry_pub:main',
    		'telemetry_sub = altair_phase3.telemetry_sub:main',
    		'driving_menu = altair_phase3.driving_menu:main',
    		'mission_node = altair_phase3.mission_node:main',
        ],
    },
)
