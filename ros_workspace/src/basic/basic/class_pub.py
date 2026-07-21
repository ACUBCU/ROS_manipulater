import rclpy
from rclpy.node import Node

class M_pub(Node):
    def __init__(self):
        super().__init__("massage_pub")
        self.create_timer(1, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        self.get_logger().info(f"{self.count} : First P")
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