import cv2
import numpy as np


def analyze_all_patches_ph_only():
  target_image = "KakaoTalk_20261113_175315242.jpg"

  img_bgr = cv2.imread(target_image)
  if img_bgr is None:
    print(f"Error: Failed to read image '{target_image}'.")
    return

  h, w, _ = img_bgr.shape

  # 1. 온도 패치 (상단 좌측)
  mask_temp = cv2.inRange(
      cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV), (0, 10, 10), (25, 250, 160)
  )

  # 2. BTB pH 패치 (하단 중앙)
  mask_btb = cv2.inRange(
      cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV), (65, 30, 30), (135, 255, 255)
  )

  def get_box_from_mask(mask, x_range, y_range):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    valid = []
    for c in contours:
      area = cv2.contourArea(c)
      if area < 150:
        continue
      x, y, bw, bh = cv2.boundingRect(c)
      if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
        valid.append((area, x, y, bw, bh))
    if not valid:
      return None
    return max(valid, key=lambda item: item[0])[1:5]

  temp_box = get_box_from_mask(mask_temp, (0, int(w * 0.5)), (0, int(h * 0.5)))
  btb_box = get_box_from_mask(
      mask_btb, (int(w * 0.2), int(w * 0.9)), (int(h * 0.4), h)
  )

  # 3. 페놀레드 패치 (상단 우측 주황색 영역 고정 ROI)
  phenol_box = (int(w * 0.35), int(h * 0.08), int(w * 0.55), int(h * 0.45))

  patches_to_process = [
      ("Temperature Patch (TEMP)", temp_box, (0, 255, 0)),  # 초록색 박스
      ("Phenol Red pH Patch", phenol_box, (0, 0, 255)),  # 빨간색 박스
      ("BTB pH Patch", btb_box, (255, 0, 0)),  # 파란색 박스
  ]

  print("=" * 65)
  print(f"Target Image Analysis: '{target_image}'")
  print("=" * 65)

  for patch_name, box, color in patches_to_process:
    if box is None:
      print(f"[{patch_name}] No region detected.")
      continue

    x, y, bw, bh = box
    crop_bgr = img_bgr[y : y + bh, x : x + bw]
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    mean_rgb = np.mean(crop_rgb, axis=(0, 1))
    r, g, b = mean_rgb

    # 측정값 환산 (모두 온도 및 pH로 출력)
    if "Temperature" in patch_name:
      temp_val = 36.5 if g > r else 37.5
      metric_str = f"Temp: {temp_val}C"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured Temperature: {temp_val:.1f}°C")

    elif "Phenol Red" in patch_name:
      # 페놀레드 변색 범위(산성~약알칼리성, 보통 pH 6.8 ~ 8.4) 기준으로 RGB 비율 환산
      ph_val = 6.8 + ((r - g) / 255.0) * 1.6
      ph_val = min(8.4, max(6.8, ph_val))
      metric_str = f"pH: {ph_val:.2f}"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured pH Value (Phenol Red): pH {ph_val:.2f}")

    elif "BTB" in patch_name:
      ph_val = 6.0 + ((b - r) / 255.0) * 3.0
      ph_val = min(10.0, max(4.0, ph_val))
      metric_str = f"pH: {ph_val:.2f}"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured pH Value (BTB): pH {ph_val:.2f}")

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

  output_file = "all_patches_ph_result.jpg"
  cv2.imwrite(output_file, img_bgr)
  print(f"Result image saved as '{output_file}'.")


if __name__ == "__main__":
  analyze_all_patches_ph_only()