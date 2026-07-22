import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.parameter import Parameter
from rclpy.parameter_client import AsyncParameterClient

class ParamAsync(Node):
    def __init__(self):
        super().__init__("tparamAsync")
        self.target_node_name = "/tparam"
        self.parameter_client = AsyncParameterClient(self, self.target_node_name)
        self.create_timer(1.0, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        parameter = Parameter(name="my_param", type_=Parameter.Type.STRING, value=f"외부 노드에서 변경한 값 : {self.count}")
        self.count += 1
        future = self.parameter_client.set_parameters([parameter])
        future.add_done_callback(self.parameter_result_callback)

    def parameter_result_callback(self, future):
        result = future.result()

        print(result)

def main(args=None):
    rclpy.init(args=args)
    node = ParamAsync()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("async param")

if __name__ == "__main__":
    main()

# 선행 명령 : ros2 run basic my_param