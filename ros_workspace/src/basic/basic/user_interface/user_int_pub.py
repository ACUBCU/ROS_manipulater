import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from user_interface.msg import UserInt

class User_pub(Node):
    def __init__(self):
        super().__init__("user_pub")
        self.create_timer(1, self.timer_callback)
        #self.qos_profile = QoSProfile()
        self.pub = self.create_publisher(UserInt, "message", 10)

    def timer_callback(self):
        msg = UserInt()
        msg.header.frame_id = "test"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.user_int = 11
        msg.user_int2 = 22
        msg.user_int3 = 33
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = User_pub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End User_interface_pub")

if __name__ == "__main__":
    main()

# ros2 topic echo /message