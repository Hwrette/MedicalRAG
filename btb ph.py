import os
import cv2
import numpy as np

# 🎨 1. 더욱 세분화된 표준 지시약 색상 데이터베이스 (정밀 기준값 정의)
REFERENCE_COLORS = [
    {
        "name": "강산성 지시약 (반응 강함)",
        "rgb": (240, 150, 80),
        "ph": 4.0,
        "co2_ppm": 3500,
        "co2_status": "높음",
    },
    {
        "name": "산성 지시약 (반응 보통)",
        "rgb": (225, 175, 110),
        "ph": 5.2,
        "co2_ppm": 1200,
        "co2_status": "높음",
    },
    {
        "name": "약산성 지시약 (과도기)",
        "rgb": (205, 185, 120),
        "ph": 6.0,
        "co2_ppm": 850,
        "co2_status": "중간",
    },
    {
        "name": "중성 지시약 (안정)",
        "rgb": (190, 180, 130),
        "ph": 6.5,
        "co2_ppm": 600,
        "co2_status": "중간",
    },
    {
        "name": "약알칼리성 지시약 (안정)",
        "rgb": (175, 178, 142),
        "ph": 7.0,
        "co2_ppm": 450,
        "co2_status": "중간",
    },
    {
        "name": "알칼리성 지시약 (정상 범위)",
        "rgb": (160, 175, 150),
        "ph": 7.4,
        "co2_ppm": 300,
        "co2_status": "낮음",
    },
    {
        "name": "강알칼리성 지시약 (높은 안정성)",
        "rgb": (140, 170, 160),
        "ph": 8.5,
        "co2_ppm": 150,
        "co2_status": "낮음",
    },
]


def find_image_automatically():
  valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")
  image_files = [
      f for f in os.listdir(".") if f.lower().endswith(valid_extensions)
  ]
  if not image_files:
    print(
        "❌ 오류: 현재 폴더에 이미지 파일이 없습니다. 이미지 파일을 스크립트와"
        " 같은 폴더에 넣어주세요."
    )
    return None
  selected_image = image_files[0]
  print(f"🔍 자동으로 감지된 이미지 파일: '{selected_image}'")
  return selected_image


def match_closest_reference_color(measured_rgb):
  """추출된 RGB 값과 가장 가까운(유클리드 거리가 최소인) 세분화된 표준 색상을 매칭합니다."""
  min_dist = float("inf")
  best_match = None

  for ref in REFERENCE_COLORS:
    ref_rgb = np.array(ref["rgb"])
    dist = np.linalg.norm(ref_rgb - np.array(measured_rgb))
    if dist < min_dist:
      min_dist = dist
      best_match = ref

  return best_match


def measure_and_match_indicators_detailed():
  image_path = find_image_automatically()
  if not image_path:
    return

  img_bgr = cv2.imread(image_path)
  if img_bgr is None:
    print(f"❌ 오류: '{image_path}' 파일을 열 수 없습니다.")
    return

  h, w, _ = img_bgr.shape

  # HSV 변환 및 무채색 배경 제거
  hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
  sat = hsv[:, :, 1]
  val = hsv[:, :, 2]

  chromatic_mask = (sat > 25) & (val > 40) & (val < 250)
  mask_uint8 = chromatic_mask.astype(np.uint8) * 255

  # 영역 병합을 위한 모폴로지 연산
  kernel = np.ones((35, 35), np.uint8)
  cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel)
  cleaned = cv2.morphologyEx(
      cleaned, cv2.MORPH_OPEN, np.ones((11, 11), np.uint8)
  )

  contours, _ = cv2.findContours(
      cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )

  boxes = []
  for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 5000:
      continue
    x, y, bw, bh = cv2.boundingRect(cnt)
    if bw > w * 0.95 or bh > h * 0.95:
      continue
    boxes.append((area, x, y, bw, bh))

  # 상위 2개의 큰 객체 선택 후 좌측부터 정렬
  boxes = sorted(boxes, key=lambda x: x[0], reverse=True)[:2]
  boxes = sorted(boxes, key=lambda item: item[1])

  print("=" * 65)
  print(
      f"📁 파일: {image_path} | 감지된 주요 지시약 객체 수: {len(boxes)}개"
  )
  print("=" * 65)

  for i, (area, x, y, bw, bh) in enumerate(boxes, start=1):
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

    # 🎯 세분화된 표준 색상 데이터베이스와 비교
    matched_ref = match_closest_reference_color(mean_rgb)

    print(f"🔹 [지시약 객체 #{i}]")
    print(
        f" - 영역 좌표 (x, y, w, h): ({x}, {y}, {bw}, {bh}) | 면적: {area:.0f}"
    )
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
    print(f" 🎯 [세분화된 표준 색상 매칭 결과]")
    print(f"   • 가장 가까운 표준 단계 : {matched_ref['name']}")
    print(f"   • 정밀 매칭 pH        : {matched_ref['ph']}")
    print(
        f"   • 정밀 매칭 CO₂ 농도  : {matched_ref['co2_ppm']} ppm"
        f" ({matched_ref['co2_ppm']/10000.0:.2f}%) ->"
        f" [{matched_ref['co2_status']}]"
    )
    print("-" * 65)

    # 🔴 빨간색 박스와 번호 표시
    cv2.rectangle(img_bgr, (x, y), (x + bw, y + bh), (0, 0, 255), 4)
    cv2.putText(
        img_bgr,
        f"Indicator #{i}",
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
    )

  output_filename = "detailed_color_matched_result.jpg"
  cv2.imwrite(output_filename, img_bgr)
  print(
      f"💾 세분화된 매칭 결과가 포함된 이미지가 '{output_filename}'로"
      f" 저장되었습니다."
  )


if __name__ == "__main__":
  measure_and_match_indicators_detailed()