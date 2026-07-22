import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter


class TParam(Node):
    def __init__(self):
        super().__init__("tparam")
        self.declare_parameter('my_param','parameter in Class Node made by me')
        self.my_param = self.get_parameter('my_param').get_parameter_value().string_value

        self.create_timer(1, self.timer_callback)
        self.add_on_set_parameters_callback(self.parameter_callback)

    def timer_callback(self):
        self.get_logger().info(self.my_param)

    def parameter_callback(self, params: list[Parameter]):
        for param in params:
            if param.name == 'my_param':
                self.my_param = param.value

        return SetParametersResult(successful = True)

def main(args=None):
    rclpy.init(args=args)
    node = TParam()

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

# ros2 param set /tparam my_param "변경할 파라미터명"