XM430-W350  

**사전작업 코드**  
cmd
* usbipd list -> BUSID 확인
* usbipd bind --busid {Bus ID}
* usbipd attach --wsl Ubuntu-24.04 --busid {BUSID} -a  
* usbipd attach --wsl Ubuntu-24.04 --busid 1-6 -a  
 
Terminal
* ros2 launch open_manipulator_bringup open_manipulator_x.launch.py
* ls /dev/ttyUSB* -> portname 변경될 때 사용
* ros2 launch open_manipulator_bringup open_manipulator_x.launch.py port_name:={/dev/ttyUSB*}

**패키지**
* workspace/src 에서 실행
* ros2 pkg create --build-type ament_python {pkg_name}

**Telelop 수동 조작**
- ros2 run open_manipulator_teleop open_manipulator_x_teleop
- 1/q, 2/w, 3/e, 4/r, o/p

**moveit**  
* ros2 launch open_manipulator_moveit_config open_manipulator_x_moveit.launch.py use_sim:=true

**Gazebo**
* gz sim
* ros2 launch open_manipulator_bringup open_manipulator_x_gazebo.launch.py
