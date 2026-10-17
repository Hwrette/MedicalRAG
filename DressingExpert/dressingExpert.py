"""센서 데이터 로딩 → 등급 변환 → 추론 → 행동 설명 연결."""

import csv
import json
import math
from pathlib import Path

if __package__:
    from .inference import infer
else:
    from inference import infer

BASE_DIR = Path(__file__).resolve().parent


def load_json(path):
    with Path(path).open(encoding="utf-8-sig") as file:
        return json.load(file)


def load_thresholds(path):
    thresholds = {}
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            thresholds.setdefault(row["channel"], {})[row["level"]] = {
                "min": float(row["min"]), "max": float(row["max"])
            }
    return thresholds


def get_level(channel, value, thresholds):
    """하한 포함·상한 제외 구간. 미입력은 unknown, 범위 밖은 abnormal."""
    if value is None or value == "unknown":
        return "unknown"
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{channel}: 유한한 센서 숫자가 필요합니다: {value!r}")
    if channel not in thresholds:
        raise ValueError(f"임계값이 없는 센서입니다: {channel}")
    for level, limits in thresholds[channel].items():
        if limits["min"] <= value < limits["max"]:
            return level
    return "abnormal"


def build_facts(raw, thresholds):
    return {channel: get_level(channel, value, thresholds) for channel, value in raw.items()}


def load_actions(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        return {
            row["action"]: {"action": row["action"], "severity": int(row["severity"]), "text": row["text"]}
            for row in csv.DictReader(file)
        }


def run(data_path=None, rules_path=None, thresholds_path=None, actions_path=None):
    thresholds = load_thresholds(thresholds_path or BASE_DIR / "thresholds.csv")
    facts = build_facts(load_json(data_path or BASE_DIR / "data.json"), thresholds)
    result = infer(facts, load_json(rules_path or BASE_DIR / "rules.json"))
    action_catalog = load_actions(actions_path or BASE_DIR / "actions.csv")
    # 모든 후보를 보존한다. severity는 CSV에 정의된 표시 순서에만 사용한다.
    result["action_details"] = sorted(
        [action_catalog[action] for action in result["actions"]],
        key=lambda item: item["severity"], reverse=True,
    )
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
