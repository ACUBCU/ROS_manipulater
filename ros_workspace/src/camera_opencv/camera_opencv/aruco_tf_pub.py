import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from scipy.spatial.transform import Rotation as R

class ArucoTfPublisher(Node):
    def __init__(self):
        super().__init__('aruco_tf_publisher')

        self.bridge = CvBridge()
        self.camera_matrix = None
        self.dist_coeffs = None
        
        # 아루코 마커 크기 설정 (4cm)
        self.marker_length = 0.04
        self.dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters = cv2.aruco.DetectorParameters_create()

        # TF 브로드캐스터 설정
        self.tf_broadcaster = TransformBroadcaster(self)

        # 토픽 구독 설정
        self.info_sub = self.create_subscription(
            CameraInfo,
            '/gripper_camera/camera_info',
            self.camera_info_callback,
            10
        )
        self.image_sub = self.create_subscription(
            Image,
            '/gripper_camera/image_raw',
            self.image_callback,
            10
        )

    def camera_info_callback(self, msg):
        if self.camera_matrix is None:
            self.camera_matrix = np.array(msg.k).reshape((3, 3))
            self.dist_coeffs = np.array(msg.d)

    def image_callback(self, msg):
        if self.camera_matrix is None:
            return

        # ROS 이미지 메시지를 OpenCV 형식으로 변환
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 마커 검출
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, self.dictionary, parameters=self.parameters)

        if ids is not None:
            # 화면에 마커의 테두리(Bounding Box) 그리기
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # 자세 추정 계산
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_length, self.camera_matrix, self.dist_coeffs
            )

            # 검출된 모든 마커에 대해 축을 그리고 TF를 발행
            for i in range(len(ids)):
                rvec = rvecs[i][0]
                tvec = tvecs[i][0]

                # 화면에 X(빨강), Y(초록), Z(파랑) 3D 축 그리기 (축 길이: 0.02m)
                cv2.drawFrameAxes(frame, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.02)

                # 회전 벡터(Rodrigues)를 쿼터니언(Quaternion)으로 변환
                rotation = R.from_rotvec(rvec)
                quat = rotation.as_quat()

                # TF 메시지 생성 및 발행
                t = TransformStamped()
                t.header.stamp = self.get_clock().now().to_msg()
                t.header.frame_id = msg.header.frame_id  # 부모 좌표계: 카메라
                t.child_frame_id = f'aruco_marker_{ids[i][0]}' # 자식 좌표계: 아루코 마커

                t.transform.translation.x = tvec[0]
                t.transform.translation.y = tvec[1]
                t.transform.translation.z = tvec[2]
                
                t.transform.rotation.x = quat[0]
                t.transform.rotation.y = quat[1]
                t.transform.rotation.z = quat[2]
                t.transform.rotation.w = quat[3]

                self.tf_broadcaster.sendTransform(t)

                # 로그 정보 터미널 출력
                self.get_logger().info(
                    f"Marker ID: {ids[i][0]} | "
                    f"Position(x,y,z): {tvec[0]:.3f}, {tvec[1]:.3f}, {tvec[2]:.3f} | "
                    f"Orientation(x,y,z,w): {quat[0]:.3f}, {quat[1]:.3f}, {quat[2]:.3f}, {quat[3]:.3f}"
                )

        # OpenCV 창에 결과 이미지 출력
        cv2.imshow("ArUco Detection", frame)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ArucoTfPublisher()
    
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