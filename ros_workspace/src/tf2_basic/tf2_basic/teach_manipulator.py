import os
import select
import sys
import termios
import tty

import rclpy
import yaml
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import SetBool


class TeachManipulator(Node):
    JOINT_NAMES = ["joint1", "joint2", "joint3", "joint4"]
    GRIPPER_JOINT = "gripper_left_joint"
    JOINT_LIMITS = {
        "joint1": [-3.14159265359, 3.14159265359],
        "joint2": [-1.5, 1.5],
        "joint3": [-1.5, 1.4],
        "joint4": [-1.7, 1.97],
    }
    GRIPPER_LIMITS = [-0.011, 0.02]

    def __init__(self):
        super().__init__("teach_manipulaotr")
        self.joint_state_subscription = self.create_subscription(
            JointState, "/joint_states", self.joint_state_callback, 10
        )
        self.torqu_service_client = self.create_client(
            SetBool, "dynamixel_hardware_interface/set_dxl_torque"
        )
        self.torqu_service_client.wait_for_service(timeout_sec=1.0)
        
        self.set_torque(False)
        
        self.create_timer(0.3, self.poll_keyboard)

        self._latest_positions: dict[str, float] = {}
        self._stdin_fd = None
        self._quit_requested = False
        self._steps = []
        self._step_duration = 1.0
        self._step_pause = 0.2
        self._pattern_name = "test"
        self._stdin_fd = sys.stdin.fileno()
        self._terminal_settings = termios.tcgetattr(self._stdin_fd)
        tty.setcbreak(self._stdin_fd)

    def set_torque(self, enable: bool):
        request = SetBool.Request()
        request.data = enable
        future = self.torqu_service_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
        response = future.result()
        state_str = "토크 걸기" if enable else "토크 해제"
        if response is not None and response.success:
            self.get_logger().info(f"{state_str} 성공")
        else:
            self.get_logger().info(f"{state_str} 실패")

    def joint_state_callback(self, msg: JointState):
        available = {
            name: float(msg.position[index])
            for index, name in enumerate(msg.name)
            if index < len(msg.position)
        }
        self._latest_positions = {
            name: available[name] for name in self.JOINT_NAMES + [self.GRIPPER_JOINT] if name in available
        }

    def poll_keyboard(self):
        if self._stdin_fd is None or self._quit_requested:
            return
        readable, _, _ = select.select([self._stdin_fd], [], [], 0.0)
        if not readable:
            return
        key = os.read(self._stdin_fd, 1)
        if key == b" ":
            self.capture_pose()
        if key.lower() == b"q":
            self.request_quit()

    def capture_pose(self):
        try:
            positions = [round(self._latest_positions[name], 6) for name in self.JOINT_NAMES]
            gripper = [round(self._latest_positions[self.GRIPPER_JOINT], 6)]
            self._steps.append(
                {
                    "positions": positions,
                    "gripper": gripper,
                    "duration": self._step_duration,
                    "pause": self._step_pause,
                }
            )
            self._write_yaml()
            self.get_logger().info("현재 자세 저장 완료")
        except KeyError as e:
            self.get_logger().warn(f"조인트 데이터 수신 대기 중: {e}")

    def _write_yaml(self):
        document = {
            "joint_names": self.JOINT_NAMES,
            "joint_limits": self.JOINT_LIMITS,
            "patterns": [{"name": self._pattern_name, "steps": self._steps}],
        }
        with open("teach_data.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(document, f, allow_unicode=True, sort_keys=False)

    def request_quit(self):
        print("exit")
        self._quit_requested = True


def main(args=None):
    rclpy.init(args=args)
    node = TeachManipulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 1. 다른 로직에 의해 블로킹되기 전에 터미널 설정을 최우선으로 복구
        if hasattr(node, '_stdin_fd') and node._stdin_fd is not None:
            try:
                termios.tcsetattr(node._stdin_fd, termios.TCSADRAIN, node._terminal_settings)
            except Exception:
                pass

        # 2. 터미널 복구 완료 후 하드웨어 토크 재활성화 시도
        try:
            node.set_torque(True)
        except Exception:
            pass
        
        # 3. 노드 안전 종료
        node.destroy_node()
        if rclpy.ok():
            rclpy.try_shutdown()


if __name__ == "__main__":
    main()