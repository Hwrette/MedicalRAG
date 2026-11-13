import cv2
import numpy as np


def analyze_patches_robustly():
  target_image = "KakaoTalk_20261113_192518326_07.png"

  img_bgr = cv2.imread(target_image)
  if img_bgr is None:
    print(f"Error: Failed to read image '{target_image}'.")
    return

  h, w, _ = img_bgr.shape

  # =========================================================================
  # [1단계] 조명 정규화 (Illumination Normalization via LAB & CLAHE)
  # - 차가운 조명이나 어두운 배경에서도 색상 왜곡이 없도록 명도 대비를 보정
  # =========================================================================
  lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
  l_channel, a_channel, b_channel = cv2.split(lab)
  clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
  cl = clahe.apply(l_channel)
  merged_lab = cv2.merge((cl, a_channel, b_channel))
  img_norm = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

  # =========================================================================
  # [2단계] 메인 패드 영역 검출 및 상대 위치 기반 3대 패치 좌표 설정
  # =========================================================================
  gray = cv2.cvtColor(img_norm, cv2.COLOR_BGR2GRAY)
  _, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)

  contours, _ = cv2.findContours(
      thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )
  if contours:
    # 🐛 [수정 완료] max() 함수에 key=cv2.contourArea 지정
    pad_cnt = max(contours, key=cv2.contourArea)
    px, py, pw, ph = cv2.boundingRect(pad_cnt)
  else:
    px, py, pw, ph = int(w * 0.1), int(h * 0.1), int(w * 0.8), int(h * 0.8)

  # 패드 내부의 상대 좌표를 활용한 3대 패치 고정/적응형 ROI 설정
  temp_box = (
      px + int(pw * 0.05),
      py + int(ph * 0.05),
      int(pw * 0.35),
      int(ph * 0.35),
  )
  phenol_box = (
      px + int(pw * 0.35),
      py + int(ph * 0.05),
      int(pw * 0.55),
      int(ph * 0.45),
  )
  btb_box = (
      px + int(pw * 0.2),
      py + int(ph * 0.45),
      int(pw * 0.6),
      int(ph * 0.45),
  )

  patches_to_process = [
      ("Temperature Patch (TEMP)", temp_box, (0, 255, 0)),  # 초록색 박스
      ("Phenol Red pH Patch", phenol_box, (0, 0, 255)),  # 빨간색 박스
      ("BTB pH Patch", btb_box, (255, 0, 0)),  # 파란색 박스
  ]

  print("=" * 65)
  print(f"Target Image Robust Analysis: '{target_image}'")
  print("=" * 65)

  for patch_name, box, color in patches_to_process:
    x, y, bw, bh = box

    # =====================================================================
    # [3단계] 보정된 이미지에서 평균 RGB 추출 및 수치 환산
    # =====================================================================
    crop_bgr = img_norm[y : y + bh, x : x + bw]
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    mean_rgb = np.mean(crop_rgb, axis=(0, 1))
    r, g, b = mean_rgb

    if "Temperature" in patch_name:
      temp_val = 36.5 if g > r else 37.5
      metric_str = f"Temp: {temp_val}C"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured Temperature: {temp_val:.1f}°C")

    elif "Phenol Red" in patch_name:
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

    # 결과 시각화
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

  output_file = "robust_measured_result.jpg"
  cv2.imwrite(output_file, img_bgr)
  print(f"Result image saved as '{output_file}'.")


if __name__ == "__main__":
  analyze_patches_robustly()