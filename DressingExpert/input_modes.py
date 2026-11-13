"""대화형 입력: 직접 수치 또는 날짜별 스마트 드레싱 사진.

이미지 보정표가 비어 있는 지표는 임의 값으로 채우지 않습니다.
사용자가 별도로 알고 있는 실측값을 보충하거나 비워 둘 수 있습니다.
"""
import math
from pathlib import Path


FIELDS = (
    ('ph_value', 'BTB 패치 pH', 0.0, 14.0),
    ('temperature_value', '온도(°C)', None, None),
    ('co2_value', '페놀레드 패치 pH (CO₂ 지표)', 0.0, 14.0),
)


def _ask_integer(input_fn, output_fn, message, *, minimum=1, maximum=None):
    while True:
        try:
            value = int(input_fn(message).strip())
        except ValueError:
            output_fn('정수를 입력해 주세요.')
            continue
        if value < minimum or (maximum is not None and value > maximum):
            output_fn(f'허용 범위: {minimum} 이상' + (f', {maximum} 이하' if maximum is not None else ''))
            continue
        return value


def _ask_number(input_fn, output_fn, label, *, minimum=None, maximum=None, optional=False):
    while True:
        text = input_fn(f'{label}' + (' (모르면 Enter)' if optional else '') + ': ').strip()
        if optional and not text:
            return None
        try:
            value = float(text)
        except ValueError:
            output_fn('숫자를 입력해 주세요.')
            continue
        if not math.isfinite(value):
            output_fn('유한한 숫자를 입력해 주세요.')
            continue
        if (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
            output_fn('입력 범위를 확인해 주세요.')
            continue
        return value


def _ask_change(input_fn, output_fn):
    while True:
        choice = input_fn('이 측정 직전에 드레싱을 교체했나요? [y/N]: ').strip().lower()
        if choice in ('', 'n', 'no'):
            return False
        if choice in ('y', 'yes'):
            return True
        output_fn('y 또는 n을 입력해 주세요.')


def _read_image(path, layout):
    # 이미지 모드에서만 cv2/numpy를 가져오므로 수동 모드에는 설치가 필요하지 않습니다.
    try:
        from .image_input import measure_image
    except ImportError:
        from image_input import measure_image
    return measure_image(path, layout)


def collect_measurements(mode, *, layout_path=None, input_fn=input, output_fn=print):
    """시간순 측정값을 받아 (현재값, 과거값 목록, 이미지 분석 기록)을 반환.

    첫 번째 측정은 day 1로 지정하고 이후 날짜는 엄격하게 증가해야 합니다.
    과거 이력에는 마지막 측정이 들어가지 않습니다.
    """
    if mode not in ('image', 'manual'):
        raise ValueError('mode는 image 또는 manual이어야 합니다.')

    layout = None
    if mode == 'image':
        try:
            from .dressingExpert import load_json
        except ImportError:
            from dressingExpert import load_json
        layout = load_json(layout_path or Path(__file__).resolve().parent / 'files' / 'image_layout.json')

    count = _ask_integer(input_fn, output_fn, '입력할 측정 횟수 (추세 분석: 3회 이상): ', maximum=50)
    records = []
    image_details = []
    last_day = 0
    last_change_day = 1
    output_fn('모든 기록은 동일 대상의 동일 드레싱에 대한 연구용 측정값이어야 합니다.')

    for index in range(count):
        output_fn(f'\n[{index + 1}/{count}번째 측정]')
        if index == 0:
            output_fn('첫 측정일을 1일 차로 기록합니다.')
            day = 1
        else:
            day = _ask_integer(input_fn, output_fn, f'측정일 (이전 {last_day}일 차보다 큰 정수): ',
                               minimum=last_day + 1)
        last_day = day
        changed = _ask_change(input_fn, output_fn)
        if changed:
            last_change_day = day
        raw = {
            'measurement_day': day,
            'day_since_start': day,
            'day_since_change': day - last_change_day + 1,
            'dressing_change_event': changed,
        }

        if mode == 'manual':
            for field, label, minimum, maximum in FIELDS:
                raw[field] = _ask_number(input_fn, output_fn, label, minimum=minimum, maximum=maximum)
        else:
            while True:
                filename = input_fn(f'{day}일 차 이미지 파일 경로 (JPG/PNG): ').strip().strip('"')
                image_path = Path(filename).expanduser()
                if not image_path.is_file():
                    output_fn('파일이 없습니다. 경로를 다시 확인해 주세요.')
                    continue
                try:
                    image_result = _read_image(image_path, layout)
                    break
                except ImportError:
                    output_fn('이미지 분석에 필요한 OpenCV(cv2) 또는 NumPy가 설치되지 않았습니다.')
                    raise
                except (ValueError, OSError) as error:
                    output_fn(f'이미지를 분석할 수 없습니다: {error}')
                except Exception as error:
                    output_fn(f'이미지 처리 중 오류가 발생했습니다: {type(error).__name__}')
                    raise
            raw.update(image_result['input_values'])
            fallback_fields = []
            for field, label, minimum, maximum in FIELDS:
                if raw.get(field) is None:
                    output_fn(f'{label}: 이미지 보정값이 없어 수치를 결정할 수 없습니다.')
                    supplied = _ask_number(input_fn, output_fn, f'{label} 수동 보충',
                                           minimum=minimum, maximum=maximum, optional=True)
                    if supplied is not None:
                        raw[field] = supplied
                        fallback_fields.append(field)
            image_details.append({
                'measurement_day': day,
                'image_path': str(image_path),
                'patches': {
                    key: {
                        'status': value.get('status'),
                        'value': value.get('value'),
                        'rgb_median': value.get('rgb_median'),
                    }
                    for key, value in image_result['patches'].items()
                },
                'manual_fallback_fields': fallback_fields,
            })
            if any(raw.get(field) is None for field, *_ in FIELDS):
                output_fn('일부 측정값이 없습니다. 전문가 시스템은 판단을 보류할 수 있습니다.')
            output_fn('이미지의 RGB→수치 보정은 검증되지 않은 연구용 추정입니다.')

        records.append(raw)
        output_fn(f'저장된 측정값: {raw}')

    return records[-1], records[:-1], image_details
