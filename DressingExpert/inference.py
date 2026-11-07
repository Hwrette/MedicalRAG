"""단계별 CSV 규칙 실행과 측정 이력 준비. 센서 분류 경계는 rules.csv에만 둔다."""
from __future__ import annotations

import ast
import math
import operator
from collections.abc import Mapping

LEVELS = ('normal', 'observation', 'caution', 'infection_risk', 'high_risk')
INDICATORS = {'ph': 'ph_value', 'temperature': 'temperature_value',
              'co2': 'co2_value'}
PRIORITY = ('insufficient_evidence', 'high_concern_pattern',
            'very_strong_combined_signal_pattern', 'strong_combined_signal_pattern',
            'isolated_high_risk_pattern', 'combined_signal_pattern',
            'isolated_signal_pattern', 'observation_pattern', 'no_warning_signal_detected')
PHASES = ('validation', 'classification', 'individual', 'combined', 'trend',
          'persistence', 'conclusion', 'action')
COMPARISONS = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
               ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge}


def expression_value(node, facts):
    """허용한 문법만 해석한다. 함수 호출·속성 접근·eval은 사용하지 않는다."""
    if isinstance(node, ast.Expression):
        return expression_value(node.body, facts)
    if isinstance(node, ast.Name):
        if node.id not in facts:
            raise ValueError(f'정의되지 않은 규칙 변수: {node.id}')
        return facts[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bool, int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp):
        value = expression_value(node.operand, facts)
        if isinstance(node.op, ast.Not):
            return not value
        if isinstance(node.op, ast.USub) and type(value) in (int, float):
            return -value
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        values = (bool(expression_value(v, facts)) for v in node.values)
        return all(values) if isinstance(node.op, ast.And) else any(values)
    if isinstance(node, ast.Compare):
        left = expression_value(node.left, facts)
        for op, right_node in zip(node.ops, node.comparators):
            right = expression_value(right_node, facts)
            if type(op) not in COMPARISONS:
                raise ValueError('지원하지 않는 비교 연산자')
            if not COMPARISONS[type(op)](left, right):
                return False
            left = right
        return True
    raise ValueError(f'지원하지 않는 규칙 문법: {ast.dump(node)}')


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_range(temperature_range):
    if temperature_range is None:
        return
    if (not isinstance(temperature_range, (list, tuple)) or len(temperature_range) != 2
            or not all(finite_number(x) for x in temperature_range)
            or temperature_range[0] >= temperature_range[1]):
        raise ValueError('temperature_range에는 최솟값 < 최댓값인 두 유한 숫자가 필요합니다.')


def initial_facts(raw, rules, temperature_range):
    if not isinstance(raw, Mapping):
        raise ValueError('측정값은 객체여야 합니다.')
    facts = {}
    for rule in rules:
        output = rule['conclusion']
        if output:
            key, sep, _ = output.partition('=')
            facts[key] = None if sep else False
    for name, key in INDICATORS.items():
        value = raw.get(key)
        limits = temperature_range if name == 'temperature' else ((0, float('inf')) if name == 'co2' else (0, 14))
        valid = finite_number(value) and limits is not None and limits[0] <= value <= limits[1]
        facts[key] = value if valid else None
        facts[name + '_valid'] = valid
        facts[name + '_rank'] = -1
    for key in ('dressing_change_event', 'clinician_change_approved', 'clinician_inspect_approved'):
        value = raw.get(key, False)
        if type(value) is not bool:
            raise ValueError(f'{key}: boolean 값이 필요합니다.')
        facts[key] = value
    for key in ('day_since_start', 'day_since_change'):
        value = raw.get(key)
        if value is not None and (type(value) is not int or value < 1):
            raise ValueError(f'{key}: 1 이상의 정수가 필요합니다.')
        facts[key] = value
    if raw.get('day_since_start') and raw.get('day_since_change'):
        if raw['day_since_change'] > raw['day_since_start']:
            raise ValueError('교체 이후 일수는 최초 측정 이후 일수를 초과할 수 없습니다.')
    if facts['dressing_change_event'] and raw.get('day_since_change') not in (None, 1):
        raise ValueError('드레싱 교체일의 day_since_change는 1이어야 합니다.')
    return facts


def apply_rules(facts, rules, phase, groups, matched):
    for rule in rules:
        if rule['phase'] != phase:
            continue
        # 불완전한 세트에서 전체 지표를 이용한 결론을 확정하지 않는다.
        if phase in ('combined', 'conclusion') and not facts['measurement_set_valid']:
            continue
        if phase == 'trend' and int(rule['id'][1:]) >= 76 and not facts['measurement_set_valid']:
            continue
        try:
            applies = expression_value(ast.parse(rule['condition'], mode='eval'), facts)
        except (TypeError, SyntaxError, ValueError) as error:
            raise ValueError(f"규칙 {rule['id']}: {error}") from error
        if not applies:
            continue
        output = rule['conclusion']
        if output:
            key, sep, value = output.partition('=')
            facts[key] = value if sep else True
            group = groups.setdefault(rule['group'], [])
            if key not in group:
                group.append(key)
        if rule['action'] and rule['action'] not in groups['actions']:
            groups['actions'].append(rule['action'])
        matched.append(dict(rule))


def classify(raw, rules, temperature_range):
    facts = initial_facts(raw, rules, temperature_range)
    apply_rules(facts, rules, 'validation', {}, [])
    apply_rules(facts, rules, 'classification', {}, [])
    return facts


def prepare_history(facts, history, rules, temperature_range):
    # 최신 이력도 현재 CSV로 재분류한다. 저장된 파생 결론은 신뢰하지 않는다.
    previous = [classify(item.get('input_values', item), rules, temperature_range) for item in history]
    facts['history_exists'] = bool(previous)
    facts['prior_valid_exists'] = any(p['measurement_set_valid'] for p in previous)
    facts['worsening_count'] = facts['improving_count'] = facts['strong_worsening_count'] = 0
    facts['changed_count'] = 0
    facts['strong_risk_worsening'] = False
    facts['all_stable_three'] = len(previous) >= 2
    for name in INDICATORS:
        level = facts[name + '_level']
        rank = LEVELS.index(level) if level in LEVELS else -1
        facts[name + '_rank'] = rank
        prior_levels = [p[name + '_level'] for p in previous[-2:]]
        comparable = rank >= 0 and bool(prior_levels) and prior_levels[-1] in LEVELS
        delta = rank - LEVELS.index(prior_levels[-1]) if comparable else 0
        facts[name + '_comparable'] = comparable
        facts[name + '_delta'] = delta
        facts['worsening_count'] += comparable and delta > 0
        facts['improving_count'] += comparable and delta < 0
        facts['strong_worsening_count'] += comparable and delta >= 2
        facts['changed_count'] += comparable and delta != 0
        facts['strong_risk_worsening'] |= comparable and delta >= 2 and rank >= 2
        for suffix, minimum in (('risk_run', 2), ('high_run', 4)):
            run = 0
            for item in [level] + list(reversed(prior_levels)):
                if item not in LEVELS or LEVELS.index(item) < minimum:
                    break
                run += 1
            facts[name + '_' + suffix] = run
        facts['all_stable_three'] &= rank >= 0 and len(prior_levels) == 2 and all(p == level for p in prior_levels)
    ranks = [facts[n + '_rank'] for n in INDICATORS]
    for key, predicate in [('risk', lambda r: r >= 2), ('advanced', lambda r: r >= 3),
                           ('high', lambda r: r == 4), ('normal', lambda r: r == 0),
                           ('observation', lambda r: r == 1)]:
        facts[key + '_count'] = sum(predicate(r) for r in ranks)


def assess(raw, rules, history=None, temperature_range=None, algorithm_config=None):
    """history는 오래된 순서의 동일 상처 측정 목록이며 현재 측정은 제외한다."""
    validate_range(temperature_range)
    ids = set()
    for rule in rules:
        if not rule.get('id') or rule['id'] in ids or rule.get('phase') not in PHASES:
            raise ValueError('규칙 ID 중복/누락 또는 잘못된 phase')
        ids.add(rule['id'])
    facts = initial_facts(raw, rules, temperature_range)
    groups = {key: [] for key in ('individual_signals', 'combined_signals', 'trend_results',
                                  'persistence_results', 'conclusions', 'actions')}
    matched = []
    algorithm_results = {}
    for sensor in ('ph', 'temperature'):
        facts[sensor + '_score_alert'] = False
        facts[sensor + '_deviation_alert'] = False
    if algorithm_config is not None:
        if __package__:
            from .temporal import derive
        else:
            from temporal import derive
        algorithm_results = derive(raw, history or [], algorithm_config, temperature_range)
        for sensor, values in algorithm_results.items():
            facts[sensor + '_score_alert'] = values['risk_level'] in ('band_3', 'band_4', 'out_of_scale', 'limit_exceeded')
            facts[sensor + '_deviation_alert'] = values['trend_status'] == 'rapid_increase'
    for phase in PHASES:
        apply_rules(facts, rules, phase, groups, matched)
        if phase == 'classification':
            prepare_history(facts, history or [], rules, temperature_range)
    final = next((c for c in PRIORITY if facts[c]), None)
    return {
        'algorithm_results': algorithm_results,
        'input_values': {key: (str(value) if type(value) is float and not math.isfinite(value) else value)
                         for key, value in raw.items()},
        'indicator_levels': {n + '_level': facts[n + '_level'] for n in INDICATORS},
        'individual_signals': groups['individual_signals'],
        'combined_signals': groups['combined_signals'],
        'trend_results': {key: facts[key] for key in groups['trend_results']},
        'persistence_results': {key: facts[key] for key in groups['persistence_results']},
        'conclusions': groups['conclusions'], 'final_assessment': final,
        'actions': groups['actions'], 'fired_rules': [r['id'] for r in matched],
        'facts': facts, 'matched_rules': matched,
        'configuration_warnings': (['온도 센서의 유효 측정 범위가 설정되지 않았습니다.']
                                   if temperature_range is None else []),
    }
