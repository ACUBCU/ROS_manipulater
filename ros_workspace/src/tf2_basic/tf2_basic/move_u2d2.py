import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time

class MoveU2D2(Node):
    def __init__(self):
        super().__init__('move_u2d2')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.start_time = time.time()

    def timer_callback(self):
        # 전체 기본 속도 변수
        now = (time.time() - self.start_time) * 0.5
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        msg.name = [
            'head_swivel',
            'shoulder_joint',
            'elbow_joint',
            'gripper_extension',
            'left_front_wheel_joint',
            'left_back_wheel_joint',
            'right_front_wheel_joint',
            'right_back_wheel_joint',
            'left_gripper_joint',
            'right_gripper_joint'
        ]
        
        head_pos = math.sin(now) * 1.5
        shoulder_pos = math.sin(now) * 1.0
        elbow_pos = math.cos(now) * 1.0
        wheel_pos = now * 1.5
        
        # 그리퍼(막대기, 손가락) 부위만 움직임 주기를 6배 빠르게 가속(now * 6.0)
        gripper_ext_pos = -0.19 + 0.19 * math.sin(now * 6.0)
        gripper_finger_pos = 0.274 + 0.274 * math.cos(now * 6.0)

        msg.position = [
            head_pos,
            shoulder_pos,
            elbow_pos,
            gripper_ext_pos,
            wheel_pos,
            wheel_pos,
            wheel_pos,
            wheel_pos,
            gripper_finger_pos,
            gripper_finger_pos
        ]
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MoveU2D2()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()