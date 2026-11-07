"""지정한 패치 영역의 RGB를 추출하고 패치별 보정표로 수치를 추정한다."""
import math
from pathlib import Path

CHANNELS = {
    'temperature': 'temperature_value',
    'phenol_red': 'phenol_red_ph_value',
    'btb': 'ph_value',
}


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_layout(layout):
    if set(layout.get('patches', {})) != set(CHANNELS):
        raise ValueError('patches에는 temperature, phenol_red, btb가 각각 필요합니다.')
    for name, patch in layout['patches'].items():
        roi = patch.get('roi')
        if (not isinstance(roi, list) or len(roi) != 4 or not all(number(x) for x in roi)
                or not (0 <= roi[0] < roi[2] <= 1 and 0 <= roi[1] < roi[3] <= 1)):
            raise ValueError(f'{name}: roi는 0~1의 [왼쪽, 위, 오른쪽, 아래] 좌표여야 합니다.')
        samples = patch.get('calibration', [])
        if not isinstance(samples, list):
            raise ValueError(f'{name}: calibration은 목록이어야 합니다.')
        limit = patch.get('max_rgb_distance')
        if samples and (not number(limit) or limit < 0):
            raise ValueError(f'{name}: 보정 실험으로 정한 max_rgb_distance가 필요합니다.')
        if samples and len(samples) < 2:
            raise ValueError(f'{name}: 보정 기준점은 최소 두 개가 필요합니다.')
        seen = set()
        for sample in samples:
            rgb, value = sample.get('rgb'), sample.get('value')
            if (not isinstance(rgb, list) or len(rgb) != 3
                    or not all(number(x) and 0 <= x <= 255 for x in rgb) or not number(value)):
                raise ValueError(f'{name}: 보정점에는 rgb 숫자 3개와 유한한 value가 필요합니다.')
            if name != 'temperature' and not 0 <= value <= 14:
                raise ValueError(f'{name}: pH 보정값은 0~14여야 합니다.')
            if tuple(rgb) in seen:
                raise ValueError(f'{name}: 중복 RGB 보정점입니다.')
            seen.add(tuple(rgb))


def match_rgb(rgb, patch):
    """기존 코드처럼 RGB 유클리드 거리가 가장 가까운 기준값을 선택한다."""
    samples = patch.get('calibration', [])
    if not samples:
        return {'value': None, 'status': 'calibration_missing'}
    distances = [math.dist(rgb, s['rgb']) for s in samples]
    minimum = min(distances)
    nearest = [s for s, d in zip(samples, distances) if math.isclose(d, minimum, abs_tol=1e-9)]
    if minimum > patch['max_rgb_distance']:
        return {'value': None, 'status': 'outside_calibration', 'rgb_distance': minimum}
    if len({s['value'] for s in nearest}) > 1:
        return {'value': None, 'status': 'ambiguous_match', 'rgb_distance': minimum}
    return {'value': nearest[0]['value'], 'status': 'matched',
            'rgb_distance': minimum, 'reference': dict(nearest[0])}


def measure_image(image_path, layout, annotated_path=None):
    # 이미지 입력을 쓰지 않는 실행에는 OpenCV/NumPy가 필요하지 않다.
    import cv2
    import numpy as np

    validate_layout(layout)
    image_path = Path(image_path)
    if annotated_path is not None and Path(annotated_path).resolve() == image_path.resolve():
        raise ValueError('표시 이미지 출력 경로는 원본과 달라야 합니다.')
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f'이미지를 읽을 수 없습니다: {image_path}')
    height, width = img.shape[:2]
    annotated = img.copy()
    measurements = {}
    raw = {}
    for name, key in CHANNELS.items():
        patch = layout['patches'][name]
        left, top, right, bottom = patch['roi']
        x1, y1 = int(left * width), int(top * height)
        x2, y2 = int(right * width), int(bottom * height)
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f'{name}: 이미지에서 측정 영역이 너무 작습니다.')
        rgb = cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
        # 글자·반사광의 영향을 줄이기 위해 채널별 중앙값을 사용한다.
        median = np.median(rgb, axis=(0, 1)).tolist()
        match = match_rgb(median, patch)
        measurements[name] = {**match, 'input_field': key,
                              'roi_pixels': [x1, y1, x2, y2], 'rgb_median': median,
                              'rgb_mean': np.mean(rgb, axis=(0, 1)).tolist()}
        raw[key] = match['value']
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(annotated, name, (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    if annotated_path is not None and not cv2.imwrite(str(annotated_path), annotated):
        raise ValueError(f'표시 이미지를 저장할 수 없습니다: {annotated_path}')
    return {'input_values': raw, 'patches': measurements,
            'image_path': str(image_path.resolve()), 'layout': layout,
            'method': 'roi_rgb_median_nearest_reference'}
