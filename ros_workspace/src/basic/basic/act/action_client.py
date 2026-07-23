import rclpy
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from rclpy.action.server import ServerGoalHandle
from user_interface.action import Fibonacci
from rclpy.task import Future
from rclpy.action.client import ClientGoalHandle

import time

# ros2 action send_goal /fibonacci_server user_interface/action/Fibonacci "{step: 10}" --feedback

class Action_client(Node):
    def __init__(self):
        super().__init__("action_client")
        self.action_client = ActionClient(self, Fibonacci, "fibonacci_server")

    def send_goal(self, step : str):
        goal_msg = Fibonacci.Goal()
        goal_msg.step =  step

        self.action_client.wait_for_server(timeout_sec=1)
        self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)

    def feedback_callback(self, msg: Fibonacci.Feedback):
        


        goal_handle: ClientGoalHandle = future.result()
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)
        pass

    def goal_response_callback(self, future : Future):
        pass

    def get_result_callback(self, future : Future):
        pass

def main(args=None):
    rclpy.init(args=args)
    node = Action_client()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End service_server")

if __name__ == "__main__":
    main()