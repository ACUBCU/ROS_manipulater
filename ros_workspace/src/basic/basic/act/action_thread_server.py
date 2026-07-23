import rclpy
from rclpy.node import Node
from action_msgs.msg import GoalStatus
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from user_interface.action import Fibonacci
import time

# 멀티 스레딩을 위한 모듈 추가
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

class Action_server(Node):
    def __init__(self):
        super().__init__("action_server")
        
        # 재진입 가능한 콜백 그룹 설정
        self.callback_group = ReentrantCallbackGroup()
        
        # ActionServer에 callback_group 할당
        self.action_server = ActionServer(
            self, 
            Fibonacci, 
            "fibonacci_server", 
            execute_callback=self.execute_callback,
            callback_group=self.callback_group
        )

    def execute_callback(self, goal_handle : ServerGoalHandle):
        goal_id_str = ''.join('{:02x}'.format(x) for x in goal_handle.goal_id.uuid)
        
        goal : Fibonacci.Goal = goal_handle.request
        step = goal.step
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.temp_seq = [0,1]   
        
        for i in range(1, step):
            feedback_msg.temp_seq.append(feedback_msg.temp_seq[i] + feedback_msg.temp_seq[i-1])
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"{goal_id_str} : {goal_handle.status}")
            
            # 스레드 동시 처리 상태를 확인하기 위한 지연 시간
            time.sleep(1)

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.seq = feedback_msg.temp_seq
        return result

def main(args=None):
    rclpy.init(args=args)
    node = Action_server()

    # 다중 스레드 실행기 생성 (num_threads로 스레드 개수 지정)
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        # 단일 스레드용 rclpy.spin(node) 대신 executor.spin() 호출
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrrupt")
        # print("keyboard interrupt")
    finally:
        node.destroy_node()
    print("End action_server")

if __name__ == "__main__":
    main()