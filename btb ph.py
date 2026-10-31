import os
import cv2
import numpy as np


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


def evaluate_ph_and_co2_ppm(mean_rgb, mean_lab):
  """색상 값(LAB, RGB)을 바탕으로 pH 농도와 CO₂ 농도(ppm)를 계산하고,

  요청하신 기준(0~400: 낮음, 400~1000: 중간, 1000~5000: 높음)에 따라 상태를 분류합니다.
  """
  l, a, b = mean_lab
  r, g, blue = mean_rgb

  # 1. pH 추정 로직
  if g > r and blue > r:
    ph_level = "7.4 (알칼리성/안정)"
    indicator_type = "초록색 계열 지시약"
  elif r > g and blue < g:
    ph_level = "5.2 (산성/반응)"
    indicator_type = "주황색 계열 지시약"
  else:
    ph_level = "6.5 (중성/과도기)"
    indicator_type = "혼합/과도기 지시약"

  # 2. CO2 농도 수치 환산 (실험 환경에 따라 계수 조절 가능)
  base_co2_ppm = 350
  if a > 0:
    co2_ppm = base_co2_ppm + (a * 200) + (max(0, b - 20) * 120)
  else:
    co2_ppm = max(200, base_co2_ppm + (a * 50))

  # 3. 요청하신 CO2 농도 구간별 판독 기준 적용
  if co2_ppm <= 400:
    co2_status = "낮음"
  elif 400 < co2_ppm <= 1000:
    co2_status = "중간"
  else:
    co2_status = "높음 (1000~5000 범위 초과 또는 해당 구간)"

  co2_percent = co2_ppm / 10000.0

  return indicator_type, ph_level, co2_ppm, co2_percent, co2_status


def measure_indicators_with_co2_levels():
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
  print(f"📁 파일: {image_path} | 주요 지시약 객체 수: {len(boxes)}개")
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

    # pH 및 CO2 수치 및 구간 판독
    ind_type, ph_est, co2_ppm, co2_percent, co2_status = (
        evaluate_ph_and_co2_ppm(mean_rgb, mean_lab_scaled)
    )

    print(f"🔹 [지시약 객체 #{i} - {ind_type}]")
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
    print(f" 🧪 [정밀 분석 결과]")
    print(f"   • 추정 pH 농도   : {ph_est}")
    print(
        f"   • 추정 CO₂ 농도  : {co2_ppm:.1f} ppm ({co2_percent:.2f}%) ->"
        f" [{co2_status}]"
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

  output_filename = "ph_co2_level_result.jpg"
  cv2.imwrite(output_filename, img_bgr)
  print(
      f"💾 CO₂ 구간 판독 결과가 포함된 이미지가 '{output_filename}'로"
      f" 저장되었습니다."
  )


if __name__ == "__main__":
  measure_indicators_with_co2_levels()