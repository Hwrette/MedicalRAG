import cv2
import numpy as np


def measure_chromatic_objects(image_path):
  # 1. 이미지 로드
  img_bgr = cv2.imread(image_path)
  if img_bgr is None:
    print(f"❌ 오류: '{image_path}' 파일을 찾을 수 없습니다.")
    return

  h, w, _ = img_bgr.shape

  # 2. HSV 색공간으로 변환 (색상 분리에 최적)
  hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
  sat = hsv[:, :, 1]  # 채도(Saturation) 채널
  val = hsv[:, :, 2]  # 명도(Value) 채널

  # 3. 무채색(흰색, 검은색, 회색 배경 등) 제외하고 채도가 있는 '진짜 색깔'만 추출
  # 채도가 일정 수준 이상이고, 너무 어둡거나 하얗게 날아간 배경을 제외합니다.
  chromatic_mask = (sat > 35) & (val > 40) & (val < 240)
  mask_uint8 = chromatic_mask.astype(np.uint8) * 255

  # 모폴로지 연산으로 끊긴 영역을 메우고 노이즈 제거
  kernel = np.ones((7, 7), np.uint8)
  cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
  cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

  # 4. 윤곽선(Contour) 검출로 색깔 있는 객체들 분리
  contours, _ = cv2.findContours(
      cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )

  detected_objects = []
  for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 800:  # 너무 작은 점이나 노이즈 무시
      continue
    x, y, bw, bh = cv2.boundingRect(cnt)
    if bw > w * 0.9 or bh > h * 0.9:  # 화면 전체를 덮는 배경 제외
      continue
    detected_objects.append((x, y, bw, bh))

  # 왼쪽에서 오른쪽 순서대로 정렬
  detected_objects = sorted(detected_objects, key=lambda item: item[0])

  print("=" * 60)
  print(f"📁 파일: {image_path} | 검출된 유색 객체 수: {len(detected_objects)}개")
  print("=" * 60)

  # 5. 각 유색 객체별 수치 측정 및 빨간색 박스 표시
  for i, (x, y, bw, bh) in enumerate(detected_objects, start=1):
    crop_bgr = img_bgr[y : y + bh, x : x + bw]
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    crop_lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB)

    median_rgb = np.median(crop_rgb, axis=(0, 1))
    mean_rgb = np.mean(crop_rgb, axis=(0, 1))

    mean_lab = np.mean(crop_lab, axis=(0, 1))
    mean_lab_scaled = [
        mean_lab[0] * (100 / 255.0),
        mean_lab[1] - 128,
        mean_lab[2] - 128,
    ]

    print(f"🔹 [유색 객체 #{i}]")
    print(f" - 영역 좌표 (x, y, w, h): ({x}, {y}, {bw}, {bh})")
    print(
        f" - RGB (중앙값): R={median_rgb[0]:.1f}, G={median_rgb[1]:.1f},"
        f" B={median_rgb[2]:.1f}"
    )
    print(
        f" - RGB (평균값): R={mean_rgb[0]:.1f}, G={mean_rgb[1]:.1f},"
        f" B={mean_rgb[2]:.1f}"
    )
    print(
        f" - LAB (L*, a*, b*): L*={mean_lab_scaled[0]:.1f},"
        f" a*={mean_lab_scaled[1]:.1f}, b*={mean_lab_scaled[2]:.1f}"
    )
    print("-" * 60)

    # 🔴 굵은 빨간색 박스와 번호 표시
    cv2.rectangle(img_bgr, (x, y), (x + bw, y + bh), (0, 0, 255), 3)
    cv2.putText(
        img_bgr,
        f"Color Obj #{i}",
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )

  # 결과 이미지 저장
  output_filename = "chromatic_result.jpg"
  cv2.imwrite(output_filename, img_bgr)
  print(
      f"💾 무채색이 제외되고 유색 객체에만 빨간색 박스가 쳐진 결과가"
      f" '{output_filename}'로 저장되었습니다."
  )


if __name__ == "__main__":
  image_file = "image_a556e2.jpg"
  measure_chromatic_objects(image_file)