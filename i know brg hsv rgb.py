import datetime
import os
import cv2
import numpy as np


def apply_white_balance(img_bgr):
  """화이트 밸런스(Gray World 가정)를 통한 색감 치우침 보정"""
  result = img_bgr.astype(np.float32)
  b_mean = np.mean(result[:, :, 0])
  g_mean = np.mean(result[:, :, 1])
  r_mean = np.mean(result[:, :, 2])

  gray_mean = (b_mean + g_mean + r_mean) / 3.0

  result[:, :, 0] *= gray_mean / (b_mean + 1e-5)
  result[:, :, 1] *= gray_mean / (g_mean + 1e-5)
  result[:, :, 2] *= gray_mean / (r_mean + 1e-5)

  return np.clip(result, 0, 255).astype(np.uint8)


def get_exact_patch_boxes(img_norm):
  """패치 추출 위치 정밀 보정 (실제 패치 크기 및 위치에 맞춘 정확한 고정 좌표)"""
  h, w, _ = img_norm.shape

  # 🎯 [수정 완료] 각 패치가 센서 안쪽에만 정확히 들어가도록 박스 위치 및 크기 재설정
  # 1. 왼쪽 위 온도 패치 (원형 센서 내부가 잘리지 않도록 위치 및 크기 조정)
  temp_box = (int(w * 0.26), int(h * 0.28), int(w * 0.16), int(h * 0.16))

  # 2. 오른쪽 위 CO2 (페놀레드) 패치 (주변 영역 배제하고 노란 패치 중심 포착)
  co2_box = (int(w * 0.44), int(h * 0.23), int(w * 0.22), int(h * 0.20))

  # 3. 아래쪽 BTB 패치 (오른쪽으로 이동시켜 흰 드레싱 제외 및 파란 패치 온전하게 포함)
  btb_box = (int(w * 0.38), int(h * 0.47), int(w * 0.26), int(h * 0.24))

  return temp_box, co2_box, btb_box


def calculate_metrics(patch_name, r, g, b):
  """측정 환산식 (센서별 고유 로직 적용)"""
  total = r + g + b + 1e-5
  r_rat = r / total
  g_rat = g / total
  b_rat = b / total

  if "Temperature" in patch_name:
    # 온도 판정 (필요시 기준값 조정 가능)
    temp_val = 36.5 if g_rat > r_rat else 37.5
    return f"Temp: {temp_val}C", temp_val

  elif "CO2" in patch_name:
    # CO2 (페놀레드) 환산 로직
    diff = r_rat - g_rat
    co2_val = 6.8 + (diff * 10.0)
    co2_val = min(8.4, max(6.8, co2_val))
    return f"CO2: {co2_val:.2f}", co2_val

  elif "BTB" in patch_name:
    # BTB 환산 로직
    diff = b_rat - r_rat
    ph_val = 6.0 + (diff * 12.0)
    ph_val = min(10.0, max(4.0, ph_val))
    return f"pH: {ph_val:.2f}", ph_val

  return "N/A", 0.0


def main():
  target_image = "KakaoTalk_20261113_192518326_06.png"

  img_bgr = cv2.imread(target_image)
  if img_bgr is None:
    print(f"Error: Failed to read image '{target_image}'.")
    return

  # 1단계: 화이트 밸런스 및 조명 정규화
  img_wb = apply_white_balance(img_bgr)
  lab = cv2.cvtColor(img_wb, cv2.COLOR_BGR2LAB)
  l_channel, a_channel, b_channel = cv2.split(lab)
  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
  cl = clahe.apply(l_channel)
  merged_lab = cv2.merge((cl, a_channel, b_channel))
  img_norm = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

  # 2단계: 정밀 보정된 패치 박스 가져오기
  temp_box, co2_box, btb_box = get_exact_patch_boxes(img_norm)

  patches_to_process = [
      ("Temperature Patch (TEMP)", temp_box, (0, 255, 0)),
      ("CO2 Patch (Phenol Red)", co2_box, (0, 0, 255)),
      ("BTB Patch", btb_box, (255, 0, 0)),
  ]

  img_raw_vis = img_bgr.copy()
  img_norm_vis = img_norm.copy()

  print("=" * 75)
  print(f"Precise Patch Analysis for: '{target_image}'")
  print("=" * 75)

  for patch_name, box, color in patches_to_process:
    x, y, bw, bh = box

    # Raw(보정 전) RGB 추출 및 환산
    raw_crop = cv2.cvtColor(img_bgr[y : y + bh, x : x + bw], cv2.COLOR_BGR2RGB)
    raw_r, raw_g, raw_b = np.mean(raw_crop, axis=(0, 1))
    raw_str, _ = calculate_metrics(patch_name, raw_r, raw_g, raw_b)

    # Norm(보정 후) RGB 추출 및 환산
    norm_crop = cv2.cvtColor(
        img_norm[y : y + bh, x : x + bw], cv2.COLOR_BGR2RGB
    )
    norm_r, norm_g, norm_b = np.mean(norm_crop, axis=(0, 1))
    norm_str, _ = calculate_metrics(patch_name, norm_r, norm_g, norm_b)

    print(f"🔹 [{patch_name}]")
    print(
        f"   - [Raw] R={raw_r:.1f}, G={raw_g:.1f}, B={raw_b:.1f} -> {raw_str}"
    )
    print(
        f"   - [Corr] R={norm_r:.1f}, G={norm_g:.1f}, B={norm_b:.1f} ->"
        f" {norm_str}"
    )
    print("-" * 75)

    # 💡 [개선] 원본 이미지와 보정 이미지에 각각 독립된 측정값(Raw / Corr) 표기
    cv2.rectangle(img_raw_vis, (x, y), (x + bw, y + bh), color, 2)
    cv2.putText(
        img_raw_vis,
        f"Raw {raw_str}",
        (x, max(20, y - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        2,
    )

    cv2.rectangle(img_norm_vis, (x, y), (x + bw, y + bh), color, 2)
    cv2.putText(
        img_norm_vis,
        f"Corr {norm_str}",
        (x, max(20, y - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        2,
    )

  # 3단계: 덮어쓰기 방지를 위한 타임스탬프 기반 고유 파일명 저장
  os.makedirs("outputs", exist_ok=True)
  timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
  raw_output_path = f"outputs/result_raw_{timestamp}.jpg"
  norm_output_path = f"outputs/result_corrected_{timestamp}.jpg"

  cv2.imwrite(raw_output_path, img_raw_vis)
  cv2.imwrite(norm_output_path, img_norm_vis)

  print(f"📁 Raw result saved to '{raw_output_path}'")
  print(f"📁 Corrected result saved to '{norm_output_path}'")


if __name__ == "__main__":
  main()