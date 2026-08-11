import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray

class RobotControlNode(Node):
    def __init__(self):
        super().__init__('robot_control_node')
        
        # 1. aruco_detect가 발행한 ID 리스트 구독
        self.sub = self.create_subscription(
            Int32MultiArray,
            '/detected_aruco_ids',
            self.id_callback,
            10
        )
        
        self.task_performed = False # 중복 동작 방지
        self.get_logger().info('로봇 제어 노드 대기 중... 마커 정보를 기다립니다.')

    def id_callback(self, msg):
        if self.task_performed:
            return

        ids = msg.data
        if len(ids) < 2:
            return

        # 2. 로봇이 직접 큐브(0~5)와 목적지(6~10) 구분
        cube_ids = [m_id for m_id in ids if 0 <= m_id <= 5]
        place_ids = [m_id for m_id in ids if 6 <= m_id <= 10]

        if cube_ids and place_ids:
            target_cube = cube_ids[0]
            target_place = place_ids[0]
            
            self.get_logger().info(f'작업 시작: 큐브({target_cube})를 목적지({target_place})로 이동')
            self.task_performed = True
            
            # 3. 여기서 로봇 동작 함수 호출
            self.execute_pick_and_place(target_cube, target_place)

    def execute_pick_and_place(self, cube_id, place_id):
        # 여기에 고정 좌표를 이용한 로봇 제어 코드 작성
        # 예: self.move_to_position(self.cube_coords[cube_id])
        # 예: self.gripper_grasp()
        # 예: self.move_to_position(self.place_coords[place_id])
        # 예: self.gripper_release()
        pass

def main(args=None):
    rclpy.init(args=args)
    node = RobotControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()