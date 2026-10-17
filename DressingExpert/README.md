# DressingExpert

CSV 지식베이스와 Python 추론 알고리즘을 분리한 실험용 전문가 시스템입니다.
현재 실행 기본값은 `demo_rules.csv`를 변환한 `rules.json`입니다.

## 실행

프로젝트 루트(MedicalRAG)에서 실행합니다.

```sh
python3 DressingExpert/csvToJson.py
python3 DressingExpert/dressingExpert.py
python3 -m unittest discover -s DressingExpert/tests -v
```

CSV 변환기에 입력·출력 경로도 지정할 수 있습니다. 출력 파일은 덮어씁니다.
CSV 조건 안에 쉼표를 쓰면 CSV 문법에 따라 셀 전체를 큰따옴표로 감싸야 합니다.

## 파일별 책임

- `csvToJson.py`: CSV → JSON 저장. import 시 파일을 변경하지 않습니다.
- `dressingExpert.py`: 파일 로딩, 센서 등급 변환, 추론 호출, 행동 설명 연결.
- `inference.py`: 조건 파싱·평가와 연쇄 추론. 파일이나 UI에 의존하지 않습니다.
- `thresholds.csv`: 센서 등급 구간(하한 포함·상한 제외).
- `actions.csv`: 행동 코드, 심각도, 설명. 심각도 내림차순으로 후보를 표시합니다.

UI나 다른 Python 코드에서는 다음처럼 호출합니다.

```python
from DressingExpert.dressingExpert import run
from DressingExpert.inference import infer

result = run()  # 파일 기반 데모
result = infer(
    {"ph": "high", "co2": "high"},
    [{"id": "R1", "condition": "ph=high AND co2=high",
      "conclusion": "check_needed", "action": "recheck_tomorrow"}],
)
```

## 규칙과 결과

조건은 `항목=값` 형태이며 `!=`, `>=`, `<=`, `>`, `<`도 지원합니다.
크기 비교에는 숫자를 사용합니다. `AND`와 쉼표는 모두 논리곱입니다.
괄호·OR·NOT은 아직 지원하지 않습니다. 지원하지 않는 문법은 오류를 냅니다.

미입력, `None`, 문자열 `unknown`은 미확인 상태입니다. `false`와 다릅니다.
AND에서 하나라도 거짓이면 규칙은 거짓이며, 나머지가 미확인이어도 추가 질문 후보에 넣지 않습니다.
범위 밖 센서값은 기존처럼 `abnormal`로 표현하고, 숫자가 아닌 센서값은 오류로 알립니다.

일반 결론(`check_needed`)은 `conclusions`에 중복 없이 저장합니다.
사실 대입 결론(`ph_reliable=false`)은 새 사실을 추가하고 규칙을 다시 검사합니다.
각 규칙은 한 번만 적용하며, 기존 사실과 충돌하는 대입은 오류를 냅니다.
단일 호출 안에서는 사실을 추가하는 방식이며 사실 철회·우선순위 기반 충돌 해결은 구현하지 않았습니다.
새 측정이나 사용자 답변이 들어오면 원본 사실을 갱신한 뒤 다시 호출합니다.

반환값:

- `facts`: 입력과 추론으로 추가한 사실.
- `conclusions`: 적용된 일반 결론.
- `actions`: 적용된 규칙의 행동 후보 전체. 최종 행동 선택은 별도 정책이 필요합니다.
- `matched_rules`: 적용 규칙과 원본 조건·CF·메모. 판단 근거 추적용입니다.
- `pending_rules`, `missing_facts`: 거짓은 아니지만 정보가 부족한 규칙과 필요한 항목.
- `action_details`: `run()`에서 추가하는 행동 설명. 행동 코드는 `actions.csv`에 있어야 합니다.

## 전체 규칙으로 확장하기 전 필요한 결정

`rules.csv` 전체판은 데모와 변수명·등급명이 다릅니다.
예: `ph_level`과 `ph`, `temp_level`과 `temperature`, `saturated`와 `high`.
먼저 임계값/입력 어댑터와 전체판 규칙의 어휘를 맞춰야 합니다.
추세값·기준선·경과일·판독 신뢰 여부도 현재 센서 JSON에서 자동 계산하지 않습니다.
필요한 사실을 준비해 `infer()`에 전달해야 합니다.

CF는 현재 규칙 메타데이터로 보존할 뿐 결론 점수로 합산하지 않습니다.
따라서 전체판의 `check_needed>=0.7` 같은 규칙은 수치 사실이 별도로 제공되어야 평가됩니다.
결론이 발견됐다는 이유만으로 점수를 1로 만들거나 미확인 점수를 0으로 채우지 않습니다.
CF 결합 방식과 음의 근거 처리, 신뢰도에 따른 규칙 차단·보정 정책은 별도 구현이 필요합니다.
현재 CF가 음수인 규칙도 조건이 맞으면 일반 결론을 기록하므로,
이 단계의 출력을 CF 기반 최종 의료 판단으로 사용하지 않습니다.

CSV/JSON의 의료 내용이나 임계값을 이번 구조 변경에서 검증·변경하지 않았습니다.
