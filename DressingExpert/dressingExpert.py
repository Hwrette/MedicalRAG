import csv
import json
base_dir = __file__.rsplit("/", 1)[0]

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

print(thresholds_dict)


def thresholds(channel):
    if channel not in channels:
        raise ValueError(f"Channel '{channel}' not found in thresholds data.")


