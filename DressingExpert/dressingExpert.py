import csv
import json
base_dir = __file__.rsplit("/", 1)[0]

# 임계값 딕셔너리 저장
with open(f"{base_dir}/thresholds.csv", "r", newline="", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    thresholds_data = [row for row in reader]

    thresholds_dict = {}

    for row in thresholds_data:
        ch = row["channel"]
        lvl = row["level"]
        lo = float(row["min"])
        hi = float(row["max"])
        if ch not in thresholds_dict:
            thresholds_dict[ch] = {}
        thresholds_dict[ch][lvl] = {"min": lo, "max": hi}

# print(thresholds_dict)


def get_level(channel, value):
    if channel not in thresholds_dict:
        return None
    for level, limits in thresholds_dict[channel].items():
        if limits["min"] <= value < limits["max"]:
            return level
    return None      # 어느 구간에도 안 걸림 = 이상치
    
facts = {}

# 임계값에 따라 팩트에 채널별 레벨 부여
with open(f"{base_dir}/data.json", "r", encoding="utf-8") as json_file:
    facts = json.load(json_file)
    for channel, value in facts.items():
        level = get_level(channel, value)
        if level is not None:
            facts[channel] = level
        else:
            facts[channel] = "abnormal"  # 이상치 처리
    print(facts)

with open(f"{base_dir}/rules.json", "r", encoding="utf-8") as json_file:
    rules_data = json.load(json_file)
    for rule in rules_data:
        print(f"Rule ID: {rule['id']}, Condition: {rule['condition']}, Conclusion: {rule['conclusion']}, Action: {rule['action']}, CF: {rule['cf']}, Note: {rule['note']}")