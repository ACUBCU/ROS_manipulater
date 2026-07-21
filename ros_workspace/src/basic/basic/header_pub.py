import rclpy
from rclpy.node import Node
from std_msgs.msg import Header

class H_pub(Node):
    def __init__(self):
        super().__init__("header_pub")
        self.create_timer(0.1, self.timer_callback)
        self.pub = self.create_publisher(Header, "time", 10)

    def timer_callback(self):
        msg = Header()
        msg.frame_id = "time_test"
        msg.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = H_pub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("This is timestamp program using by Header")

if __name__ == "__main__":
    main()
