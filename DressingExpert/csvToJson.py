"""CSV 원본을 같은 열 구조의 JSON으로 저장한다."""

import argparse
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"


def convert_csv_to_json(csv_path, json_path):
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as file:
        rules = list(csv.DictReader(file))
    with Path(json_path).open("w", encoding="utf-8") as file:
        json.dump(rules, file, indent=4, ensure_ascii=False)
    return rules


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=FILES_DIR / "demo_rules.csv")
    parser.add_argument("json_path", nargs="?", type=Path, default=FILES_DIR / "rules.json")
    args = parser.parse_args()
    convert_csv_to_json(args.csv_path, args.json_path)
