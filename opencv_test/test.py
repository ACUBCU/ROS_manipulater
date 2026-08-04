import cv2

def main():
    # 0번 웹캠 장치 열기 (V4L2 백엔드 명시)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("오류: 카메라를 열 수 없습니다.")
        return

    # --- 핵심 수정 부분: 화면 깨짐 방지를 위한 설정 강제 ---
    # 1. 코덱을 MJPEG로 강제 설정 (대부분의 깨짐 현상 해결)
    # 운영체제에 따라 'MJPG' 대신 cv2.VideoWriter_fourcc(*'MJPG') 사용
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    
    # 2. 해상도 설정 (카메라가 지원하는 해상도로 명시)
    # 너무 높은 해상도는 대역폭 문제로 깨짐을 유발할 수 있습니다.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 3. (선택사항) 프레임 레이트 설정
    cap.set(cv2.CAP_PROP_FPS, 30)
    # ----------------------------------------------------

    print("웹캠 실행 중... 종료하려면 'q'를 누르세요.")

    while True:
        ret, frame = cap.read()

        if not ret:
            # MJPG 설정 후 프레임을 못 읽어온다면 카메라가 해당 포맷 미지원
            print("오류: 프레임을 읽어올 수 없습니다. 코덱 설정을 확인하세요.")
            break

        cv2.imshow("Webcam View (Fixed)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()