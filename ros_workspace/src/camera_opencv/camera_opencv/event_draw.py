import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


def onMouse(event, x, y, flags, param):
  img, option = param
  if event == cv2.EVENT_LBUTTONDOWN:
    cv2.circle(img, (x, y), 1, (0, 0, 255), 5)
    print("마우스 버튼 클릭")
    onMouse.old_x = x
    onMouse.old_y = y
  elif flags == cv2.EVENT_FLAG_LBUTTON and event == cv2.EVENT_MOUSEMOVE:
    print("드래그")

    color_list = [
        (0, 0, 255),  # 빨강
        (0, 255, 0),  # 초록
        (255, 0, 0),  # 파랑
        (0, 255, 255),  # 노랑
        (255, 0, 255),  # 마젠타
        (255, 255, 0),  # 시안
        (255, 255, 255),  # 흰색
        (128, 128, 128),  # 회색
        (0, 0, 128),  # 진한 빨강
        (0, 128, 0),  # 진한 초록
        (128, 0, 0),  # 진한 파랑
        (128, 128, 0),  # 올리브
        (128, 0, 128),  # 보라
    ]

    selected_color = color_list[option[0]]

    cv2.line(
        img,
        (onMouse.old_x, onMouse.old_y),
        (x, y),
        selected_color,
        2,
    )
    onMouse.old_x = x
    onMouse.old_y = y
  elif event == cv2.EVENT_MOUSEMOVE:
    pass


class RosDrawingNode(Node):

  def __init__(self):
    super().__init__("ros_drawing_node")

    # ROS 2 퍼블리셔 생성
    self.publisher_ = self.create_publisher(Image, "camera/image_raw", 10)
    self.bridge = CvBridge()

    # 웹캠 초기화 (V4L2 및 MJPG 포맷 강제)
    self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not self.cap.isOpened():
      self.get_logger().error("카메라를 열 수 없습니다.")
      return

    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.namedWindow("canvas")

    self.drawing_canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
    self.option = [0]

    cv2.setMouseCallback(
        "canvas", onMouse, (self.drawing_canvas, self.option)
    )

    # 30fps 주기로 프레임 처리 및 퍼블리시
    self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
    self.get_logger().info("ROS 2 드로잉 노드가 시작되었습니다.")

  def timer_callback(self):
    ret, frame = self.cap.read()
    if not ret:
      self.get_logger().warn("프레임을 읽어올 수 없습니다.")
      return

    # 웹캠 화면과 사용자가 그린 캔버스 합성
    display_frame = frame.copy()
    mask = np.any(self.drawing_canvas > 0, axis=-1)
    display_frame[mask] = self.drawing_canvas[mask]

    # ROS 2 이미지 메시지로 변환 후 퍼블리시
    try:
      img_msg = self.bridge.cv2_to_imgmsg(display_frame, encoding="bgr8")
      self.publisher_.publish(img_msg)
    except Exception as e:
      self.get_logger().error(f"메시지 변환 실패: {e}")

    # 화면에 출력
    cv2.imshow("canvas", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
      rclpy.shutdown()
    elif key == ord(" "):
      self.option[0] += 1
      if self.option[0] > 12:
        self.option[0] = 0

  def destroy_node(self):
    if hasattr(self, "cap") and self.cap.isOpened():
      self.cap.release()
    cv2.destroyAllWindows()
    super().destroy_node()


def main(args=None):
  rclpy.init(args=args)
  node = RosDrawingNode()

  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  finally:
    node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()


if __name__ == "__main__":
  main()