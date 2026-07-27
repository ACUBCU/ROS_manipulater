import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import GripperCommand, GripperCommand_GetResult_Response
from rclpy.action import ActionClient
from sensor_msgs.msg import JointState
from rclpy.task import Future
from action_msgs.msg import GoalStatus

class M_pub(Node):
    def __init__(self):
        super().__init__("massage_pub")
        self.create_timer(2, self.timer_callback)
        self.pub = self.create_publisher(JointTrajectory, "arm_controller/joint_trajectory", 10)
        self.gripper_client = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.joint_state_subscription = self.create_subscription(JointState, "joint_states", self.joint_callback, 10)

        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.current_gripper_positon = 0.0
        self.joint_state_received = False
        self.count = True
        self.duration_sec = 2

    def timer_callback(self):
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "move_manipulator"
        msg.joint_names = ["joint1", "joint2","joint3", "joint4"]
        point = JointTrajectoryPoint()
        if self.count:
            point.positions = [-0.01999971971044071, -1.0798331127892098, 1.0813552197425864, 0.09969379940452348]
            self.move_gripper(0.019)
            self.count = False
        else:
            point.positions = [-0.01999971971044071, -0.33983311278920914, -1.298644780257415, 0.09969379940452348]
            self.move_gripper(-0.01)
            self.count = True

        seconds = int(self.duration_sec)
        nanoseconds = int((self.duration_sec - seconds)*1_000_000_000)

        point.time_from_start.sec = seconds
        point.time_from_start.nanosec = nanoseconds

        msg.points.append(point)
        self.pub.publish(msg)

    def joint_callback(self, msg: JointState):
        self.current_joint_position = msg.position

    def move_gripper(self, position: float, max_effort = 10.0, timeout_sec = 0.5):
        if not self.gripper_client.wait_for_server(timeout_sec=timeout_sec):
            self.get_logger().info("gripper controller Action can not find server.")
        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)
        send_goal_future = self.gripper_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_callback)

    def goal_callback(self, future: Future):
        self.goal_handle = future.result()  # type: ignore
        self.get_result_future = self.goal_handle.get_result_async()  # type: ignore
        self.get_result_future.add_done_callback(self.get_result_callback)
        self.get_logger().info("end of goal response callback function!!")

    def feedback_callback(self, msg: GripperCommand.Impl.FeedbackMessage):
        feedback: GripperCommand.Feedback = msg.feedback
        self.get_logger().info(f"{feedback.position}")

    def get_result_callback(self, future: Future):
        result: GripperCommand_GetResult_Response = (
            future.result()  # type: ignore
        )
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"result: {result.result.position}")
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("aborted!!")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("canceled!!")

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
    print("END move_manipulator")

if __name__ == "__main__":
    main()
