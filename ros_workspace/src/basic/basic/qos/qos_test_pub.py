import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy
from rclpy.qos import qos_profile_default

class Qos_pub(Node):
    def __init__(self):
        super().__init__("massage_pub")
        self.create_timer(1, self.timer_callback)
        #self.qos_profile = QoSProfile()
        self.pub = self.create_publisher(String, "message", qos_profile_default)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f"{self.count} : First P"
        self.get_logger().info(msg.data)
        self.pub.publish(msg)
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = Qos_pub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End Qos_pub")

if __name__ == "__main__":
    main()
