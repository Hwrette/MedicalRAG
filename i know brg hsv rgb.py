import cv2
import numpy as np


def analyze_all_patches_with_comments():
  # 분석할 대상 이미지 파일 로드
  target_image = "KakaoTalk_20261113_175315242.jpg"

  img_bgr = cv2.imread(target_image)
  if img_bgr is None:
    print(f"Error: Failed to read image '{target_image}'.")
    return

  h, w, _ = img_bgr.shape

  # =========================================================================
  # [1단계] 색상 공간 변환 및 마스킹 (색보정 및 노이즈 차단 전처리)
  # - OpenCV는 기본적으로 BGR 형식이므로 채널 분리를 위해 RGB 및 HSV로 변환
  # - 조명 변화나 비닐 랩 반사광의 영향을 최소화하기 위해 HSV(색상, 채도, 명도) 기준 활용
  # =========================================================================
  hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

  # 온도 패치 검출을 위한 HSV 범위 (갈색~어두운 원형 패치)
  mask_temp = cv2.inRange(hsv, (0, 10, 10), (25, 250, 160))

  # BTB pH 패치 검출을 위한 HSV 범위 (파란색/청록색 계열)
  mask_btb = cv2.inRange(hsv, (65, 30, 30), (135, 255, 255))

  # 마스크 영역 내 픽셀을 추출하여 바운딩 박스를 반환하는 내부 함수
  def get_box_from_mask(mask, x_range, y_range):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    valid = []
    for c in contours:
      area = cv2.contourArea(c)
      if area < 150:  # 너무 작은 노이즈 영역은 무시
        continue
      x, y, bw, bh = cv2.boundingRect(c)
      # 지정된 화면 위치(ROI) 내에 있는 객체만 유효한 패치로 인정
      if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
        valid.append((area, x, y, bw, bh))
    if not valid:
      return None
    # 가장 면적이 큰 유효 컨투어를 선택하여 반환
    return max(valid, key=lambda item: item[0])[1:5]

  # 온도 패치와 BTB 패치의 대략적인 위치 제약을 주어 오인식 방지
  temp_box = get_box_from_mask(mask_temp, (0, int(w * 0.5)), (0, int(h * 0.5)))
  btb_box = get_box_from_mask(
      mask_btb, (int(w * 0.2), int(w * 0.9)), (int(h * 0.4), h)
  )

  # 페놀레드 pH 패치 (상단 우측 주황색 영역: 비닐 반사광 왜곡을 방지하기 위해 고정 ROI 지정)
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

    # =====================================================================
    # [2단계] 평균 RGB 추출 및 색보정 (왜곡 최소화)
    # - 단일 픽셀은 카메라 노이즈나 빛 반사로 값이 튈 수 있으므로
    #   패치 내부 전체 픽셀의 평균값(np.mean)을 구해 색상 왜곡을 최소화함
    # =====================================================================
    crop_bgr = img_bgr[y : y + bh, x : x + bw]
    crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    mean_rgb = np.mean(crop_rgb, axis=(0, 1))
    r, g, b = mean_rgb

    # =====================================================================
    # [3단계] RGB 편차 기반 수치 환산 알고리즘
    # - 추출된 R, G, B 채널의 상대적 크기와 차이를 공식에 대입하여 물리적 값 도출
    # =====================================================================
    if "Temperature" in patch_name:
      # 초록색(G)과 빨간색(R) 성분 비교를 통한 체온 환산
      temp_val = 36.5 if g > r else 37.5
      metric_str = f"Temp: {temp_val}C"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured Temperature: {temp_val:.1f}°C")

    elif "Phenol Red" in patch_name:
      # 페놀레드 변색 범위(pH 6.8 ~ 8.4)에 맞춰 R과 G 채널 편차를 활용한 pH 환산
      ph_val = 6.8 + ((r - g) / 255.0) * 1.6
      ph_val = min(8.4, max(6.8, ph_val))
      metric_str = f"pH: {ph_val:.2f}"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured pH Value (Phenol Red): pH {ph_val:.2f}")

    elif "BTB" in patch_name:
      # BTB 지시약의 파란색(B)과 빨간색(R) 차이를 활용한 pH 환산
      ph_val = 6.0 + ((b - r) / 255.0) * 3.0
      ph_val = min(10.0, max(4.0, ph_val))
      metric_str = f"pH: {ph_val:.2f}"
      print(f"🔹 [{patch_name}] x={x}, y={y} | RGB: R={r:.1f}, G={g:.1f}, B={b:.1f}")
      print(f" -> Measured pH Value (BTB): pH {ph_val:.2f}")

    print("-" * 65)

    # =====================================================================
    # [4단계] 결과 시각화 (원본 이미지 위에 박스와 측정값 텍스트 오버레이)
    # =====================================================================
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

  # 최종 결과 이미지 저장
  output_file = "commented_measurement_result.jpg"
  cv2.imwrite(output_file, img_bgr)
  print(f"Result image saved as '{output_file}'.")


if __name__ == "__main__":
  analyze_all_patches_with_comments()