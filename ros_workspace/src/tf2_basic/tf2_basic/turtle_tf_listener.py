import math
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from tf2_ros.transform_listener import TransformListener
from tf2_ros.buffer import Buffer
from tf2_ros.transform_broadcaster import TransformBroadcaster
from turtlesim.msg import Pose
from turtlesim.srv import Spawn


def euler_to_quaternion_pure(roll, pitch, yaw):
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return qx, qy, qz, qw


class TurtleTfListener(Node):
    def __init__(self):
        super().__init__("turtle_tf_listener")
        
        self.target_frame = "turtle1"
        self.follower_frame = "turtle2"
        
        # 1. turtle2 생성을 위한 Service Client
        self.spawn_cli = self.create_client(Spawn, 'spawn')
        while not self.spawn_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not available, waiting...')
        
        self.req = Spawn.Request()
        self.req.name = self.follower_frame
        self.req.x = 2.0
        self.req.y = 2.0
        self.req.theta = 0.0
        self.future = self.spawn_cli.call_async(self.req)

        # 2. turtle2 TF 발행을 위한 Subscriber 및 Broadcaster 설정
        self.tf_broadcaster = TransformBroadcaster(self)
        self.create_subscription(
            Pose, 
            f"{self.follower_frame}/pose", 
            self.pose_callback, 
            10
        )

        # 3. 목표 추종을 위한 TF Listener 설정
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # 4. 제어 명령 Publisher 설정
        self.cmd_vel_pub = self.create_publisher(Twist, f'{self.follower_frame}/cmd_vel', 10)

        # 5. 제어 타이머 설정 (1.0초 주기)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def pose_callback(self, msg: Pose):
        # turtle2의 현재 위치를 TF 트리(world -> turtle2)로 지속적으로 발행
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "world"
        t.child_frame_id = self.follower_frame
        
        x, y, z, w = euler_to_quaternion_pure(0.0, 0.0, msg.theta)
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0
        t.transform.rotation.x = x
        t.transform.rotation.y = y
        t.transform.rotation.z = z
        t.transform.rotation.w = w
        
        self.tf_broadcaster.sendTransform(t)

    def timer_callback(self):
        try:
            # turtle2 프레임 기준 turtle1의 위치 룩업
            t = self.tf_buffer.lookup_transform(
                self.follower_frame, 
                self.target_frame, 
                rclpy.time.Time()
            )
            
            x = t.transform.translation.x
            y = t.transform.translation.y
            
            distance = math.sqrt(x**2 + y**2)
            angle = math.atan2(y, x)
            
            msg = Twist()
            
            # 정지 조건
            if distance < 0.5:
                msg.linear.x = 0.0
                msg.angular.z = 0.0
            else:
                msg.linear.x = 0.5 * distance
                msg.angular.z = 1.0 * angle

            self.cmd_vel_pub.publish(msg)

        except Exception as e:
            self.get_logger().info(f"TF 룩업 대기 중: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = TurtleTfListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()