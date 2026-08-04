import random
import time
from cv_bridge import CvBridge
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class RandomCircleDrawerNode(Node):

  def __init__(self):
    super().__init__('random_circle_drawer_node')

    # DDS(ROS 2) 토픽 퍼블리셔 생성
    self.publisher_ = self.create_publisher(
        Image, 'camera/drawing_image', 10
    )
    self.bridge = CvBridge()

    # 웹캠 열기 (기본 장치 인덱스 0번)
    #self.cap = cv2.VideoCapture(0)
    self.cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 프레임 해상도 획득 (가져오기 실패 시 640x480 기본값 설정)
    self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if self.width == 0 or self.height == 0:
      self.width = 640
      self.height = 480

    # 랜덤 위치 좌표 저장용 리스트
    self.points = []
    self.max_points = 10
    self.last_update_time = time.time()
    self.update_interval = 0.5  # 0.5초 간격으로 새 좌표 생성

    # 약 30Hz(0.033초) 주기로 프레임 갱신 콜백 실행
    self.timer = self.create_timer(0.033, self.timer_callback)

  def timer_callback(self):
    ret, frame = self.cap.read()
    if not ret:
      # 카메라 프레임 수신 실패 시 검은 배경 화면 생성 (확률적 오류 대비)
      frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    current_time = time.time()

    # 설정한 시간 주기(0.5초)마다 새로운 랜덤 좌표 생성
    if current_time - self.last_update_time >= self.update_interval:
      # 화면 가장자리에서 잘리지 않도록 여백(30px)을 두고 좌표 지정
      rand_x = random.randint(30, self.width - 30)
      rand_y = random.randint(30, self.height - 30)
      self.points.append((rand_x, rand_y))
      self.last_update_time = current_time

      # 10곳의 위치 이동(시작점 포함 11개 지점)을 완료하면 초기화 후 반복
      if len(self.points) > self.max_points + 1:
        self.points = [(rand_x, rand_y)]  # 궤적 초기화 및 새 지점을 첫 지점으로 지정

    # 누적된 랜덤 지점들을 선(Line)으로 연결
    for i in range(1, len(self.points)):
      cv2.line(
          frame,
          self.points[i - 1],
          self.points[i],
          (0, 255, 0),  # 초록색 선 (BGR)
          2,
      )

    # 현재 이동한 최신 위치에 원(Circle) 표시
    if len(self.points) > 0:
      cv2.circle(
          frame,
          self.points[-1],
          10,  # 반지름 10px
          (0, 0, 255),  # 빨간색 원 (BGR)
          -1,  # 내부 채우기
      )

    # 1. OpenCV imshow 화면 출력
    cv2.imshow('Random Circle Tracker', frame)
    cv2.waitKey(1)

    # 2. DDS(ROS 2 Topic) Publish
    try:
      msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
      self.publisher_.publish(msg)
    except Exception as e:
      self.get_logger().error(f'이미지 변환 및 Publish 실패: {e}')

  def destroy_node(self):
    if self.cap.isOpened():
      self.cap.release()
    cv2.destroyAllWindows()
    super().destroy_node()


def main(args=None):
  rclpy.init(args=args)
  node = RandomCircleDrawerNode()
  try:
    rclpy.spin(node)
  except KeyboardInterrupt:
    pass
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()