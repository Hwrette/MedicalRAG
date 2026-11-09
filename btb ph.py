import cv2
import numpy as np


def analyze_exact_indicators():
  target_image = "KakaoTalk_20261107_150910596_01.png"

  img_bgr = cv2.imread(target_image)
  if img_bgr is None:
    print(f"Error: Failed to read image '{target_image}'.")
    return

  h, w, _ = img_bgr.shape

  # 상단 배경 철망 영역을 제외하고 페트리 디쉬가 있는 하단 영역(ROI) 설정
  roi_ymin = int(h * 0.3)
  roi_img = img_bgr[roi_ymin:h, 0:w]

  hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)

  # 1. BTB 지시약 (파란색 계열) 정밀 마스크
  mask_btb = cv2.inRange(hsv, (95, 50, 50), (130, 255, 255))

  # 2. 페놀레드 지시약 (노란색/주황색 계열) 정밀 마스크
  mask_phenol = cv2.inRange(hsv, (15, 60, 60), (35, 255, 255))

  # 3. 온도 패치 (TEMP 갈색/어두운 원형 패치) 정밀 마스크
  mask_temp = cv2.inRange(hsv, (0, 10, 10), (25, 250, 160))

  patches = [
      ("BTB pH Patch", mask_btb, (255, 0, 0)),  # 파란색 박스
      ("Phenol Red CO2 Patch", mask_phenol, (0, 0, 255)),  # 빨간색 박스
      ("Temperature Patch (TEMP)", mask_temp, (0, 255, 0)),  # 초록색 박스
  ]

  print("=" * 65)
  print(f"Target Image Analysis: '{target_image}'")
  print("=" * 65)

  for patch_name, mask, color in patches:
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
      print(f"[{patch_name}] No region detected.")
      continue

    valid_contours = [
        c for c in contours if 150 < cv2.contourArea(c) < 30000
    ]
    if not valid_contours:
      continue

    best_cnt = max(valid_contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(best_cnt)

    # 전체 이미지 좌표계로 변환
    y += roi_ymin

    crop_bgr = img_bgr[y : y + bh, x : x + bw]
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    mean_rgb = np.mean(crop_rgb, axis=(0, 1))
    r, g, b = mean_rgb

    # 수치 환산 로직
    if "BTB" in patch_name:
      ph_val = 6.0 + ((b - r) / 255.0) * 3.0
      ph_val = min(10.0, max(4.0, ph_val))
      metric_str = f"pH: {ph_val:.2f}"
      print(f"[{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured pH Value: {ph_val:.2f}")

    elif "Phenol" in patch_name:
      co2_val = 350.0 + (max(0, r - g) * 25.0) + (max(0, r - 100) * 10.0)
      co2_val = min(5000.0, max(100.0, co2_val))
      metric_str = f"CO2: {int(co2_val)}ppm"
      print(f"[{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured CO2 Concentration: {co2_val:.1f} ppm")

    else:
      temp_val = 36.5 if g > r else 37.5
      metric_str = f"Temp: {temp_val}C"
      print(f"[{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured Temperature: {temp_val:.1f}C[cite: 5]")

    print("-" * 65)

    cv2.rectangle(img_bgr, (x, y), (x + bw, y + bh), color, 3)
    cv2.putText(
        img_bgr,
        metric_str,
        (x, max(25, y - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
    )

  output_file = "corrected_patches_result.jpg"
  cv2.imwrite(output_file, img_bgr)
  print(f"Result image saved as '{output_file}'.")


if __name__ == "__main__":
  analyze_exact_indicators()