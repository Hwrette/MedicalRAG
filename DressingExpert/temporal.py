"""일 단위 측정 이력에서 R과 회귀 대비 편차 D 계산 (연구용)."""
import json
import math
from pathlib import Path


def finite(x):
    return type(x) in (int, float) and math.isfinite(x)


def calculate(series, config):
    result = dict(risk_score=None, risk_level=None, recent_slope=None,
                  trend_slope=None, slope_deviation=None, trend_status=None,
                  status='insufficient_history', risk_status='insufficient_history')
    if len(series) < 2:
        return result
    if any(not finite(t) or not finite(x) for t, x in series):
        return {**result, 'status': 'invalid_measurement', 'risk_status': 'invalid_measurement'}
    if any(b[0] <= a[0] for a, b in zip(series, series[1:])):
        return {**result, 'status': 'invalid_time_order', 'risk_status': 'invalid_time_order'}
    window = config['window']
    if type(window) is not int or window < 3:
        raise ValueError('회귀 window는 3 이상의 정수여야 합니다.')
    points = series[-window:]
    t, x = points[-1]
    previous_t, previous_x = points[-2]
    slope = (x - previous_x) / (t - previous_t)
    result['recent_slope'] = slope
    alpha, beta, limit = (config[k] for k in ('alpha', 'beta', 'x_limit'))
    if not all(finite(v) for v in (alpha, beta, limit)):
        raise ValueError('알고리즘 계수는 유한 숫자여야 합니다.')
    if x >= limit:
        result.update(risk_status='limit_reached_or_exceeded', risk_level='limit_exceeded')
    else:
        score = alpha / (limit - x) + beta * slope
        if not math.isfinite(score):
            result['risk_status'] = 'numeric_overflow'
        else:
            level = next((f'band_{i}' for i, bound in enumerate((20, 40, 60, 80, 100)) if score < bound), 'out_of_scale')
            result.update(risk_score=score, risk_level=level, risk_status='calculated')
    # 두 점이면 D=0은 필연적이므로 안정으로 분류하지 않는다.
    if len(points) < 3:
        return result
    times = [p[0] - points[0][0] for p in points]
    mean_t = sum(times) / len(points)
    mean_x = sum(p[1] for p in points) / len(points)
    trend = sum((tt - mean_t) * (p[1] - mean_x) for tt, p in zip(times, points)) / sum((tt - mean_t)**2 for tt in times)
    deviation = slope - trend
    low, high = config['deviation_bounds']
    if not (finite(low) and finite(high) and 0 < low < high):
        raise ValueError('편차 경계값은 0 < low < high여야 합니다.')
    status = ('rapid_decrease' if deviation < -high else
              'slight_decrease' if deviation < -low else
              'similar_to_trend' if deviation <= low else
              'slight_increase' if deviation <= high else 'rapid_increase')
    result.update(trend_slope=trend, slope_deviation=deviation, trend_status=status, status='calculated')
    return result


def derive(raw, history, config, temperature_range):
    records = [item.get('input_values', item) for item in history] + [raw]
    output = {}
    for sensor, settings in config['sensors'].items():
        # 무효 측정 구간을 건너뛰지 않고 최근 연속 유효 구간만 사용한다.
        series = []
        for item in records:
            value = item.get(sensor + '_value')
            day = item.get('measurement_day', item.get('day_since_start'))
            valid = finite(value) and finite(day) and day >= 1
            if sensor == 'ph':
                valid = valid and 0 <= value <= 14
            elif sensor == 'temperature':
                valid = valid and temperature_range is not None and temperature_range[0] <= value <= temperature_range[1]
            if not valid:
                series = []
            else:
                series.append((day, value))
        output[sensor] = calculate(series, settings)
    return output


def main():
    files = Path(__file__).resolve().parent / 'files'
    config = json.loads((files / 'algorithm_config.json').read_text(encoding='utf-8'))
    sensor_config = json.loads((files / 'sensor_config.json').read_text(encoding='utf-8'))
    choice = input('지표 선택 [1: pH, 2: 온도]: ').strip()
    while choice not in ('1', '2'):
        choice = input('1 또는 2를 입력하세요: ').strip()
    sensor = 'ph' if choice == '1' else 'temperature'
    low, high = (0, 14) if sensor == 'ph' else sensor_config['temperature_range']
    while True:
        try:
            count = int(input('며칠치 측정값을 입력할까요? '))
            if count >= 1:
                break
        except ValueError:
            pass
        print('1 이상의 정수를 입력하세요.')
    print(f'측정일과 값({low}~{high})을 한 줄씩 입력하세요. 예: 1 {6.2 if sensor == "ph" else 37.2}')
    print('최근 변화율은 2회, 회귀 기울기와 D는 3회부터 계산됩니다.')
    series = []
    while len(series) < count:
        line = input(f'[{len(series) + 1}/{count}] 측정일 측정값 > ').strip()
        try:
            day, value = map(float, line.split())
        except ValueError:
            print('공백으로 구분한 숫자 두 개를 입력하세요.')
            continue
        if not finite(day) or day < 1 or (series and day <= series[-1][0]):
            print('측정일은 1 이상이며 이전 측정일보다 커야 합니다.')
            continue
        if not finite(value) or not low <= value <= high:
            print(f'현재 설정의 허용 범위는 {low}~{high}입니다.')
            continue
        series.append((day, value))
    if len(series) < 2:
        print('계산하려면 측정값이 두 개 이상 필요합니다.')
        return
    result = calculate(series, config['sensors'][sensor])
    for key, label in [('recent_slope', '최근 변화율'), ('trend_slope', '회귀 기울기'),
                       ('slope_deviation', '편차 D'), ('risk_score', '연구용 점수 R')]:
        value = result[key]
        print(f'{label}: {value:.4f}' if value is not None else f'{label}: 계산 보류')
    print('추세 상태:', result['trend_status'] or result['status'])
    print('점수 상태:', result['risk_status'], result['risk_level'] or '')


if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print('입력을 종료했습니다.')
