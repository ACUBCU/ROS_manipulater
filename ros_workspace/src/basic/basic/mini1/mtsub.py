import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from std_msgs.msg import String

class M_sub(Node):
    def __init__(self):
        super().__init__("mtsub")
        # subscription callback
        self.create_subscription(Header, "time", self.sub_header_callback, 10)
        self.create_subscription(String, "message1", self.sub_msg_callback, 10)
    def sub_header_callback(self, msg : Header):
        self.get_logger().info(str(msg))
    def sub_msg_callback(self, msg : String):
        self.get_logger().info(msg.data)
        

def main(args=None):
    rclpy.init(args=args)
    node = M_sub()

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