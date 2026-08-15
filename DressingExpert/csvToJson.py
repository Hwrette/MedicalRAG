import json
import csv

import os
base_dir = os.path.dirname(os.path.abspath(__file__))

with open(f"{base_dir}/rules.csv", "r", newline="", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    rules_data = [row for row in reader]


with open(f"{base_dir}/data.json", "w", encoding="utf-8") as json_file:
    json.dump(rules_data, json_file, indent=4, ensure_ascii=False)
        
