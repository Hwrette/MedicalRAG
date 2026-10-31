"""데이터와 분리된 규칙 평가기. 외부 라이브러리 없이 사용할 수 있다."""

from __future__ import annotations

import math
import operator
import re
from dataclasses import dataclass
from typing import Any, Mapping


# 연산자 확장은 이 표에서 관리한다. 조건 문자열을 eval로 실행하지 않는다.
OPERATORS = {
    "=": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}
CONDITION_PATTERN = re.compile(r"^([A-Za-z_][\w]*)\s*(!=|>=|<=|=|>|<)\s*(.+)$")


@dataclass(frozen=True)
class Condition:
    field: str
    operator: str
    expected: Any


def parse_value(value: str) -> Any:
    """CSV의 참/거짓과 숫자를 Python 값으로 변환한다."""
    value = value.strip()
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        number = float(value)
    except ValueError:
        return value
    if not math.isfinite(number):
        raise ValueError(f"유한한 숫자가 필요합니다: {value}")
    return number


def parse_condition(expression: str) -> list[Condition]:
    """AND 또는 쉼표로 연결한 조건을 파싱한다. 둘 다 논리곱이다."""
    conditions = []
    for part in re.split(r"\bAND\b|,", expression):
        match = CONDITION_PATTERN.fullmatch(part.strip())
        if not match:
            raise ValueError(f"지원하지 않는 조건입니다: {part!r}")
        field, operation, value = match.groups()
        conditions.append(Condition(field, operation, parse_value(value)))
    return conditions


def evaluate_condition(condition: Condition, facts: Mapping[str, Any]) -> bool | None:
    """참/거짓/미확인(None)을 반환한다. 잘못된 자료형은 오류로 알린다."""
    actual = facts.get(condition.field)
    if actual is None or actual == "unknown":
        return None
    expected = condition.expected
    # Python에서는 True == 1이므로 자료형을 먼저 구별한다.
    if isinstance(expected, bool):
        compatible = isinstance(actual, bool)
    elif isinstance(expected, (int, float)):
        compatible = isinstance(actual, (int, float)) and not isinstance(actual, bool)
        if compatible:
            compatible = math.isfinite(actual)
    else:
        compatible = isinstance(actual, str)
    if not compatible:
        raise ValueError(f"{condition.field}: 값 {actual!r}의 자료형이 조건과 다릅니다.")
    if condition.operator not in ("=", "!=") and isinstance(expected, (str, bool)):
        raise ValueError(f"{condition.field}: 크기 비교에는 숫자가 필요합니다.")
    return OPERATORS[condition.operator](actual, expected)


def evaluate_rule(conditions: list[Condition], facts: Mapping[str, Any]) -> bool | None:
    states = [evaluate_condition(condition, facts) for condition in conditions]
    if False in states:
        return False
    return None if None in states else True


def infer(facts: Mapping[str, Any], rules: list[dict]) -> dict:
    """새 사실이 생기지 않을 때까지 추론한다. 각 규칙은 한 번만 적용한다.

    일반 결론은 conclusions에, key=value 형태의 결론은 facts에 저장한다.
    CF는 기록만 하며 확률이나 결론 점수로 계산하지 않는다.
    """
    working_facts = dict(facts)
    parsed_rules = []
    ids = set()
    for rule in rules:
        rule_id = rule.get("id", "").strip()
        if not rule_id or rule_id in ids:
            raise ValueError(f"규칙 ID가 없거나 중복됩니다: {rule_id!r}")
        ids.add(rule_id)
        try:
            conditions = parse_condition(rule["condition"])
            conclusion = rule.get("conclusion", "").strip()
            assignment = None
            if "=" in conclusion:
                assignments = parse_condition(conclusion)
                if len(assignments) != 1 or assignments[0].operator != "=":
                    raise ValueError("사실을 추가하는 결론은 key=value 형식이어야 합니다.")
                assignment = assignments[0]
            cf = rule.get("cf")
            cf = float(cf) if cf not in (None, "") else None
            if cf is not None and (not math.isfinite(cf) or not -1 <= cf <= 1):
                raise ValueError("CF는 -1부터 1 사이여야 합니다.")
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"규칙 {rule_id}: {error}") from error
        parsed_rules.append((rule, conditions, conclusion, assignment, cf))

    fired_ids = set()
    matched_rules = []
    conclusions = []
    actions = []
    while True:
        changed = False
        for rule, conditions, conclusion, assignment, cf in parsed_rules:
            if rule["id"] in fired_ids or evaluate_rule(conditions, working_facts) is not True:
                continue
            if assignment is not None:
                previous = working_facts.get(assignment.field)
                if previous is None or previous == "unknown":
                    working_facts[assignment.field] = assignment.expected
                    changed = True
                elif type(previous) is not type(assignment.expected) or previous != assignment.expected:
                    raise ValueError(f"규칙 {rule['id']}: {assignment.field}의 기존 사실과 충돌합니다.")
            elif conclusion and conclusion not in conclusions:
                conclusions.append(conclusion)
            action = rule.get("action", "").strip()
            if action and action not in actions:
                actions.append(action)
            fired_ids.add(rule["id"])
            matched_rules.append({**rule, "cf": cf})
        if not changed:
            break

    pending_rules = []
    for rule, conditions, *_ in parsed_rules:
        if rule["id"] not in fired_ids and evaluate_rule(conditions, working_facts) is None:
            missing = list(dict.fromkeys(
                condition.field for condition in conditions
                if evaluate_condition(condition, working_facts) is None
            ))
            pending_rules.append({"id": rule["id"], "missing_facts": missing})
    return {
        "facts": working_facts,
        "conclusions": conclusions,
        "actions": actions,
        "matched_rules": matched_rules,
        "pending_rules": pending_rules,
        "missing_facts": list(dict.fromkeys(
            field for rule in pending_rules for field in rule["missing_facts"]
        )),
    }
