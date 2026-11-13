import os
import cv2
import numpy as np


def apply_white_balance(img_bgr):
  """1. 화이트 밸런스(Gray World 가정)를 통한 색감 치우침 보정

  - 노란빛이나 푸른빛 조명으로 인해 왜곡된 색감을 채널별 평균 게인을 조절하여 교정
  """
  result = img_bgr.astype(np.float32)
  # 각 채널별 평균 계산
  b_mean = np.mean(result[:, :, 0])
  g_mean = np.mean(result[:, :, 1])
  r_mean = np.mean(result[:, :, 2])

  # 전체 평균 (목표 무채색 밝기)
  gray_mean = (b_mean + g_mean + r_mean) / 3.0

  # 채널별 게인 적용으로 색 편차 보정
  result[:, :, 0] *= gray_mean / (b_mean + 1e-5)  # Blue
  result[:, :, 1] *= gray_mean / (g_mean + 1e-5)  # Green
  result[:, :, 2] *= gray_mean / (r_mean + 1e-5)  # Red

  return np.clip(result, 0, 255).astype(np.uint8)


def get_robust_patch_boxes(img_norm, use_fixed=True):
  """2. 패치 위치 검출 안정화

  - 구도가 동일한 조건에서는 오인식을 방지하기 위해 '고정 좌표(Fixed ROI)'를 우선 사용하고,
    추후 검증을 위해 자동 외곽선 검출 결과를 함께 비교할 수 있도록 설계
  """
  h, w, _ = img_norm.shape

  if use_fixed:
    # 💡 [고정 좌표 모드] 동일 구도 사진 간의 좌표 흔들림을 원천 방지
    # (이미지 크기 비율에 따른 고정 픽셀 박스 지정 - 필요시 미세 조정 가능)
    px, py, pw, ph = int(w * 0.2), int(h * 0.2), int(w * 0.6), int(w * 0.6)
  else:
    # [자동 검출 모드] 기존 외곽선 기반 검출
    gray = cv2.cvtColor(img_norm, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if contours:
      pad_cnt = max(contours, key=cv2.contourArea)
      px, py, pw, ph = cv2.boundingRect(pad_cnt)
    else:
      px, py, pw, ph = int(w * 0.1), int(h * 0.1), int(w * 0.8), int(h * 0.8)

  # 3대 패치 상대 좌표 설정 (패치 간섭 및 배경 포함 여부 검증용 마진 포함)
  temp_box = (
      px + int(pw * 0.05),
      py + int(ph * 0.05),
      int(pw * 0.30),
      int(pw * 0.30),
  )
  phenol_box = (
      px + int(pw * 0.40),
      py + int(ph * 0.05),
      int(pw * 0.30),
      int(pw * 0.30),
  )
  btb_box = (
      px + int(pw * 0.20),
      py + int(ph * 0.40),
      int(pw * 0.40),
      int(pw * 0.40),
  )

  return temp_box, phenol_box, btb_box


def calculate_metrics(patch_name, r, g, b):
  """3. 환산식 구조 (추후 실제 샘플 캘리브레이션 표로 고도화 필요)"""
  total = r + g + b + 1e-5
  r_rat = r / total
  g_rat = g / total
  b_rat = b / total

  if "Temperature" in patch_name:
    # 예시 환산 로직 (실제 캘리브레이션 데이터로 대체 필요)
    temp_val = 36.5 if g_rat > r_rat else 37.5
    return f"Temp: {temp_val}C", temp_val

  elif "Phenol Red" in patch_name:
    # 비율 차이 기반 pH 산출
    diff = r_rat - g_rat
    ph_val = 6.8 + (diff * 10.0)
    ph_val = min(8.4, max(6.8, ph_val))
    return f"pH: {ph_val:.2f}", ph_val

  elif "BTB" in patch_name:
    # 비율 차이 기반 pH 산출
    diff = b_rat - r_rat
    ph_val = 6.0 + (diff * 12.0)
    ph_val = min(10.0, max(4.0, ph_val))
    return f"pH: {ph_val:.2f}", ph_val

  return "N/A", 0.0


def main():
  target_image = "KakaoTalk_20261113_192518326_05.png"

  img_bgr = cv2.imread(target_image)
  if img_bgr is None:
    print(f"Error: Failed to read image '{target_image}'.")
    return

  # =========================================================================
  # [1단계] 화이트 밸런스 및 조명 정규화 (색감 + 밝기 동시 보정)
  # =========================================================================
  img_wb = apply_white_balance(img_bgr)

  lab = cv2.cvtColor(img_wb, cv2.COLOR_BGR2LAB)
  l_channel, a_channel, b_channel = cv2.split(lab)
  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
  cl = clahe.apply(l_channel)
  merged_lab = cv2.merge((cl, a_channel, b_channel))
  img_norm = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

  # =========================================================================
  # [2단계] 패치 위치 검출 (고정 좌표 모드 활성화로 흔들림 방지)
  # =========================================================================
  temp_box, phenol_box, btb_box = get_robust_patch_boxes(
      img_norm, use_fixed=True
  )

  patches_to_process = [
      ("Temperature Patch (TEMP)", temp_box, (0, 255, 0)),
      ("Phenol Red pH Patch", phenol_box, (0, 0, 255)),
      ("BTB pH Patch", btb_box, (255, 0, 0)),
  ]

  # 시각화용 복사본 (원본용, 보정용 분리)
  img_raw_vis = img_bgr.copy()
  img_norm_vis = img_norm.copy()

  print("=" * 75)
  print(f"Advanced Multi-Stage Analysis for: '{target_image}'")
  print("=" * 75)

  for patch_name, box, color in patches_to_process:
    x, y, bw, bh = box

    # Raw(보정 전) RGB 추출
    raw_crop = cv2.cvtColor(img_bgr[y : y + bh, x : x + bw], cv2.COLOR_BGR2RGB)
    raw_r, raw_g, raw_b = np.mean(raw_crop, axis=(0, 1))

    # Norm(보정 후) RGB 추출
    norm_crop = cv2.cvtColor(
        img_norm[y : y + bh, x : x + bw], cv2.COLOR_BGR2RGB
    )
    norm_r, norm_g, norm_b = np.mean(norm_crop, axis=(0, 1))

    # 3단계 환산식 적용
    metric_str, numeric_val = calculate_metrics(patch_name, norm_r, norm_g, norm_b)

    # 결과 출력 (편차 및 값 비교)
    print(f"🔹 [{patch_name}]")
    print(f"   - [Raw RGB] R={raw_r:.1f}, G={raw_g:.1f}, B={raw_b:.1f}")
    print(
        f"   - [Norm RGB] R={norm_r:.1f}, G={norm_g:.1f}, B={norm_b:.1f} ->"
        f" {metric_str}"
    )
    print("-" * 75)

    # 원본 시각화 이미지에 박스 렌더링
    cv2.rectangle(img_raw_vis, (x, y), (x + bw, y + bh), color, 2)
    cv2.putText(
        img_raw_vis,
        f"Raw {metric_str}",
        (x, max(20, y - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        2,
    )

    # 보정 시각화 이미지에 박스 렌더링
    cv2.rectangle(img_norm_vis, (x, y), (x + bw, y + bh), color, 2)
    cv2.putText(
        img_norm_vis,
        f"Corr {metric_str}",
        (x, max(20, y - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        2,
    )

  # =========================================================================
  # [4단계] 원본 영상과 보정 영상을 각각 다른 파일명으로 분리 저장
  # =========================================================================
  os.makedirs("outputs", exist_ok=True)
  raw_output_path = "outputs/result_raw_analyzed.jpg"
  norm_output_path = "outputs/result_corrected_analyzed.jpg"

  cv2.imwrite(raw_output_path, img_raw_vis)
  cv2.imwrite(norm_output_path, img_norm_vis)

  print(f"📁 Raw visualization saved to '{raw_output_path}'")
  print(f"📁 Corrected visualization saved to '{norm_output_path}'")


if __name__ == "__main__":
  main()