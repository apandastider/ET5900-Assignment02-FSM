from setuptools import setup
from glob import glob
package_name='tb4_fsm_assignment'
setup(name=package_name,version='0.1.0',packages=[package_name],
 data_files=[('share/ament_index/resource_index/packages',['resource/'+package_name]),
 ('share/'+package_name,['package.xml']),
 ('share/'+package_name+'/launch',glob('launch/*.launch.py')),
 ('share/'+package_name+'/config',glob('config/*.yaml')),
 ('share/'+package_name+'/docs',glob('docs/*.md')),
 ('share/'+package_name+'/maps',glob('maps/*'))],
 install_requires=['setuptools','PyYAML'],zip_safe=True,
 maintainer='Course instructor',maintainer_email='instructor@example.invalid',
 description='ET5900 FSM assignment scaffold and infrastructure',license='Apache-2.0',
 entry_points={'console_scripts':[
  'nav2_twist_bridge = tb4_fsm_assignment.nav2_twist_bridge:main',
  'station_markers = tb4_fsm_assignment.station_markers:main',
  'student_fsm = tb4_fsm_assignment.student_fsm:main',
 ]})
