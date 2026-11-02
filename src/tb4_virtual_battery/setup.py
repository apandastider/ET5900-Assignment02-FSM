from setuptools import setup
package_name = 'tb4_virtual_battery'
setup(
    name=package_name, version='0.2.1', packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Robotics Lab', maintainer_email='lab@example.edu',
    description='Virtual battery infrastructure for student FSM assignments',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'battery_sim=tb4_virtual_battery.battery_sim:main',
    ]},
)
