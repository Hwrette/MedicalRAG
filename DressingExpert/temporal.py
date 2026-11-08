"""일 단위 측정 이력에서 R과 회귀 대비 편차 D 계산 (연구용)."""
import math


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
