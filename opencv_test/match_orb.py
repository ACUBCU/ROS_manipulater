import cv2
import numpy as np

# 1. 기준 이미지 로드 및 특징점 추출 (사진 촬영본)
# 검출하고자 하는 물체의 이미지를 지정합니다.
src1 = cv2.imread("./data/aruco_1.png")
if src1 is None:
    print("기준 이미지를 찾을 수 없습니다. 경로를 확인하십시오.")
    exit()

img1 = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)

# ORB 생성 및 특징점 계산
orbF = cv2.ORB_create(nfeatures=1000)
kp1, des1 = orbF.detectAndCompute(img1, None)

# BFMatcher 객체 생성 (Hamming 거리, 교차 검사 활성화)
bf = cv2.BFMatcher_create(cv2.NORM_HAMMING, crossCheck=True)

# 2. 카메라 영상 캡처 설정
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

MIN_MATCH_COUNT = 10  # Homography 연산을 위한 최소 매칭점 개수

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 실시간 프레임에서 특징점 추출
    kp2, des2 = orbF.detectAndCompute(img2, None)
    
    # 디스크립터가 존재하는 경우에만 매칭 수행
    if des2 is not None and len(des2) > 0:
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda m: m.distance)
        
        if len(matches) > 0:
            # 거리 기준 필터링
            minDist = matches[0].distance
            # minDist가 0일 경우를 대비해 최소 거리 보정값(예: 30)을 추가로 적용할 수 있으나 예제 기준을 유지함
            good_matches = list(filter(lambda m: m.distance < 5 * minDist, matches))
            
            # 충분한 매칭점이 확보된 경우 물체 영역 표시
            if len(good_matches) >= MIN_MATCH_COUNT:
                # 쿼리 및 트레인 인덱스 추출
                src1_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                src2_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                
                # Homography 계산
                H, mask = cv2.findHomography(src1_pts, src2_pts, cv2.RANSAC, 3.0)
                
                # 변환 행렬이 정상적으로 구해진 경우
                if H is not None:
                    # 기준 이미지의 원본 크기를 바탕으로 모서리 좌표 설정
                    h, w = img1.shape
                    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                    
                    # 카메라 프레임 상의 투시 변환 좌표 계산
                    pts2 = cv2.perspectiveTransform(pts, H)
                    
                    # 카메라 영상에 경계선(다각형) 그리기
                    frame = cv2.polylines(frame, [np.int32(pts2)], True, (0, 255, 0), 3)
                    
                    # 매칭 상태를 시각화하고 싶을 경우 아래 주석 해제
                    # mask_matches = mask.ravel().tolist()
                    # draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=mask_matches, flags=2)
                    # frame = cv2.drawMatches(src1, kp1, frame, kp2, good_matches, None, **draw_params)
            else:
                cv2.putText(frame, "Not enough matches", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Real-time Object Detection", frame)
    
    # ESC 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()