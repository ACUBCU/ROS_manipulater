import rclpy
import sys
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from rclpy.action import ActionClient
from user_interface.action._fibonacci import Fibonacci_GetResult_Response
from user_interface.action import Fibonacci
from rclpy.task import Future
from rclpy.action.client import ClientGoalHandle

import time

# ros2 run basic action_client [step]

class Action_client(Node):
    def __init__(self):
        super().__init__("action_client")
        self.action_client = ActionClient(self, Fibonacci, "fibonacci_server")

    def send_goal(self, step : str):
        goal_msg = Fibonacci.Goal()
        goal_msg.step = int(step)
        while not self.action_client.wait_for_server(timeout_sec=1):
            self.get_logger().info("Fibonacci server is not avaliable.")
        
        self.future = self.action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self.future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, msg: Fibonacci.Feedback):
        feedback: Fibonacci.Feedback = msg.feedback
        self.get_logger().info(f"{list(feedback.temp_seq)}")

    def goal_response_callback(self, future : Future):
        goal_handle: ClientGoalHandle = future.result()  # type: ignore
        if not goal_handle.accepted:
            self.get_logger().info("goal rejected!!")
            return
        self.get_logger().info("goal accepted!!")
        # result 가 왔을때의 callback 을 등록
        self.get_result_future = goal_handle.get_result_async()
        self.get_result_future.add_done_callback(self.get_result_callback)
        self.get_logger().info("end of goal response callback function!!")

    def get_result_callback(self, future : Future):
        result: Fibonacci_GetResult_Response = future.result()  # type: ignore
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"result: {list(result.result.seq)}")
        if result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("aborted!!")
        if result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("canceled!!")

def main(args=None):
    rclpy.init(args=args)
    node = Action_client()
    if len(sys.argv) != 2:
        print("사용법 : ros2 run [package] [node] [step: int]")
        return
    node.send_goal(sys.argv[1])

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