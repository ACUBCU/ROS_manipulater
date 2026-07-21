import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class M_pub(Node):
    def __init__(self):
        super().__init__("mpub")
        self.create_timer(1, self.timer_callback)
        self.pub = self.create_publisher(String, "message1", 10)
        self.pub = self.create_publisher(String, "message2", 10)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f"{self.count} : First P"
        self.get_logger().info(msg.data)
        self.pub.publish(msg)
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = M_pub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("This is first program using by Class")

if __name__ == "__main__":
    main()
