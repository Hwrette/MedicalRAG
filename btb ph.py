import cv2
import numpy as np


def extract_indicator_color(image_path, roi_box):
  """이미지 파일에서 특정 영역(ROI)의 RGB 및 LAB 색상 수치를 추출하는 함수

  :param image_path: 이미지 파일 경로 (예: 'sample.jpg')
  :param roi_box: 추출할 영역 좌표 (x, y, w, h)
  """
  # 1. 이미지 로드
  img_bgr = cv2.imread(image_path)
  if img_bgr is None:
    print(f"❌ 오류: '{image_path}' 파일을 찾을 수 없습니다.")
    return

  # 2. 영역(ROI) 자르기
  x, y, w, h = roi_box
  crop_bgr = img_bgr[y : y + h, x : x + w]

  if crop_bgr.size == 0:
    print("❌ 오류: 지정한 영역(ROI)이 이미지 범위를 벗어났습니다.")
    return

  # 3. RGB 및 LAB 값 계산 (OpenCV 기본 BGR을 RGB로 변환)
  crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
  crop_lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB)

  # 중앙값(Median)과 평균(Mean) 추출
  median_rgb = np.median(crop_rgb, axis=(0, 1))
  mean_rgb = np.mean(crop_rgb, axis=(0, 1))

  mean_lab = np.mean(crop_lab, axis=(0, 1))
  # OpenCV LAB 스케일 조정 (L: 0~255 -> 0~100, a/b: 0~255 -> -128~127)
  mean_lab_scaled = [
      mean_lab[0] * (100 / 255.0),
      mean_lab[1] - 128,
      mean_lab[2] - 128,
  ]

  # 4. 결과 출력
  print("=" * 40)
  print(f"📁 파일: {image_path}")
  print(f"📍 영역(x,y,w,h): {roi_box}")
  print("-" * 40)
  print(
      f" - RGB (중앙값): R={median_rgb[0]:.1f}, G={median_rgb[1]:.1f},"
      f" B={median_rgb[2]:.1f}"
  )
  print(
      f" - RGB (평균값): R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f},"
      f" B={mean_rgb[2]:.1f}"
  )
  print(
      f" - LAB (L,a,b):  L*={mean_lab_scaled[0]:.1f},"
      f" a*={mean_lab_scaled[1]:.1f}, b*={mean_lab_scaled[2]:.1f}"
  )
  print("=" * 40)

  # (선택) 확인용 이미지 창 띄우기 (아무 키나 누르면 닫힘)
  # cv2.rectangle(img_bgr, (x, y), (x+w, y+h), (0, 0, 255), 2)
  # cv2.imshow("Image Preview", img_bgr)
  # cv2.waitKey(0)
  # cv2.destroyAllWindows()


if __name__ == "__main__":
  # 사용 예시:
  # 1. 분석할 이미지 파일 이름
  image_file = "sample.jpg"

  # 2. 추출하고 싶은 지시약 영역의 픽셀 좌표 (x, y, 가로크기, 세로크기)
  # 본인의 이미지에 맞는 좌표로 수정하세요.
  my_roi = (150, 120, 50, 50)

  extract_indicator_color(image_file, my_roi)