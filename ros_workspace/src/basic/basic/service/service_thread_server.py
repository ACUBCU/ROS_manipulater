import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from user_interface.srv import AddAndOdd
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import threading

class Service_server(Node):
    def __init__(self):
        super().__init__("service_server")
        self.lock = threading.Lock()
        self.callback_group = ReentrantCallbackGroup()
        self.create_service(AddAndOdd, "add_server", self.add_callback, callback_group=self.callback_group)

    def add_callback(self, request : AddAndOdd.Request, response : AddAndOdd.Response):
        with self.lock:
            response.sum = request.inta + request.intb
        time.sleep(2)
        if response.sum % 2:
            response.odd = "True"
        else:
            response.odd = "False"
        return response

def main(args=None):
    rclpy.init(args=args)
    node = Service_server()

    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
        executor.shutdown()
    print("End service_server")

if __name__ == "__main__":
    main()