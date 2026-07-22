import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy
from rclpy.qos import qos_profile_default

class Qos_sub(Node):
    def __init__(self):
        super().__init__("massage_sub")
        # subscription callback
        self.create_subscription(String, "message", self.sub_callback, qos_profile_default)

    def sub_callback(self, msg : String):
        self.get_logger().info(msg.data)
        

def main(args=None):
    rclpy.init(args=args)
    node = Qos_sub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End Qos sub")

if __name__ == "__main__":
    main()