import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from user_interface.srv import AddAndOdd
import time

class Service_client(Node):
    def __init__(self):
        super().__init__("service_client")
        self.client = self.create_client(AddAndOdd, "add_server")
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Service is not avaliable.")
        
        self.request = AddAndOdd.Request()
        self.create_timer(3, self.send_request)
        self.create_timer(1, self.update)
        self.count = 0

    def send_request(self):
        self.request.inta = 4
        self.request.intb = 8 + self.count
        self.get_logger().info(f"{self.request.inta}, {self.request.intb} 요청")
        self.count += 1
        self.future = self.client.call_async(self.request)
        self.future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        response : AddAndOdd.Response = future.result()
        self.get_logger().info(f"{response.sum}, {response.odd}.")

    def update(self):
        self.get_logger().info("Update.")


def main(args=None):
    rclpy.init(args=args)
    node = Service_client()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End service_client")

if __name__ == "__main__":
    main()