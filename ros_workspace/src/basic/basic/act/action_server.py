import rclpy
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from user_interface.action import Fibonacci
import time


class Action_server(Node):
    def __init__(self):
        super().__init__("action_server")
        self.action_server = ActionServer(self, Fibonacci, "fibonacci_server", 
                                            execute_callback=self.execute_callback)

    def execute_callback(self, goal_handle : ServerGoalHandle):
        self.get_logger().info(f"{goal_handle.status}")
        goal : Fibonacci.Goal = goal_handle.request
        step = goal.step
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.temp_seq = [0,1]   
        for i in range(1, step):
            feedback_msg.temp_seq.append(feedback_msg.temp_seq[i] + feedback_msg.temp_seq[i-1])
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"{goal_handle.status}")

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.seq = feedback_msg.temp_seq
        return result

def main(args=None):
    rclpy.init(args=args)
    node = Action_server()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End action_server")

if __name__ == "__main__":
    main()