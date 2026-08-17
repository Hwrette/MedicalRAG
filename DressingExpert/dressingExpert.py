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
    


# 임계값에 따라 팩트에 채널별 레벨 부여
with open(f"{base_dir}/data.json", "r", encoding="utf-8") as json_file:
    raw = json.load(json_file)

facts = {}
facts["conc"] = []  # 결론을 담을 리스트 초기화

for channel, value in raw.items():
    level = get_level(channel, value)
    facts[channel] = level if level is not None else "abnormal"

print(facts)

with open(f"{base_dir}/rules.json", "r", encoding="utf-8") as json_file:
    rules_data = json.load(json_file)
    for rule in rules_data:

        print(f"Evaluating rule: {rule['id']} with condition: {rule['condition']}")
        condition = rule["condition"]

        # AND 파싱
        if "AND" in condition:
            ALL_satisfied = True
            sub_conditions = condition.split("AND")
            for rules in range(len(sub_conditions)):
                sub_conditions[rules] = sub_conditions[rules].strip()
                current_sub_condition = sub_conditions[rules]
                # AND 파싱 후 = 파싱
                if "=" in current_sub_condition:
                    parsed_current_sub_condition = current_sub_condition.split("=")
                    channel = parsed_current_sub_condition[0].strip()
                    expected_value = parsed_current_sub_condition[1].strip()
                    if channel in facts and facts[channel] == expected_value:
                        print(f"Sub-condition {current_sub_condition} is satisfied.")
                        ALL_satisfied = True
                    else:
                        ALL_satisfied = False
                        break  # 하나라도 만족하지 않으면 AND 조건 전체가 만족하지 않음

                        
            if ALL_satisfied and rule["conclusion"] not in facts["conc"]:
                facts["conc"].append(rule["conclusion"])

                
        # AND 없는 경우 = 파싱
        elif "=" in condition:
            parsed_condition = condition.split("=")
            channel = parsed_condition[0].strip()
            expected_value = parsed_condition[1].strip()
            if channel in facts and facts[channel] == expected_value:
                print(f"Condition {condition} is satisfied.")
                if rule["conclusion"] not in facts["conc"]:
                    facts["conc"].append(rule["conclusion"])
                continue 
            
            # print(f"Evaluating rule: {rule['id']} with sub-conditions: {sub_conditions}")
            
        # print(f"Evaluating rule: {rule['id']} with condition: {condition}")

print(facts)