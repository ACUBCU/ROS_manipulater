import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from std_msgs.msg import Int32MultiArray

class ArucoContrastTest(Node):
    def __init__(self):
        super().__init__('aruco_contrast_test')
        self.bridge = CvBridge()
        
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()

        self.image_sub = self.create_subscription(
            Image,
            '/gripper_camera/image_raw',
            self.image_callback,
            10
        )
        self.marker_pub = self.create_publisher(Int32MultiArray, '/detected_aruco_ids', 10)
        # self.get_logger().info('대비(Contrast) 조절 테스트 노드 시작')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 대비(Contrast)와 밝기(Brightness)를 조절하여 회색과 검은색의 경계를 극대화
        # alpha: 대비 계수 (1.0보다 크면 대비 증가), beta: 밝기 조절
        alpha = 2.0  # 대비 2배 증가
        beta = -50   # 전체적으로 어둡게 만들어 검은색과 회색의 차이를 벌림
        enhanced_gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

        corners, ids, rejected = cv2.aruco.detectMarkers(enhanced_gray, self.dictionary, parameters=self.parameters)

        pub_msg = Int32MultiArray()

        if ids is not None and len(ids) == 2:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            detected_ids = [int(ids[0][0]), int(ids[1][0])]
            
            # 0~5번 범위의 마커와 6~10번 범위의 마커를 각각 분류
            cube_id = None
            target_id = None
            
            for m_id in detected_ids:
                if 0 <= m_id <= 5:
                    cube_id = m_id
                elif 6 <= m_id <= 10:
                    target_id = m_id
            
            self.get_logger().info(f'대상 큐브: ID {cube_id} -> 목표 장소: ID {target_id}')
            
            # 이후 cube_id와 target_id에 대응하는 위치(corners 좌표)를 바탕으로 로봇 제어 수행

        # 변조된 그레이스케일 화면 출력
        cv2.imshow("Enhanced Gray", enhanced_gray)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoContrastTest()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()