# DressingExpert

실측 수치를 CSV 규칙으로 분류하고, 복합 신호·추세·지속성을 평가하는 연구용 전문가 시스템입니다.
기존 R01~R109, A01~A18에서 페놀레드 입력을 CO₂로 변경하고 Q01/Q02 보조 규칙을 추가했습니다. 현재는 임시 수치를 사용하는 시뮬레이션 모드입니다. 감염 확진이나 검증된 임상 판단을 제공하는 시스템은 아닙니다.

## 실행

프로젝트 루트에서 실행합니다. Python 표준 라이브러리만 필요합니다.

```sh
python3 DressingExpert/dressingExpert.py
python3 -m unittest discover -s DressingExpert/tests -v
```

기본 입력은 `DressingExpert/files/data.json`, 규칙 원본은 `DressingExpert/files/rules.csv`입니다.
CSV를 직접 읽으므로 규칙 수정 후 변환할 필요가 없습니다. JSON 사본이 필요하면 다음 명령을 실행합니다.

```sh
python3 DressingExpert/csvToJson.py
```

## 수치 입력

```python
from DressingExpert.dressingExpert import run

result = run(raw={
    "ph_value": 6.8,
    "temperature_value": 37.2,
    "co2_value": 800,
    "day_since_start": 1,
    "day_since_change": 1,
    "dressing_change_event": False,
})
print(result["final_assessment"])
print(result["indicator_levels"])
print(result["actions"])
print(result["fired_rules"])
```

기존 `ph`, `temperature`, `co2`, `humidity` 입력을 새 이름으로 자동 변환하지 않습니다.
페놀레드는 `co2_value`(임시 단위 ppm)를 받으며 이전 `phenol_red_ph_value` 입력은 변환하지 않습니다. 세 필수 측정값은 숫자로 전달합니다.

`thresholds.csv`와 사전 등급 변환을 제거했습니다. 분류 경계는 R01~R15의 수치 조건에만 있습니다.
`normal → observation → caution → infection_risk → high_risk`의 5단계를 사용합니다.
내부 순서는 단계 변화 비교용이며 점수를 합산하지 않습니다.

`files/sensor_config.json`의 `temperature_range`는 **입력 유효성 검사용 장치 범위**입니다.
사용자 제안에 따라 **36~40℃를 임시 설정**했으며, 실제 센서 사양으로 확인된 범위가 아닙니다.
따라서 현재 설정에서는 36℃ 미만도 유효하지 않습니다. 실제 사양 확인 후 수정해야 합니다.
이 범위를 생략하면 온도 유효성과 종합 판단을 보류하고 설정 경고를 반환합니다.
BTB pH의 유효 범위는 0~14, CO₂ 입력은 0 이상의 유한 숫자입니다. CO₂는 센서 상한이 아직 정해지지 않았습니다.

## 이력과 시간

```python
result = run(
    raw={"ph_value": 7.2, "temperature_value": 37.7, "co2_value": 1200},
    history_path="/tmp/my-wound-history.json",
    save_history=True,
)
```

또는 `history=[이전_측정값, ...]`를 전달합니다. 이력은 **동일 대상·동일 상처의 오래된 순서**이며,
현재 측정은 포함하지 않습니다. 원시 입력 객체와 이전 결과의 `input_values`를 모두 지원합니다.
이전 값도 현재 CSV로 재분류합니다. `history`와 `history_path`는 동시에 지정하지 않습니다.

```sh
python3 DressingExpert/dressingExpert.py --data DressingExpert/files/data.json --history /tmp/my-wound-history.json --save-history
```

저장은 명시적으로 요청할 때만 실행합니다. 같은 측정을 다시 저장하면 별도 측정으로 누적되므로
한 측정당 한 번만 저장해야 합니다. 이력 파일은 한 프로세스에서 순차적으로 사용합니다.
유효하지 않은 측정도 기록해 연속 경고가 누락 구간을 건너뛰지 않게 합니다.
NaN/Infinity는 유효하지 않은 입력으로 처리하고 이력에는 문자열로 보존합니다.

경과 일수는 선택적 메타데이터로 1 이상의 정수를 받습니다. 최초 측정일과 교체일은 1입니다.
호출자가 날짜를 계산해 전달하며, 교체 후에는 `day_since_change`만 초기화합니다.
`dressing_change_event=True`는 현재 측정 직전 교체를 뜻하고 직전 기록과 비교합니다.
날짜 경과만으로 위험을 올리지 않습니다. 반복은 연속 2회, 지속은 연속 3회 측정입니다.
R102의 동일 지표 고위험 지속도 3회 연속 고위험으로 해석했습니다.

## 규칙 실행 및 출력

- `inference.py`: 유효성 준비, 안전한 조건 해석, 단계별 실행, 이력 비교, 대표 평가 선택. 직접 호출할 때는 `inference.assess()`를 사용합니다.
- `dressingExpert.py`: 파일/입력 로딩, 행동 설명 연결, 선택적 이력 저장 및 CLI.
- `rules.csv`: `id,phase,condition,conclusion,group,action` 형식의 전체 규칙 원본.
- `actions.csv`: 행동 코드와 한국어 설명. severity는 호환용 메타데이터이며 판단에 쓰지 않습니다.
- `demo_rules.csv`: 이전 형식의 참고 자료이며 현재 엔진에서 사용하지 않습니다.

규칙은 검증 → 분류 → 개별 신호 → 복합 신호 → 추세 → 지속성 → 결론 → 행동 순서로 실행합니다.
같은 단계에서는 CSV 행 순서로 실행하므로 선행 결과를 쓰는 행은 뒤에 배치합니다.
조건은 Python 표기의 `and`, `or`, `not`, 비교 연산자, 연속 비교를 지원합니다.
허용한 AST 문법만 해석하며 함수 호출, 속성 접근, 임의 코드 실행은 허용하지 않습니다.
결론 `변수=단계`는 단계 값을 지정하고, 단일 변수명은 참인 신호를 생성합니다.

세 측정값이 모두 유효해야 복합 신호와 종합 결론을 생성합니다. 하나라도 무효이면
`insufficient_evidence`를 대표 결과로 선택하면서 유효한 개별 신호는 보존합니다.
두 지표 조합 및 그 강도는 세 지표 조합과 중복하지 않습니다. 온도+페놀레드만의 강한 조합은
보조 복합 신호로 보존하며 R99의 강한 종합 결론으로 승격하지 않습니다.

출력은 `input_values`, `indicator_levels`, `individual_signals`, `combined_signals`,
`trend_results`, `persistence_results`, `conclusions`, `final_assessment`, `actions`,
`fired_rules`를 포함합니다. `facts`, `matched_rules`, `action_details`,
`sensor_configuration`, `configuration_warnings`로 근거와 설정도 확인할 수 있습니다.
여러 결론·행동을 보존하며 대표 평가는 명세서 우선순위를 적용합니다.

`clinician_change_approved=True`일 때만 A17의 교체 행동을 생성합니다.
여기에 `clinician_inspect_approved=True`도 있어야 A18의 교체 및 상처 확인 행동을 생성합니다.
이 두 값은 의료진 결정을 전달하는 입력이며 센서 규칙이 자동으로 승인하지 않습니다.
A15는 기록 및 예정된 관찰 계속이라는 행동 설명으로 표현합니다.
관찰 간격과 수치 기준은 제공된 연구 명세를 구현한 것이며 임상적으로 검증한 값이 아닙니다.


## 하루 단위 알고리즘 및 임시 CO₂ 규칙

`files/algorithm_config.json`에 pH/온도 계수와 D 경계를 둡니다. 분류용 CO₂ 경계는
`rules.csv` R11~R15에만 있으며, 임시 구간은 <600, 600~1000, 1000~1500,
1500~2500, >=2500 ppm입니다(각 하한 포함). 임상 또는 센서 검증을 거친 값이 아닙니다.
CO₂가 높을수록 단계가 올라가며 기존 복합·지속성 규칙은 이 단계로 판단합니다.

`measurement_day`는 최초 측정일부터 센 일 단위 시점입니다. 첫날은 1, 12시간 후는 1.5,
하루 후는 2입니다. 생략하면 `day_since_start`를 사용합니다. 둘 다 없으면 R/D는 계산하지 않습니다.
이력은 같은 대상·상처의 오래된 순서로 전달합니다. 중복/역순 시간은 계산 보류,
무효 측정은 연속 구간을 끊습니다. R은 최소 2회, D 분류는 최소 3회 측정이 필요합니다.

- pH R: alpha=40, beta=500, limit=8.5 (제공한 예시).
- 온도 R: alpha=10, beta=20, limit=40 (동작 확인용 임시값).
- 회귀: 최근 연속 유효 측정 최대 7회. D는 최근 기울기에서 회귀 기울기를 뺀 값.
- D 경계: pH ±0.018/±0.03, 온도 ±0.015/±0.04 (단위 pH/일, ℃/일).
- R 구간: <20부터 20 간격으로 `band_0`~`band_4`. >=100은 `out_of_scale`.
- X>=limit이면 R을 계산하지 않고 `limit_exceeded`. 감염 확진 표현은 사용하지 않습니다.
- Q01: R>=60 또는 상한 도달/초과 시 `numeric_score_review`와 재확인 행동.
- Q02: D가 양의 큰 편차이면 `numeric_trend_review`와 재확인 행동.

Q01/Q02는 세 센서값이 모두 유효할 때 적용하는 임시 보조 규칙입니다.
기존 대표 평가를 점수로 덮어쓰지 않고 `conclusions`와 `actions`에 반영합니다.
`algorithm_results`에서 R·D와 각각의 계산 상태를 확인합니다. 두 점에서 D=0인 것을
안정으로 오인하지 않게 D는 미정으로 둡니다. `simulation_mode=true`와 설정 설명을 출력합니다.

3일 샘플 실행(기록 파일을 변경하지 않음):

```sh
python3 DressingExpert/dressingExpert.py --history DressingExpert/files/demo_history.json
```

## 이미지 입력 연결

```sh
python3 DressingExpert/dressingExpert.py --image input_file.jpg --day 1 --annotated /tmp/patches.jpg
python3 "btb ph.py" --image input_file.jpg --day 1
```

`image_input.py`는 `files/image_layout.json`의 상대 좌표 ROI에서 RGB 중앙값을 추출합니다.
사용자 사진 방향 기준 왼쪽 원형=온도, 오른쪽 위=페놀레드(CO₂), 아래=BTB(pH)입니다.
자동 패치 인식/회전 보정은 아니므로 다른 구도에서는 ROI를 다시 지정하고 표시 이미지로 확인하세요.

BTB만 사용자가 확인한 기존 표를 연결했습니다. 최근접 RGB 기준값 선택이며 연속 역산은 아닙니다.
기존 표의 CO₂ 필드는 제거했습니다. BTB 거리 제한은 미설정이므로 가장 가까운 값을 항상 선택합니다.
표 자체와 촬영 조건의 정확도를 검증해야 합니다. 나머지 두 패치의 보정표는 비어 있고,
실제 이미지에서 임의 온도·CO₂를 만들지 않습니다. 이 경우 전체 판단은 `insufficient_evidence`입니다.

보정표는 패치별 `calibration: [{"rgb": [R,G,B], "value": 실제수치}, ...]` 형식이며
최소 두 점이 필요합니다. `max_rgb_distance`로 허용 거리를 설정할 수 있습니다.
`null`이면 거리 제한 없이 최근접 값을 선택합니다. ROI·중앙값 추출 방식과 같은 조건으로
보정표를 만들어야 합니다. 이미지 입력의 `raw`에는 시점·교체 이벤트 등 메타데이터만 전달합니다.
온도/CO₂ 보정 데이터가 확보되면 보정표만 채워 동일 추론 경로로 전달할 수 있습니다.
