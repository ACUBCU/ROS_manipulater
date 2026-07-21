import rclpy
from rclpy.node import Node

def timer_callback():
    Node("massage_pub").get_logger().info("First P")

def main(args=None):
    rclpy.init(args=args)
    node = Node("massage_pub")
    # timer
    node.create_timer(1, timer_callback)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("This is first program.")

if __name__ == "__main__":
    main()