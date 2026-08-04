import cv2
import numpy as np


def onMouse(event, x, y, flags, param):
    img, option = param
    if event == cv2.EVENT_LBUTTONDOWN:
        # 직접 지정한 튜플 사용 (예: 빨간색 BGR 기준 (0, 0, 255))
        cv2.circle(img, (x, y), 1, (0, 0, 255), 5)
        print("마우스 버튼 클릭")
        onMouse.old_x = x
        onMouse.old_y = y
    elif flags == cv2.EVENT_FLAG_LBUTTON and event == cv2.EVENT_MOUSEMOVE:
        print("드래그")
        
        # option[0] 값에 따라 직접 정의한 튜플 리스트에서 색상 선택 (OpenCV용 BGR 튜플 직접 사용)
        color_list = [
            (0, 0, 255),    # 빨강
            (0, 255, 0),    # 초록
            (255, 0, 0),    # 파랑
            (0, 255, 255),  # 노랑
            (255, 0, 255),  # 마젠타
            (255, 255, 0),  # 시안
            (255, 255, 255),# 흰색
            (128, 128, 128),# 회색
            (0, 0, 128),    # 진한 빨강
            (0, 128, 0),    # 진한 초록
            (128, 0, 0),    # 진한 파랑
            (128, 128, 0),  # 올리브
            (128, 0, 128)   # 보라
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


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("오류: 카메라를 열 수 없습니다.")
        return

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cv2.namedWindow("canvas")

    drawing_canvas = np.zeros((height, width, 3), dtype=np.uint8)
    option = [0]

    cv2.setMouseCallback("canvas", onMouse, (drawing_canvas, option))

    print("웹캠 실행 중... 스페이스바: 색상 변경, 'q': 종료")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("오류: 프레임을 읽어올 수 없습니다.")
            break

        display_frame = frame.copy()
        mask = np.any(drawing_canvas > 0, axis=-1)
        display_frame[mask] = drawing_canvas[mask]

        cv2.imshow("canvas", display_frame)

        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            option[0] += 1
        if option[0] > 12:
            option[0] = 0

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()