import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
# 선행 실행 명령어
# ros2 run turtlesim turtlesim_node

class MV_turtle(Node):
    def __init__(self):
        super().__init__("move_turtle")
        self.create_timer(0.1, self.timer_callback)
        self.pub = self.create_publisher(Twist, "turtle1/cmd_vel", 10)
        self.count = 0

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.0 + self.count
        msg.angular.z = 1.0
        self.pub.publish(msg)
        self.count += 0.01

def main(args=None):
    rclpy.init(args=args)
    node = MV_turtle()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End Turtle")

if __name__ == "__main__":
    main()
