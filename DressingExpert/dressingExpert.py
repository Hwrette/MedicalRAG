"""실측값 → CSV 규칙 기반 평가 → 행동 설명 및 선택적 이력 저장."""
import argparse
import csv
import json
from pathlib import Path

if __package__:
    from .inference import assess
else:
    from inference import assess

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / 'files'


def load_json(path):
    with Path(path).open(encoding='utf-8-sig') as file:
        return json.load(file)


def load_rules(path):
    path = Path(path)
    if path.suffix.lower() == '.json':
        return load_json(path)
    with path.open(newline='', encoding='utf-8-sig') as file:
        return list(csv.DictReader(file))


def load_actions(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as file:
        return {row['action']: {**row, 'severity': int(row['severity'])}
                for row in csv.DictReader(file)}


def run(data_path=None, rules_path=None, actions_path=None, *, raw=None,
        history=None, history_path=None, config_path=None, save_history=False,
        image_path=None, layout_path=None, annotated_path=None):
    """파일 또는 raw 수치를 평가한다. 이력 저장은 save_history=True일 때만 수행한다."""
    if history is not None and history_path is not None:
        raise ValueError('history와 history_path 중 하나만 지정하세요.')
    if save_history and history_path is None:
        raise ValueError('이력 저장에는 history_path가 필요합니다.')
    if history_path is not None:
        path = Path(history_path)
        history = load_json(path) if path.exists() else []
    if history is not None and not isinstance(history, list):
        raise ValueError('history는 오래된 순서의 측정 목록이어야 합니다.')
    image_measurement = None
    if image_path is not None:
        if data_path is not None:
            raise ValueError('image_path와 data_path는 동시에 지정할 수 없습니다.')
        if __package__:
            from .image_input import measure_image, CHANNELS
        else:
            from image_input import measure_image, CHANNELS
        metadata = dict(raw or {})
        if set(metadata) & set(CHANNELS.values()):
            raise ValueError('이미지 입력 시 raw에는 경과일·의료진 승인 등 메타데이터만 지정하세요.')
        image_measurement = measure_image(
            image_path, load_json(layout_path or FILES_DIR / 'image_layout.json'), annotated_path)
        raw = {**metadata, **image_measurement['input_values']}
    elif layout_path is not None or annotated_path is not None:
        raise ValueError('layout_path/annotated_path에는 image_path가 필요합니다.')
    config = load_json(config_path or FILES_DIR / 'sensor_config.json')
    result = assess(raw if raw is not None else load_json(data_path or FILES_DIR / 'data.json'),
                    load_rules(rules_path or FILES_DIR / 'rules.csv'), history,
                    config.get('temperature_range'))
    if image_measurement is not None:
        result['image_measurement'] = image_measurement
    result['sensor_configuration'] = config
    catalog = load_actions(actions_path or FILES_DIR / 'actions.csv')
    result['action_details'] = [catalog[a] for a in result['actions']]
    if save_history:
        # 무효 측정도 보존하여 연속 경고가 누락 구간을 건너뛰지 않게 한다.
        records = [*(history or []), result]
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        temporary.replace(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--data', type=Path)
    source.add_argument('--image', type=Path)
    parser.add_argument('--layout', type=Path)
    parser.add_argument('--annotated', type=Path)
    parser.add_argument('--history', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--save-history', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(data_path=args.data, history_path=args.history,
                         config_path=args.config, save_history=args.save_history,
                         image_path=args.image, layout_path=args.layout, annotated_path=args.annotated),
                     indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
