# 2차 제로샷 의료 RAG 최종 비교보고서

환자 질문 9개. 같은 모델(gemini-3.5-flash-lite)에 같은 지시와 질문을 주고 이전 대화 없이 조건별로 한 번씩 실행했다. 문항마다 기준 청크, 실제 검색 3건, OFF·ON 답변에서 일치하거나 빠진 내용을 한 표에 모았다. 표 바로 아래에서 당시 답변 전문과 청크 영어 원문·한국어 해석을 펼칠 수 있다.

**Hit@1은 3/9(33.3%), Hit@3은 7/9(77.8%)**다. Hit@k는 사전에 지정한 청크 ID가 실제 상위 k개에 들어간 질문의 비율이다. 기록에 벡터 유사도 점수는 없다. **ON 충실성**은 주요 주장을 검색 문단이 지지하면 2점, 일부 확대 해석이 있으면 1점, 핵심 근거가 없으면 0점으로 판독했다. OFF는 같은 문단에 사후 대조했으며 당시 근거를 제공받지 않아 충실성 점수를 매기지 않았다.

| 문항 | 기준 ID | 실제 1 → 2 → 3위 | 기준 순위 | ON 충실성 |
|---|---:|---|---|---:|
| 1. 만성 상처와 수분 균형 | 280 | 280 → 323 → 425 | 1위 | 2/2 |
| 2. 드레싱 교체 뒤 진물 증가 | 487 | 486 → 487 → 425 | 2위 | 1/2 |
| 3. 전형적 징후가 없는 치유 지연 | 275 | 37 → 203 → 36 | 미적중 | 2/2 |
| 4. 냄새와 통증 증가 | 38 | 38 → 275 → 37 | 1위 | 2/2 |
| 5. 석 달 뒤 피부 강도 | 319 | 371 → 319 → 370 | 2위 | 1/2 |
| 6. pH 단일 수치와 감염 | 481 | 206 → 491 → 558 | 미적중 | 0/2 |
| 7. 진물의 분할 수집 | 487 | 486 → 487 → 485 | 2위 | 2/2 |
| 8. 코팅과 분석물 도달 속도 | 503 | 502 → 503 → 496 | 2위 | 2/2 |
| 9. 새 피부 세포의 이동 | 314 | 314 → 368 → 367 | 1위 | 2/2 |

## 1. 오래 안 낫는 상처인데, 드레싱을 떼고 바람에 좀 말리면 더 빨리 낫나요?

지정 청크 **1위** · ON 충실성 **2/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 280** | 280은 습윤 유지와 과도한 배액으로부터 주변 피부 보호를 함께 설명한다. |
| 검색 1위 · **280** · 10쪽 | 만성 상처를 말리지 말고 수분 균형을 유지한다. 배액은 주변 피부에서 떨어지도록 관리한다. |
| 검색 2위 · **323** · 6쪽 | 약물·당뇨·산소 공급이 치유에 영향을 준다. 공기에 말리는 처치의 근거는 없다. |
| 검색 3위 · **425** · 18쪽 | 변연절제·염증 등에 관한 참고문헌 목록이다. |
| **공통 답변** | 바람에 말리지 말고 드레싱으로 습윤하게 유지한다. |
| **OFF와 문헌 대조** | 습윤 유지에 더해 세포 이동, 흉터 감소, 특정 제품까지 언급한다. 뒤의 설명은 검색 세 문단에서 확인하기 어렵다. |
| **ON과 검색 근거 대조** | 280의 건조 방지, 습윤 상태에서의 빠른 치유와 낮은 감염 위험을 인용한다. |
| **누락·적용 범위** | 과도한 배액을 조절해 주변 피부를 보호한다는 기준 요소는 양쪽 모두 빠졌다. ON의 실제 주장은 280에 충실하다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

오래 안 낫는 상처를 드레싱을 떼고 바람에 말리면 더 빨리 낫는다고 생각하기 쉽지만, 이는 **사실이 아닙니다**. 

상처는 촉촉하게 유지해야 새살이 빨리 돋고 흉터도 적게 생깁니다. 상처를 바람에 말려 딱지가 생기게 하면 오히려 다음과 같은 문제가 생길 수 있습니다.

* **회복 지연:** 상처가 마르면 세포가 이동하여 상처를 메우는 과정이 방해를 받아 오히려 치유가 더뎌집니다.
* **감염 및 흉터 위험:** 딱지가 생기면 외부 세균으로부터 보호되는 것처럼 보이지만, 상처 아래의 습한 치유 과정을 막고 흉터가 남을 확률을 높입니다.

따라서 의사의 지시에 따라 적절한 습윤 드레싱(메디폼 등)을 유지하는 것이 상처 회복에 훨씬 좋습니다. 

---
*(※ 개인별 진단이나 처방은 할 수 없으므로, 상처가 오래 낫지 않는다면 병원을 방문하여 전문의의 진료를 받으시기 바랍니다.)*

**RAG ON**

아니요, 상처를 바람에 말리면 더 빨리 낫는다는 것은 잘못된 상식입니다. 

오래 안 낫는 상처(만성 상처)는 바람에 노출시켜 말리면 안 됩니다. 상처는 촉촉한 상태를 유지해야 더 빨리 낫고 감염 위험도 줄어듭니다. 상처가 마르지 않도록 적절한 드레싱을 사용하여 적절한 습도를 유지해 주는 것이 중요합니다. ([출처: Chronic_Wounds_Evaluation_and_Management_AFP.pdf, PDF 10쪽])

※ 개인별 진단이나 치료 처방은 의료 전문인과 상담하셔야 합니다.

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 280 · 사전 기준 / 실제 검색 1위**　Chronic_Wounds_Evaluation_and_Management_AFP.pdf · PDF 10쪽

> 2026. 10. 31. য়റ 11:02Chronic Wounds: Evaluation and Management | AFP
> 10ಕ੉૑/19ಕ੉૑https://www.aafp.org/afp/2020/0201/p159?utm_source=
> Moisture balance is an essential part of wound care. Chronic
> wounds should never be exposed to air to “dry out,” as is often
> recommended. Moist wounds heal more quickly and have less risk
> of infection. If a wound appears dry, moisture needs to be added;
> this is accomplished by choosing an appropriate dressing (Table
> 3). Conversely, if a wound is draining, the drainage needs to be
> controlled and kept o" of the periwound. The proper dressing
> should hold the moisture on the wound bed to prevent
> desiccation.
> Wound edges must be free from undermining. If edges are rolled,
> they should be excised. This allows for epithelialization, which is
> the clearest sign the wound is healing.
> TREATMENT BY WOUND ETIOLOGY
> Venous Ulcers. Venous hypertension due to incompetent veins or
> venous obstruction distends the superﬁcial veins, causing wall

**한국어 해석**　상처 관리에는 수분 균형이 필수다. 만성 상처를 공기에 노출해 말려서는 안 된다. 습윤한 상처는 더 빨리 낫고 감염 위험도 낮다. 건조하면 적절한 드레싱으로 수분을 더하고, 배액이 있으면 이를 조절하여 상처 주변 피부에 닿지 않도록 한다. 드레싱은 상처 바닥의 수분을 유지해 건조를 막아야 한다. 가장자리의 밑부분이 파인 상태가 없어야 하며 말린 가장자리는 절제하여 상피화를 가능하게 한다. 이어지는 정맥성 궤양 단락은 정맥 기능부전이나 폐색으로 인한 정맥 고혈압이 표재정맥을 확장한다고 설명하다 끊긴다.

**청크 323 · 실제 검색 2위**　Physiology, Wound Healing - StatPearls - NCBI Bookshelf.pdf · PDF 6쪽

> phase. Anti-inflammatory drugs, particularly during the first 3 days of healing; corticosteroids;
> immunosuppressants; and chemotherapy agents can alter wound healing.[6] Similarly, some
> comorbidities negatively influence wound healing, with diabetes mellitus being one of the most
> significant diseases associated with chronic wound formation. Poor perfusion, neuropathy,
> immunosuppression, slower collagen synthesis and accumulation, and inadequate angiogenesis
> often cause an increased risk of infection and delayed wound healing in patients with diabetes
> mellitus.
> Adequate perfusion and oxygenation of the wounded area are also critical for normal wound
> healing. Oxygen significantly affects successful wound healing due to its role in inflammation,
> bactericidal activity, angiogenesis, epithelization, and collagen deposition.[6] Smoking,
> peripheral arterial insufficiency, prolonged local pressure, and radiation exposure can cause

**한국어 해석**　특히 치유 초기 3일의 항염증제, 코르티코스테로이드, 면역억제제, 항암제는 치유에 영향을 줄 수 있다. 당뇨 등 동반 질환도 영향을 준다. 당뇨 환자에서는 불량한 관류, 신경병증, 면역억제, 느린 콜라겐 합성·축적과 불충분한 혈관 생성이 감염 위험 증가와 치유 지연에 관여한다. 정상 치유에는 적절한 관류와 산소 공급이 중요하고 산소는 염증, 살균, 혈관 생성, 상피화 및 콜라겐 침착에 관여한다. 흡연·말초동맥부전·지속적인 국소 압박·방사선 노출의 결과를 설명하는 문장은 중간에 끝난다.

**청크 425 · 실제 검색 3위**　Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf · PDF 18쪽

> fluid. Wound Rep Regen 2000; 8: 392–8. [PubMed: 11115151]
> Steed DL, Donohoe D, Webster MW, Lindsley L. Effect of extensive debridement and
> treatment on the healing of diabetic foot ulcers. J Am Coll Surg 1996; 183, 61–4. [PubMed:
> 8673309]
> Agren MS, Eaglstein WH, Ferguson MW, Harding KG, Moore K, Saarialho-Kere UK,
> Schultz GS. Causes and effects of the chronic inflammation in venous leg ulcers. Acta
> Derm Venereol Suppl (Stockh) 2000; 210: 3–17. [PubMed: 10884942]

**한국어 해석**　참고문헌 목록의 일부다. 첫 항목은 앞부분이 잘린 논문의 서지정보이고, 이어 Steed 등의 당뇨발 궤양에서 광범위한 변연절제와 치유에 관한 논문, Agren 등의 정맥성 다리 궤양에서 만성 염증의 원인과 영향에 관한 학술대회 문헌을 열거한다. 연구 결과 본문은 제시하지 않는다.

</details>

## 2. 드레싱을 바꾼 뒤에 진물이 전보다 많이 모였대요. 그럼 상처가 더 나빠진 건가요?

지정 청크 **2위** · ON 충실성 **1/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 487** | 487은 환자 14명에서 드레싱과 음압상처치료(NPWT)의 채취량이 달랐다고 보고한다. 개인의 악화를 판정하지 않는다. |
| 검색 1위 · **486** · 12쪽 | 흡수력이 높은 드레싱, 시료 회수 문제, 깊은 조직에서도 채취하는 장치를 설명한다. |
| 검색 2위 · **487** · 12쪽 | 드레싱 0.17~0.21과 NPWT 1.3 g/cm²/일. 채취법 차이가 연구 간 비교를 어렵게 한다. |
| 검색 3위 · **425** · 18쪽 | 참고문헌 목록으로 진물량 비교를 제시하지 않는다. |
| **공통 답변** | 수집된 양이 늘었다는 사실만으로 악화 여부를 결정하기 어렵다. |
| **OFF와 문헌 대조** | 드레싱 흡수력 차이를 제시한다. 붓기·진물 색 등 추가 증상 목록은 이 검색 결과의 주제가 아니다. |
| **ON과 검색 근거 대조** | 487의 방법별 수집량 차이를 근거로 개인에 대한 판단을 유보한다. |
| **누락·적용 범위** | ON의 ‘드레싱 종류에 따라 큰 차이’는 원문의 비교 대상보다 넓다. 정량 비교는 드레싱 대 NPWT였다. 실제 숫자를 생략해도 환자 질문에 대한 핵심 설명은 성립한다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

드레싱을 바꾼 후에 진물이 전보다 많아졌다고 해서 **무조건 상처가 더 나빠졌다고 볼 수는 없습니다.** 

진물(삼출물)은 상처가 아물어가는 자연스러운 치유 과정에서 나오는 것입니다. 드레싱의 종류에 따라 흡수력이 다르기 때문에, 이전보다 진물이 더 많이 모이는 것처럼 보일 수 있습니다. 

다만, 진물과 함께 다음과 같은 증상이 나타난다면 상처에 문제가 생겼을 가능성이 있으므로 의료기관을 방문하시는 것이 좋습니다.
* 상처 부위가 점점 더 붓거나 붉어질 때
* 통증이 심해질 때
* 진물에서 냄새가 나거나 색깔이 탁할 때 (노란색, 초록색 등)
* 열감이 느껴질 때

*※ 개인별 진단이나 처방은 할 수 없으므로, 정확한 상태를 확인하려면 의사나 간호사 등 의료 전문가의 진료를 받으시기 바랍니다.*

**RAG ON**

제공해주신 자료에는 드레싱 교체 후 진물이 늘어난 것이 상처가 나빠졌는지를 직접적으로 설명하는 내용은 포함되어 있지 않습니다. 

다만, 상처 치료와 진물(삼출물) 측정에 관한 연구들을 보면, 사용하는 드레싱의 종류나 측정 방법에 따라 수집되는 진물의 양에 큰 차이가 날 수 있다고 합니다 ([출처: nihms-2086081.pdf, PDF 12쪽]). 

*이 답변은 의료 전문가의 진단이나 처방이 아니므로, 상처 상태에 대한 정확한 판단은 의사나 간호사 등 의료진과 상담하시기 바랍니다.*

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 487 · 사전 기준 / 실제 검색 2위**　nihms-2086081.pdf · PDF 12쪽

> not solely represent surface conditions. The methods used for measuring wound exudate can 
> yield disparate results. A comparative study of 14 patients revealed significant differences in 
> exudate collection between methods: 0.17–0.21 g cm−2 day−1 with dressing and 1.3 g cm−2 
> day−1 with NPWT109. The inconsistencies in wound analysis methods and sample collection 
> pose a crucial challenge, hindering accurate characterization of the wound healing process 
> and impeding effective results comparison across studies. To address these challenges, 
> microfluidic-based sampling has been introduced for on-site intermittent storage and precise 
> management of wound exudate. This approach effectively reduces the likelihood of dilution, 
> mixing, or cross-contamination96, 110. However, one main challenge of such microfluidic 
> sampling is the limited volume of collected wound extrudate, typically 0.05–0.4 g/cm2 
> per day111. Despite numerous reports on microfluidics for wound sampling, none have

**한국어 해석**　측정법에 따라 삼출물 수집량이 달라질 수 있다. 환자 14명의 비교에서 드레싱은 하루 0.17~0.21 g/cm², NPWT는 1.3 g/cm²였다. 분석·채취 방법 차이는 치유 과정의 특성 파악과 연구 간 비교를 어렵게 한다. 현장에서 삼출물을 간헐적으로 저장·관리하는 미세유체 채취는 희석·혼합·교차오염 가능성을 줄인다. 하루 채취량이 대개 0.05~0.4 g/cm²로 제한되는 점은 과제다. 마지막 문장은 중간에 끝난다.

**청크 486 · 실제 검색 1위**　nihms-2086081.pdf · PDF 12쪽

> crucial for reliable wound assessment. Adopting continuous and effective in situ sampling 
> techniques, aimed at isolating fresh exudate through a singular extraction process, offers a 
> promising avenue. However, the practical implementation and success of such a strategy 
> remain areas for future demonstration and refinement.
> Dressings with enhanced exudate absorption capacity and a self-pumping feature were 
> developed for efficient exudate sampling31. However, there are challenges associated with 
> this approach, such as potential contamination from the biomaterials and difficulties in 
> extracting fluid from the dressing scaffolds without losing critical information. Alternatively, 
> NPWT and microneedles are capable of extracting fluid from deeper tissue layers, providing 
> a more comprehensive overview of the wound environment. However, this approach may 
> not solely represent surface conditions. The methods used for measuring wound exudate can

**한국어 해석**　신뢰할 만한 평가를 위해 한 번의 추출로 새 삼출물을 분리하는 연속 현장 채취가 유망하지만 실제 구현과 성공 여부는 추가 입증이 필요하다. 흡수력이 높고 자체 펌핑 기능이 있는 드레싱이 개발됐으나 재료에 의한 오염과 정보 손실 없이 액체를 회수하는 데 어려움이 있다. 음압상처치료(NPWT)와 미세바늘은 깊은 조직층의 액체도 얻어 넓은 환경을 반영하지만 표면 상태만 나타내지는 않을 수 있다. 측정 방법에 관한 마지막 문장은 다음 청크로 이어진다.

**청크 425 · 실제 검색 3위**　Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf · PDF 18쪽

> fluid. Wound Rep Regen 2000; 8: 392–8. [PubMed: 11115151]
> Steed DL, Donohoe D, Webster MW, Lindsley L. Effect of extensive debridement and
> treatment on the healing of diabetic foot ulcers. J Am Coll Surg 1996; 183, 61–4. [PubMed:
> 8673309]
> Agren MS, Eaglstein WH, Ferguson MW, Harding KG, Moore K, Saarialho-Kere UK,
> Schultz GS. Causes and effects of the chronic inflammation in venous leg ulcers. Acta
> Derm Venereol Suppl (Stockh) 2000; 210: 3–17. [PubMed: 10884942]

**한국어 해석**　참고문헌 목록의 일부다. 첫 항목은 앞부분이 잘린 논문의 서지정보이고, 이어 Steed 등의 당뇨발 궤양에서 광범위한 변연절제와 치유에 관한 논문, Agren 등의 정맥성 다리 궤양에서 만성 염증의 원인과 영향에 관한 학술대회 문헌을 열거한다. 연구 결과 본문은 제시하지 않는다.

</details>

## 3. 상처가 몇 주째 잘 안 낫는데, 열도 안 나고 빨갛지도 않아요. 그러면 감염 걱정은 안 해도 되나요?

지정 청크 **미적중** · ON 충실성 **2/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 275** | 275는 만성 감염 상처에서 홍반·부종·통증·발열이 항상 나타나지는 않는다고 명시한다. |
| 검색 1위 · **37** · 9쪽 | 예상보다 늦은 치유와 진행에 따라 뚜렷해지는 전형적 징후를 언급한다. |
| 검색 2위 · **203** · 48쪽 | 국소 감염은 미묘한 징후에서 전형적 징후로 발전할 수 있고 흔히 치유 지연을 동반한다. |
| 검색 3위 · **36** · 9쪽 | 예상보다 늦은 치유를 눈에 잘 띄지 않는 국소 감염 징후로 열거한다. |
| **공통 답변** | 둘 다 열·발적이 없더라도 감염 가능성을 배제하지 않는다. |
| **OFF와 문헌 대조** | 느린 세균 증식·혈액순환·기저질환 등으로 설명 범위를 넓힌다. 세 청크는 이 환자의 원인을 특정하지 않는다. |
| **ON과 검색 근거 대조** | 36·203의 ‘미묘한 징후’와 ‘예상보다 늦은 치유’를 연결하고 가능성으로 한정한다. |
| **누락·적용 범위** | 275는 누락됐으나 대체 근거가 충분하다. 검색된 세 문단이 발열과 발적을 각각 명시하는 것은 아니므로 이는 일반 설명을 질문의 조건에 적용한 추론이다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

열이 나거나 빨갛게 붓는 증상이 없더라도, **상처가 몇 주째 잘 낫지 않는다면 감염의 가능성을 완전히 안심할 수는 없습니다.** 

눈에 띄는 붉은기나 열감(급성 염증 반응)이 없더라도, 상처 부위에 세균이 천천히 증식하면서 치유를 방해하는 '만성 감염'이나 다른 원인(예: 혈액순환 문제, 기저질환 등)으로 인해 상처가 낫지 않을 수 있습니다. 

따라서 열이 나지 않는다고 해서 감염 걱정을 완전히 놓기보다는, 상처가 오래 지속되는 원인을 확인하기 위해 병원을 방문해 진료를 받아보시는 것이 좋습니다.

*(※ 개인별 진단이나 처방은 할 수 없으므로, 정확한 상태 확인은 의료기관을 이용해 주세요.)*

**RAG ON**

상처가 잘 낫지 않는다면 열이 나거나 빨개지는 등의 전형적인 증상이 없더라도 감염(국소 감염)의 가능성을 완전히 안심할 수는 없습니다. 

참고 자료에 따르면, 상처 감염은 눈에 잘 띄는 전형적인 증상 외에도 **눈에 잘 띄지 않는 미세한(subtle/covert) 증상**으로 나타날 수 있습니다. 그 대표적인 초기 증상 중 하나가 바로 **'예상보다 상처가 낫는 속도가 지연되는 것'**입니다. 즉, 겉으로 붉거나 열감이 없더라도 상처가 몇 주째 잘 낫지 않는 것 자체가 감염과 관련이 있을 수 있습니다.

(참고 자료: `8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf`, PDF 9쪽, 48쪽)

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 275 · 사전 기준 / 이 턴에서 검색되지 않음**　Chronic_Wounds_Evaluation_and_Management_AFP.pdf · PDF 8쪽

> 2026. 10. 31. য়റ 11:02Chronic Wounds: Evaluation and Management | AFP
> 8ಕ੉૑/19ಕ੉૑https://www.aafp.org/afp/2020/0201/p159?utm_source=
> Stage 3 sacral pressure ulcer.
> When assessing a chronic wound for infection, physicians should
> be aware that chronic infected wounds have di"erent signs and
> symptoms than acute infected wounds. Typical signs of infection
> such as erythema, edema, pain, and fever are not always present.
> Two mnemonics are used to identify chronic wounds with
> infectious processes:
> NERDS (for wounds with bioﬁlm or critical colonization):
> nonhealing, exudative, red and bleeds easily, debris, and smell.
> Sensitivity is 73% and speciﬁcity is 80.5% when three criteria
> are present.
> STONEES (for infection): size increasing, temperature increased,
> os (probes to or exposed bone), new areas of breakdown,
> exudative, erythema/edema, and smell. Sensitivity is 90% and
> speciﬁcity is 69.4% when three criteria are present.
> Biopsy with quantitative processing is the best method of wound

**한국어 해석**　3단계 천골 욕창 사진 설명 다음에, 만성 감염 상처는 급성 감염 상처와 양상이 다르고 홍반·부종·통증·발열이 항상 있지는 않다고 설명한다. NERDS는 낫지 않음, 삼출, 붉고 쉽게 출혈, 잔해, 냄새를 가리키며 세 기준 충족 시 민감도 73%, 특이도 80.5%라고 적었다. STONEES는 크기·온도 증가, 뼈 탐지/노출, 새 조직 붕괴, 삼출, 홍반/부종, 냄새를 포함하며 세 기준에서 각각 90%, 69.4%다. 정량 생검 설명은 문장이 잘렸다.

**청크 37 · 실제 검색 1위**　8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf · PDF 9쪽

> ■ Delayed wound healing beyond expectations.
> As local wound infection progresses, classic cardinal (overt) signs and symptoms that are 
> traditionally associated with local infections generally become evident and are more recognisable 
> Figure 1 | IWII Wound Infection 
> Continuum (IWII-WIC)

**한국어 해석**　예상보다 지연되는 상처 치유가 목록에 제시된다. 국소 감염이 진행되면 전형적이고 겉으로 보이는 주요 징후와 증상이 대체로 더 뚜렷하고 알아보기 쉬워진다. 뒤에는 국제상처감염연구소(IWII)의 상처 감염 연속체 그림 제목이 있다.

**청크 203 · 실제 검색 2위**　8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf · PDF 48쪽

> inactive.
> Infection: When the quantity of microorganisms in a wound 
> become imbalanced such that the host response is overwhelmed 
> and wound healing becomes impaired.44 T ransition from  
> non-infected to infected is a gradual process determined by the 
> quantity and virulence of microbial burden and the individual’s 
> immune response.12 
> Local infection: Local infection refers to the presence and 
> proliferation of microorganisms within the wound that evoke a 
> response from the host that often includes delayed wound healing. 
> Local infection is contained within the wound and the immediate 
> periwound region (less than 2cm). Local infection often presents as 
> subtle (covert) signs that may develop into the classic (overt) signs 
> of infection.20 
> Lymphangitis: Inflammation of lymph vessels, seen as streaking, 
> linear erythema running proximally from a site of infection toward 
> lymph nodes. Presentation reflects inflammation of the underlying

**한국어 해석**　감염은 미생물의 균형이 깨져 숙주 반응이 압도되고 상처 치유가 손상된 상태다. 감염으로의 이행은 점진적이며 미생물의 양·독성과 개인의 면역 반응에 좌우된다. 국소 감염은 미생물 증식이 숙주 반응을 유발하고 흔히 치유 지연을 동반하며 상처와 바로 주변(2cm 미만)에 국한된다. 미묘한 징후에서 전형적 징후로 발전할 수 있다. 이어 림프관염을 감염 부위에서 림프절 쪽으로 선형 홍반이 뻗는 림프관 염증으로 정의하다 문장이 끊긴다.

**청크 36 · 실제 검색 3위**　8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf · PDF 9쪽

> Microorganisms that colonise a wound may also arise from exogenous sources or as a result of 
> environmental exposure.
> Local infection is used to refer to a stage of infection in which there is presence and proliferation 
> of microorganisms within the wound that evoke a response from the host, often including a delay 
> in wound healing. Local infection is contained within the wound and the immediate periwound 
> region (less than 2cm). Local infection often presents as covert (subtle) signs and symptoms12, 19 
> that may not be immediately recognised as a sign of infection. 
> Covert (subtle) signs and symptoms of wound infection include:62, 67-70 
> ■ Hypergranulation
> ■ Bleeding, friable granulation
> ■ Epithelial bridging and pocketing in granulation tissue
> ■ Increasing exudate
> ■ Delayed wound healing beyond expectations.
> As local wound infection progresses, classic cardinal (overt) signs and symptoms that are

**한국어 해석**　정착 미생물은 외부 환경에서도 올 수 있다. 국소 감염은 상처 내 미생물의 존재·증식에 숙주가 반응하는 단계로, 흔히 치유가 지연되며 상처와 2cm 미만의 인접 부위에 국한된다. 바로 감염으로 알아보기 어려운 징후에는 과도한 육아조직, 쉽게 피가 나는 취약한 육아조직, 상피 가교와 육아조직 내 주머니 형성, 삼출물 증가, 예상보다 지연되는 치유가 있다. 다음 문장은 감염 진행 시 전형적 징후를 설명하다 끊긴다.

</details>

## 4. 상처에서 나던 냄새가 더 심해졌고 전보다 아파요. 병원에 이 두 가지도 얘기해야 하나요?

지정 청크 **1위** · ON 충실성 **2/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 38** | 38은 새로 생기거나 심해진 통증과 증가한 악취를 국소 감염에서 나타날 수 있는 징후로 함께 열거한다. |
| 검색 1위 · **38** · 10쪽 | 증가한 통증과 악취 두 가지를 직접 명시한다. |
| 검색 2위 · **275** · 8쪽 | 만성 상처 평가 목록에 냄새가 있고, 통증 등 전형적 징후는 항상 나타나지는 않는다고 한다. |
| 검색 3위 · **37** · 9쪽 | 감염 진행 시 전형적 징후가 더 뚜렷해진다는 배경이다. |
| **공통 답변** | 두 증상이 이전보다 심해졌다고 의료진에게 알리라는 답이다. |
| **OFF와 문헌 대조** | 변화의 크기와 시작 시점을 전달하라고 구체화한다. 38과 방향이 맞는다. |
| **ON과 검색 근거 대조** | 두 증상의 영어 표현을 38과 연결하고 만성 상처에 대한 배경을 275에서 보충한다. |
| **누락·적용 범위** | 사전 기준의 두 증상은 양쪽 모두 반영했다. 275만으로는 두 증상의 ‘증가’를 함께 뒷받침하기 어려우나 ON의 첫 인용인 38이 이를 직접 지지한다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

네, **당연히 병원에 꼭 말씀하셔야 합니다.**

상처에서 나던 냄새가 심해지고 통증이 더 심해진 것은 상처에 문제가 생겼음을 알려주는 중요한 신호입니다. 

의료진에게 다음과 같은 내용을 구체적으로 이야기해 주세요.
* 상처 냄새가 예전보다 얼마나 더 심해졌는지
* 통증이 언제부터, 얼마나 더 아파졌는지

개인별 진단이나 처방은 해드릴 수 없으므로, 증상을 정확하게 말씀하시고 의사의 진료를 받으시기 바랍니다.

**RAG ON**

네, 병원에 가셔서 **이 두 가지(냄새가 심해진 것, 통증이 전보다 심해진 것)를 꼭 말씀하셔야 합니다.**

참고 자료에 따르면, 상처 감염이 있을 때 나타나는 대표적인 증상 중에는 **'새로 생기거나 심해지는 통증(New or increasing pain)'**과 **'심해지는 냄새(Increasing malodour)'**가 포함되어 있습니다 ([8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf, PDF 10쪽]). 

또한 만성 상처에서 감염을 확인할 때도 냄새(smell)와 통증(pain) 등은 의료진이 중요하게 살피는 신호입니다 ([Chronic_Wounds_Evaluation_and_Management_AFP.pdf, PDF 8쪽]). 

따라서 의사에게 이 증상들을 자세히 설명하는 것이 정확한 진단과 치료에 큰 도움이 됩니다.

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 38 · 사전 기준 / 실제 검색 1위**　8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf · PDF 10쪽

> 10 INTERNATIONAL CONSENSUS UPDATE 2022 | WOUND INFECTION IN CLINICAL PRACTICE
> as an indicator of wound infection. However, these symptoms may be masked in people with 
> compromised immune systems and/ or poor vascular perfusion.
> Overt (classic) signs and symptoms of wound infection may include:62, 67-69, 71
> ■ Erythema (which may present differently depending on the individual’s skin tone)
> ■ Local warmth
> ■ Swelling
> ■ Purulent discharge
> ■ Wound breakdown and enlargement
> ■ New or increasing pain
> ■ Increasing malodour.
> Spreading infection (also referred to as cellulitis) describes the stage of infection in which there is invasion 
> of the surrounding tissue by infective microorganisms that have spread from a wound. Microorganisms 
> proliferate and spread to a degree that signs and symptoms extend beyond the wound border.9, 72 
> Spreading infection may involve deep tissue, muscle, fascia, organs or body cavities. 
> Spreading infection signs and symptoms may include:62, 67
> ■ Extending induration

**한국어 해석**　면역 기능이나 혈류가 저하된 사람에서는 증상이 가려질 수 있다. 외현적 국소 감염 징후에는 피부색에 따라 다르게 보이는 홍반, 국소 열감, 부종, 화농성 분비물, 상처 붕괴·확대, 새로 생기거나 심해지는 통증과 악취 증가가 있을 수 있다. 확산성 감염에서는 미생물이 주변 조직을 침범하여 증상이 경계를 넘어가며 깊은 조직·근육·근막·장기·체강까지 침범할 수 있다. 마지막 목록은 경결 확대에서 끊긴다.

**청크 275 · 실제 검색 2위**　Chronic_Wounds_Evaluation_and_Management_AFP.pdf · PDF 8쪽

> 2026. 10. 31. য়റ 11:02Chronic Wounds: Evaluation and Management | AFP
> 8ಕ੉૑/19ಕ੉૑https://www.aafp.org/afp/2020/0201/p159?utm_source=
> Stage 3 sacral pressure ulcer.
> When assessing a chronic wound for infection, physicians should
> be aware that chronic infected wounds have di"erent signs and
> symptoms than acute infected wounds. Typical signs of infection
> such as erythema, edema, pain, and fever are not always present.
> Two mnemonics are used to identify chronic wounds with
> infectious processes:
> NERDS (for wounds with bioﬁlm or critical colonization):
> nonhealing, exudative, red and bleeds easily, debris, and smell.
> Sensitivity is 73% and speciﬁcity is 80.5% when three criteria
> are present.
> STONEES (for infection): size increasing, temperature increased,
> os (probes to or exposed bone), new areas of breakdown,
> exudative, erythema/edema, and smell. Sensitivity is 90% and
> speciﬁcity is 69.4% when three criteria are present.
> Biopsy with quantitative processing is the best method of wound

**한국어 해석**　3단계 천골 욕창 사진 설명 다음에, 만성 감염 상처는 급성 감염 상처와 양상이 다르고 홍반·부종·통증·발열이 항상 있지는 않다고 설명한다. NERDS는 낫지 않음, 삼출, 붉고 쉽게 출혈, 잔해, 냄새를 가리키며 세 기준 충족 시 민감도 73%, 특이도 80.5%라고 적었다. STONEES는 크기·온도 증가, 뼈 탐지/노출, 새 조직 붕괴, 삼출, 홍반/부종, 냄새를 포함하며 세 기준에서 각각 90%, 69.4%다. 정량 생검 설명은 문장이 잘렸다.

**청크 37 · 실제 검색 3위**　8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf · PDF 9쪽

> ■ Delayed wound healing beyond expectations.
> As local wound infection progresses, classic cardinal (overt) signs and symptoms that are 
> traditionally associated with local infections generally become evident and are more recognisable 
> Figure 1 | IWII Wound Infection 
> Continuum (IWII-WIC)

**한국어 해석**　예상보다 지연되는 상처 치유가 목록에 제시된다. 국소 감염이 진행되면 전형적이고 겉으로 보이는 주요 징후와 증상이 대체로 더 뚜렷하고 알아보기 쉬워진다. 뒤에는 국제상처감염연구소(IWII)의 상처 감염 연속체 그림 제목이 있다.

</details>

## 5. 상처가 아문 지 석 달쯤 됐는데, 그 자리 피부도 이제 예전만큼 튼튼해졌나요?

지정 청크 **2위** · ON 충실성 **1/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 319** | 319는 3개월 이후 원조직 강도의 약 80%라고 설명한다. 개인 측정값이나 상처가 닫힌 날을 기준으로 한 수치는 없다. |
| 검색 1위 · **371** · 7쪽 | 수개월 이상 콜라겐 재배열로 인장강도가 정상의 최대 약 80%에 이른다. |
| 검색 2위 · **319** · 5쪽 | 3개월 이후 약 80%, 정상 피부의 강도를 완전히 따라잡지 못한다. |
| 검색 3위 · **370** · 7쪽 | 새로 상피화된 상처는 약 25%이며 이후 콜라겐 재배열로 강도가 높아진다. |
| **공통 답변** | 회복 과정이 길며 원래 피부 강도와 차이가 난다는 방향은 같다. |
| **OFF와 문헌 대조** | 70~80%·수개월~1년 이상·자외선 주의를 덧붙인다. ‘예전만큼 튼튼해지려면’이라는 표현은 원문의 회복 상한과 긴장 관계에 있다. |
| **ON과 검색 근거 대조** | 319·371의 약 80%와 최대치라는 의미를 살리고 두 페이지를 제시한다. |
| **누락·적용 범위** | 기준의 ‘개인치 단정 보류’가 ON에서 빠졌다. ‘아문 지 석 달’과 문헌의 ‘3개월 이후’는 기산점이 같다고 확인되지 않는다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

상처가 아문 지 3개월이 지났다면 겉보기에는 다 나은 것 같아 보이지만, **피부의 모든 기능이 예전 상태로 완전히 튼튼해졌다고 보기는 어렵습니다.**

피부가 다치고 회복되는 과정은 크게 몇 단계를 거칩니다. 상처가 아문 후에도 피부 안쪽에서는 콜라겐이 리모델링(재조정)되는 과정이 아주 오랜 시간 동안 일어납니다. 

* **강도의 차이:** 상처 부위의 피부는 완전히 아문 것처럼 보여도, **원래 건강했던 피부 강도의 약 70~80% 정도**만 회복된 상태인 경우가 많습니다.
* **시간의 필요성:** 피부가 외부 자극에 완전히 적응하고 예전만큼 튼튼해지려면 보통 **수개월에서 1년 이상**의 시간이 필요합니다.

따라서 3개월이 지났더라도 상처 부위는 여전히 자극에 예민할 수 있으므로, 강한 마찰이나 자외선 등에 주의하는 것이 좋습니다.

*(※ 만약 개인적인 피부 상태나 통증 등으로 걱정되신다면 의사나 전문가와 상담해 보시는 것을 권장합니다.)*

**RAG ON**

아니요, 상처가 아문 지 석 달이 지났더라도 그 부위의 피부가 예전만큼 완전히 튼튼해진 것은 아닙니다. 

참고 자료에 따르면, 상처 부위의 장력(피부가 당기는 힘을 견디는 강도)은 원래 피부의 최대 약 80% 수준까지만 회복되며, 다치기 전의 원래 피부 강도와는 같아질 수 없습니다. ([출처: Physiology, Wound Healing - StatPearls - NCBI Bookshelf.pdf, PDF 5쪽], [출처: Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf, PDF 7쪽])

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 319 · 사전 기준 / 실제 검색 2위**　Physiology, Wound Healing - StatPearls - NCBI Bookshelf.pdf · PDF 5쪽

> For instance, the wound strength can never catch up with the normal skin strength. At 3 months
> and beyond, the wound strength reaches only about 80% of that of the original tissue.[10]
> Similarly, subepidermal appendages such as hair follicles or sweat glands do not heal after a
> severe injury. Scar tissue also lacks rete pegs, which allow for a tight connection between the
> epidermis and dermis.[2]
> Clinical Significance
> Disruption during any wound-healing phase can lead to excessive wound healing or chronic
> wound formation.[4][15]
> Excessive Wound Healing
> The pathogenesis of excessive wound healing is not fully understood. This condition is an
> abnormal form of wound healing characterized by continuous localized inflammation, excessive
> collagen synthesis, abnormal collagen turnover, and exaggerated extracellular matrix
> accumulation. Examples of excessive wound healing include keloid and hypertrophic scars.[15]
> Chronic Wound Formation

**한국어 해석**　상처 조직의 강도는 정상 피부를 완전히 따라잡지 못하며 3개월 이후 원래 조직의 약 80%에 이른다. 심한 손상 뒤 모낭·땀샘 같은 부속기는 회복되지 않으며 반흔에는 표피와 진피의 결합을 돕는 표피능선이 없다. 치유 단계가 교란되면 과도한 치유나 만성 상처가 생길 수 있다. 과도한 치유는 기전이 완전히 밝혀지지 않았고 국소 염증 지속, 콜라겐 과다 합성·비정상 대사, 세포외기질 과다 축적이 특징이며 켈로이드와 비후성 반흔이 예로 든다. 마지막에는 만성 상처 형성 소제목이 있다.

**청크 371 · 실제 검색 1위**　Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf · PDF 7쪽

> Over several months or more, changes in collagen organization in the repaired tissue will slowly
> increase the tensile strength to a maximum of about 80% of normal tissue.
> 17

**한국어 해석**　수개월 이상에 걸쳐 회복 조직에서 콜라겐 배열이 바뀌면서 인장강도가 서서히 증가해 정상 조직의 최대 약 80%에 이른다.

**청크 370 · 실제 검색 3위**　Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf · PDF 7쪽

> glycosaminoglycans (GAGs) and proteoglycans. Cell density and metabolic activity in the
> granulation tissue decrease during maturation. Changes also occur in the type, amount, and
> organization of collagen, which enhance tensile strength. Initially, type III collagen was
> synthesized at high levels, but it becomes replaced by type I collagen, the dominant fibrillar
> collagen in skin. The tensile strength of a newly epithelialized wound is only about 25% of
> normal tissue. Healed or repaired tissue is never as strong as normal tissues that have never been
> wounded. Tissue tensile strength is enhanced primarily by the reorganization of collagen fibers
> that were deposited randomly during granulation and increased covalent cross-linking of
> collagen molecules by the enzyme, lysyl oxidase, which is secreted into the ECM by fibroblasts.
> Over several months or more, changes in collagen organization in the repaired tissue will slowly

**한국어 해석**　성숙하면서 육아조직의 세포 밀도와 대사활성이 줄고 콜라겐의 유형·양·배열이 바뀌어 인장강도가 높아진다. 초기의 III형은 피부의 주요 섬유성 콜라겐인 I형으로 대체된다. 갓 상피화된 상처의 강도는 정상 조직의 약 25%이고 회복 조직은 손상된 적 없는 조직만큼 강해지지는 않는다. 육아기 무작위 배열 섬유의 재조직화와 섬유아세포가 세포외기질에 분비한 리실 산화효소에 의한 공유결합 가교가 강도를 높인다. 수개월 동안의 변화는 다음 청크로 이어진다.

</details>

## 6. 스마트 드레싱에 pH 수치가 뜨던데, 그 숫자 하나만 보고 제가 감염됐는지 알 수 있나요?

지정 청크 **미적중** · ON 충실성 **0/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 481** | 481은 pH 등 여러 생체지표를 나열하고 이들 지표가 감염·염증 등의 상태와 관련된다고 설명한다. pH 단독 진단 성능까지 제시하지 않는다. |
| 검색 1위 · **206** · 48쪽 | pH의 산성·알칼리성 정의와 주변 피부의 홍반·열감·부종을 각각 설명한다. |
| 검색 2위 · **491** · 13쪽 | 온도·피부 임피던스를 감염 등의 지표로 언급하고, 별도로 pH의 전위차 측정 원리를 설명한다. |
| 검색 3위 · **558** · 27쪽 | pH 센서 등의 참고문헌 목록이다. |
| **공통 답변** | 두 답변 모두 pH 하나로 감염을 확정할 수 없다고 답한다. |
| **OFF와 문헌 대조** | 주변 피부의 붉어짐·붓기는 206과 겹친다. 통증·진물 색·냄새와 단독 진단 능력은 이 세 문단에서 확인되지 않는다. |
| **ON과 검색 근거 대조** | pH 정의는 206과 맞다. 그러나 491의 온도·피부 임피던스에 관한 ‘중요한 지표’를 pH까지 확장했다. |
| **누락·적용 범위** | 지정 481을 놓쳤고 대체 문단도 질문의 핵심인 단독 진단 능력까지 다루지 않는다. 신중한 결론과 별개로 ON이 내세운 근거 연결은 지지되지 않는다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

스마트 드레싱에 나타나는 pH 숫자 **하나만으로는 감염 여부를 확실하게 알 수 없습니다.** 

pH 수치는 상처의 상태를 알려주는 중요한 참고 지표 중 하나이지만, 감염을 진단하기 위해서는 상처 주변의 붉어짐, 붓기, 통증, 분비물의 냄새나 색깔 등 **다른 임상 증상들과 함께 종합적으로 판단**해야 합니다. 

따라서 pH 수치에만 의존하지 마시고, 상처 부위에 이상이 느껴지거나 걱정되는 부분이 있다면 의료전문가의 진료를 받는 것이 안전합니다.

**RAG ON**

아니요, 스마트 드레싱에 나타나는 pH 수치 **하나만 보고 감염 여부를 확실하게 알 수는 없습니다.** 

제공된 자료에 따르면 pH 수치는 산성과 알칼리성의 정도를 나타내는 지표이며, 온도, 피부 임피던스(저항) 등과 함께 감염, 수분 상태, 염증을 파악하는 데 도움을 주는 **중요한 지표(crucial indicators)** 중 하나입니다 ([출처: nihms-2086081.pdf, PDF 13쪽]). 하지만 감염 진단은 pH 단일 수치에만 의존하는 것이 아니라 여러 요소와 임상적 상황을 종합하여 판단해야 합니다.

*개인별 진단이나 처방은 하지 않으므로, 정확한 상태를 확인하려면 의료 전문가와 상담하시기 바랍니다.*

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 481 · 사전 기준 / 이 턴에서 검색되지 않음**　nihms-2086081.pdf · PDF 11쪽

> and multiplexed biomarkers through signal transduction techniques and system integration, 
> providing a comprehensive platform for the development and application of smart wound 
> management (Fig. 4).
> Biomarkers for wound healing
> Emerging biosensors and imaging devices have shown promising capabilities to characterize 
> wound features and monitor versatile biomolecules including metabolites (such as glucose, 
> uric acid, and lactate), electrolytes (such as pH, Na+, Ca2+, and NH4+), nutrients (such 
> as vitamins, amino acids, and fatty acids), proteins (such as cytokines and C-reactive 
> protein), and therapeutic drugs (such as growth factors, plasmids, and antibiotics)85, 94–100. 
> These biomarkers are associated with physiological and pathological conditions, such as 
> infection and inflammation101–103. Notably, analytes of interest can be detected directly at 
> the wound site, eliminating the need for blood tests or invasive tissue biopsies. Blood tests

**한국어 해석**　다중 생체지표와 신호 변환·시스템 통합에 이어 상처 치유용 생체지표를 설명한다. 바이오센서와 영상 장치는 상처 특징, 포도당·요산·젖산 등 대사산물, pH와 여러 이온, 비타민·아미노산·지방산, 사이토카인·C반응성 단백질, 성장인자·플라스미드·항생제 등을 관찰할 가능성을 보여 왔다. 이들 지표는 감염·염증 등 생리적·병리적 상태와 관련된다. 상처 현장에서 직접 검출하면 채혈이나 침습적 생검을 피할 수 있다는 설명 뒤 문장이 잘린다.

**청크 206 · 실제 검색 1위**　8-wound-infection-in-clinical-practice-principles-of-best-practices-2022.pdf · PDF 48쪽

> edge extending out 4cm and including any skin and tissue under 
> the wound dressing.394 The periwound region can be affected 
> by moisture (e.g. maceration and excoriation) or may be dry, or 
> develop hyperkeratosis, callus or eczema.394 The periwound region 
> can be indicative of the wound infection (e.g. erythema, warmth 
> and swelling indicates potential wound infection).394 
> pH: A measure on a scale from 0–14 of acidity or alkalinity, with 7 
> being neutral, greater than 7 being more alkaline and less than 7 
> being more acidic. The skin has a natural pH of around 5.5.
> Phagocytosis: A cellular process by which certain living cells ingest 
> and destroy other large cells or particles. Phagocytosis is a critical 
> first line component of the host’s defence, with phagocytes (e.g. 
> neutrophils and macrophages) detecting and binding to the cell 
> surface of invading microorganisms in order to eradicate them. 
> The process of phagocytosis also initiates other host immune

**한국어 해석**　상처 주변 부위에는 드레싱 아래 피부·조직이 포함되며 수분으로 인한 침윤·짓무름, 건조, 과각화, 굳은살, 습진이 나타날 수 있다. 홍반·열감·부종은 감염 가능성을 시사할 수 있다. pH는 0~14 범위의 산성·알칼리성 척도로 7은 중성이고 피부의 자연 pH는 약 5.5라고 정의한다. 이어 식세포가 미생물에 결합해 포식·제거하는 방어 과정을 설명하다 끊긴다.

**청크 491 · 실제 검색 2위**　nihms-2086081.pdf · PDF 13쪽

> as temperature and skin impedance, providing crucial indicators of infection, hydration, 
> and inflammation. Conversely, electrochemical sensors leverage techniques including 
> amperometry, potentiometry, and voltammetry, to precisely quantify alterations in electrical 
> signals at the sensor interface, facilitating detailed analysis of chemical and biological 
> processes. For ions (such as Na+, Ca2+, and NH4+) and pH monitoring, potentiometry is 
> primarily employed, utilizing ion-selective electrodes (ISEs) modified with ionophores (such 
> as valinomycin) that selectively and reversibly bind to ions or ion-sensitive materials (such 
> as polyaniline for pH sensing)113, 114. The measured voltage difference between the ISE 
> and the reference electrode shows a log-linear relationship with the analyte concentration. 
> The detection of metabolites such as glucose, uric acid, and lactate can be achieved 
> using amperometric enzymatic electrodes immobilized with a specific enzyme (such as

**한국어 해석**　문두에서 온도와 피부 임피던스 등이 감염·수분·염증을 파악하는 지표라고 설명한다. 이어 전기화학 센서의 전류·전위·전압 측정법을 소개한다. 나트륨·칼슘·암모늄 이온과 pH는 이온선택성 전극을 쓰는 전위차법으로 주로 감시한다. 이오노포어나 pH 감지용 폴리아닐린 등을 사용하며 기준전극과의 전압차는 분석물 농도와 로그선형 관계다. 포도당·요산·젖산 등은 전류 측정형 효소 전극으로 검출할 수 있다는 설명에서 끝난다.

**청크 558 · 실제 검색 3위**　nihms-2086081.pdf · PDF 27쪽

> 112. Iizaka S et al. Quantitative estimation of exudate volume for full-thickness pressure ulcers: the 
> ESTimation method. J Wound Care 20, 453–454, 458–463 (2011). [PubMed: 22067883] 
> 113. Gao W et al. Fully integrated wearable sensor arrays for multiplexed in situ perspiration analysis. 
> Nature 529, 509–514 (2016). [PubMed: 26819044] 
> 114. Nyein HYY et al. A Wearable Electrochemical Platform for Noninvasive Simultaneous 
> Monitoring of Ca2+ and pH. ACS Nano 10, 7216–7224 (2016). [PubMed: 27380446] 
> 115. Arroyo-Currás N et al. Real-time measurement of small molecules directly in awake, ambulatory 
> animals. Proceedings of the National Academy of Sciences 114, 645 (2017).
> 116. Garland NT et al. A Miniaturized, Battery-Free, Wireless Wound Monitor That Predicts Wound 
> Closure Rate Early. Advanced Healthcare Materials 12, 2301280 (2023).
> 117. Hussain G & Silvester DS Comparison of V oltammetric Techniques for Ammonia Sensing in 
> Ionic Liquids. Electroanalysis 30, 75–83 (2018).

**한국어 해석**　참고문헌 112~117이다. 차례로 욕창 삼출량 추정, 착용형 땀 분석 센서, 칼슘·pH 동시 비침습 측정 센서, 생체 내 소분자 실시간 측정, 상처 폐쇄를 예측하는 무선 모니터, 이온액체에서 암모니아 감지법 비교 논문이다. pH 단독값의 감염 진단 성능을 보고하는 본문은 없다.

</details>

## 7. 스마트 드레싱이 진물을 조금씩 나눠 받아 보관한다고 들었어요. 이렇게 모으면 어떤 점이 좋고, 검사할 때 어떤 한계가 있나요?

지정 청크 **2위** · ON 충실성 **2/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 487** | 487은 미세유체 분할 수집이 희석·혼합·교차오염을 줄이고 하루 채취량이 보통 0.05~0.4 g/cm²라고 설명한다. |
| 검색 1위 · **486** · 12쪽 | 흡수형 드레싱의 오염과 회수, 깊은 조직 채취의 한계를 설명한다. |
| 검색 2위 · **487** · 12쪽 | 미세유체 방식의 세 가지 장점과 작은 채취량을 함께 명시한다. |
| 검색 3위 · **485** · 12쪽 | 오래된 시료와 새 삼출물을 분리하고 신속히 분석해야 한다고 설명한다. |
| **공통 답변** | 검사에 쓸 시료가 적다는 한계는 양쪽 모두 설명한다. |
| **OFF와 문헌 대조** | 시간대별 추적에 초점을 두어 기준의 희석·혼합·교차오염 감소를 빠뜨린다. 받지 않은 첨부 PDF 1쪽을 인용한다. |
| **ON과 검색 근거 대조** | 487의 세 장점과 하루 채취량을 방식·수치·단위까지 보존해 인용한다. |
| **누락·적용 범위** | ON은 질문이 요구한 장점과 한계를 모두 반영했다. 같은 487 앞부분의 NPWT 채취량을 미세유체 수치에 섞지 않았다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

참고 자료에 따르면, 스마트 드레싱이 진물을 조금씩 나누어 보관하는 방식과 관련된 장점과 한계는 다음과 같습니다.

**1. 진물을 나누어 모았을 때의 좋은 점 (장점)**
* **시간대별 상태 변화 확인 가능:** 진물을 시간대별로 나누어 보관(구획화)하면, 상처가 치유되는 과정에서 시간 흐름에 따른 생체 지표의 변화를 추적할 수 있습니다. (출처: 첨부파일 '스마트 드레싱...' PDF 1페이지)

**2. 검사할 때의 한계점**
* **시료의 양 부족:** 상처에서 나오는 진물의 양이 원래 적기 때문에, 이를 여러 시간대별로 쪼개어 담으면 각 구획에 들어가는 시료의 양이 매우 적어집니다. 
* **분석의 어려움:** 양이 너무 적으면 나중에 감염 여부 등을 정확하게 검사(분석)하기 어려울 수 있습니다. (출처: 첨부파일 '스마트 드레싱...' PDF 1페이지)

※ 본 답변은 일반적인 정보 제공을 위한 것이며, 개인별 진단이나 처방을 대신할 수 없습니다.

**RAG ON**

질문하신 내용에 대해 참고 자료를 바탕으로 쉬운 한국어로 답변드립니다.

미세유체학(microfluidic) 기반의 스마트 드레싱 기술을 사용해 진물을 조금씩 나누어(간헐적으로) 보관하고 관리하면 다음과 같은 좋은 점과 한계가 있습니다.

**1. 좋은 점 (장점)**
* 진물이 희석되거나 섞이는 것, 또는 교차 오염될 가능성을 효과적으로 줄여줍니다 ([출처: nihms-2086081.pdf, PDF 12쪽]).

**2. 검사할 때의 한계**
* 모을 수 있는 진물의 양이 하루에 0.05~0.4 g/cm² 정도로 매우 적다는 한계가 있습니다 ([출처: nihms-2086081.pdf, PDF 12쪽]).

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 487 · 사전 기준 / 실제 검색 2위**　nihms-2086081.pdf · PDF 12쪽

> not solely represent surface conditions. The methods used for measuring wound exudate can 
> yield disparate results. A comparative study of 14 patients revealed significant differences in 
> exudate collection between methods: 0.17–0.21 g cm−2 day−1 with dressing and 1.3 g cm−2 
> day−1 with NPWT109. The inconsistencies in wound analysis methods and sample collection 
> pose a crucial challenge, hindering accurate characterization of the wound healing process 
> and impeding effective results comparison across studies. To address these challenges, 
> microfluidic-based sampling has been introduced for on-site intermittent storage and precise 
> management of wound exudate. This approach effectively reduces the likelihood of dilution, 
> mixing, or cross-contamination96, 110. However, one main challenge of such microfluidic 
> sampling is the limited volume of collected wound extrudate, typically 0.05–0.4 g/cm2 
> per day111. Despite numerous reports on microfluidics for wound sampling, none have

**한국어 해석**　측정법에 따라 삼출물 수집량이 달라질 수 있다. 환자 14명의 비교에서 드레싱은 하루 0.17~0.21 g/cm², NPWT는 1.3 g/cm²였다. 분석·채취 방법 차이는 치유 과정의 특성 파악과 연구 간 비교를 어렵게 한다. 현장에서 삼출물을 간헐적으로 저장·관리하는 미세유체 채취는 희석·혼합·교차오염 가능성을 줄인다. 하루 채취량이 대개 0.05~0.4 g/cm²로 제한되는 점은 과제다. 마지막 문장은 중간에 끝난다.

**청크 486 · 실제 검색 1위**　nihms-2086081.pdf · PDF 12쪽

> crucial for reliable wound assessment. Adopting continuous and effective in situ sampling 
> techniques, aimed at isolating fresh exudate through a singular extraction process, offers a 
> promising avenue. However, the practical implementation and success of such a strategy 
> remain areas for future demonstration and refinement.
> Dressings with enhanced exudate absorption capacity and a self-pumping feature were 
> developed for efficient exudate sampling31. However, there are challenges associated with 
> this approach, such as potential contamination from the biomaterials and difficulties in 
> extracting fluid from the dressing scaffolds without losing critical information. Alternatively, 
> NPWT and microneedles are capable of extracting fluid from deeper tissue layers, providing 
> a more comprehensive overview of the wound environment. However, this approach may 
> not solely represent surface conditions. The methods used for measuring wound exudate can

**한국어 해석**　신뢰할 만한 평가를 위해 한 번의 추출로 새 삼출물을 분리하는 연속 현장 채취가 유망하지만 실제 구현과 성공 여부는 추가 입증이 필요하다. 흡수력이 높고 자체 펌핑 기능이 있는 드레싱이 개발됐으나 재료에 의한 오염과 정보 손실 없이 액체를 회수하는 데 어려움이 있다. 음압상처치료(NPWT)와 미세바늘은 깊은 조직층의 액체도 얻어 넓은 환경을 반영하지만 표면 상태만 나타내지는 않을 수 있다. 측정 방법에 관한 마지막 문장은 다음 청크로 이어진다.

**청크 485 · 실제 검색 3위**　nihms-2086081.pdf · PDF 12쪽

> only contribute to our understanding of the wound environment, classifications, and healing 
> process but could also assist in drug screening and prognosis prediction107, 108.
> Wound sampling
> Efficient and precise sampling of wound exudate is crucial in wound care research and 
> management, given that wound exudate is a valuable source of biomarkers. Ensuring the 
> precision and relevance of data derived from biomarkers necessitates the careful collection 
> of samples where fresh and old wound exudate must be separated. Old exudate, potentially 
> laden with degraded substances, may not accurately convey the wound’s current condition, 
> contrarily to fresh exudate, which provides immediate insights into the wound’s state. The 
> ability to efficiently collect and promptly transfer fresh exudate to analysis modules is 
> crucial for reliable wound assessment. Adopting continuous and effective in situ sampling

**한국어 해석**　앞 연구가 상처 환경·분류·치유 과정 이해와 약물 선별·예후 예측에 기여할 수 있다는 문장 뒤에 삼출물 채취 절이 이어진다. 바이오마커 정보를 정확히 얻으려면 오래된 삼출물과 새 삼출물을 분리해야 한다. 오래된 시료의 분해 물질은 현 상태를 정확히 나타내지 못할 수 있으며, 새 시료를 신속히 채취·이송하는 것이 중요하다. 연속 현장 채취를 소개하다 끝난다.

</details>

## 8. 상처 위의 센서에 얇은 코팅을 입히면, 측정하려는 물질이 센서에 닿는 속도도 달라지나요?

지정 청크 **2위** · ON 충실성 **2/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 503** | 503은 투과성을 조정하는 하이드로겔 등 코팅이 분석물의 센서 도달 속도를 조절한다고 설명한다. |
| 검색 1위 · **502** · 15쪽 | 코팅의 표면 특성·여과 기능을 설명하고 투과성 조절 코팅을 소개한다. |
| 검색 2위 · **503** · 15쪽 | 투과성 조절 → 도달 속도 조절 → 일관된 검출을 직접 연결한다. |
| 검색 3위 · **496** · 14쪽 | 비색 센서의 느린 반응과 외부 판독 요건. 코팅으로 인한 속도 조절과는 다른 현상이다. |
| **공통 답변** | 코팅이 분석물의 이동 속도를 조절할 수 있다는 결론이 같다. |
| **OFF와 문헌 대조** | 필터 비유는 502의 선택적 통과 설명과 일부 겹친다. 첨부 파일이 있다는 안내는 실제 OFF 입력과 맞지 않는다. |
| **ON과 검색 근거 대조** | 하이드로겔 예시, 도달 속도 조절, 일관된 검출을 503과 정확히 연결한다. |
| **누락·적용 범위** | 핵심 누락 없음. ON은 속도가 무조건 빨라지거나 느려진다고 단정하지 않았다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

네, 맞습니다! 상처 위에 붙이는 센서에 얇은 코팅을 입히면, 측정하려고 하는 물질(예: 땀이나 상처 분비물 속의 포도당 등)이 센서에 닿는 속도가 달라지게 됩니다. 

이 코팅은 물질이 센서로 이동하는 것을 조절하는 '필터'나 '문' 같은 역할을 하기 때문입니다.

---
*(참고 자료: 첨부된 파일과 PDF 페이지를 통해 더 자세한 내용을 확인하실 수 있습니다.)*

**RAG ON**

네, 그렇습니다. 

상처 센서에 하이드로겔(hydrogel) 같은 코팅을 입히면, 측정하려는 물질(analyte)이 센서에 도달하는 속도를 조절할 수 있습니다. 이를 통해 일관되고 통제된 측정(detection)이 가능해집니다.

(출처: nihms-2086081.pdf, PDF 15쪽)

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 503 · 사전 기준 / 실제 검색 2위**　nihms-2086081.pdf · PDF 15쪽

> 135. Furthermore, coatings, including hydrogel-based coatings for adjustable permeability, 
> regulate the rate at which analytes reach the sensor, ensuring consistent and controlled 
> detection136. These coating elements are integral to developing advanced wound sensors, 
> providing reliable and precise data for effective wound management and treatment.
> For reliable in situ biomarker monitoring with conformal sensor-skin contact, stretchable 
> biosensors can be developed. This typically involves incorporating metallic or carbon-
> based nanomaterials into elastomers, such as polydimethylsiloxane (PDMS) or styrene–
> butadiene–styrene (SBS)137, 138. This approach enhances flexibility and adaptability, 
> Wang et al. Page 15
> Nat Rev Mater. Author manuscript; available in PMC 2025 June 18.
> Author Manuscript Author Manuscript Author Manuscript Author Manuscript

**한국어 해석**　투과성을 조정할 수 있는 하이드로겔 등의 코팅은 분석물이 센서에 도달하는 속도를 조절하여 일관되고 제어된 검출을 가능하게 한다. 이러한 부품은 신뢰할 만한 센서 데이터를 얻는 데 기여한다. 피부와 밀착해 현장 측정하는 신축성 센서는 금속·탄소 기반 나노소재를 PDMS·SBS 같은 탄성체에 넣어 유연성과 적응성을 높일 수 있다는 설명으로 이어진다.

**청크 502 · 실제 검색 1위**　nihms-2086081.pdf · PDF 15쪽

> coatings, such as polyethylene glycol (PEG), hydrogels, Nafion, and chitosan are commonly 
> utilized129–132. These protective coatings introduce desired surface hydrophilicity, charge, 
> or porosity to minimize protein adsorption and cell adhesion, ensuring the sensors’ 
> functionality in complex wound fluids. Additionally, filtration membranes made from 
> materials like polyvinylidene fluoride (PVDF) or polytetrafluoroethylene (PTFE) are 
> employed to selectively permit the passage of target analytes while excluding larger 
> interfering substances86, 133. The stability of receptors, such as antibodies or enzymes, is 
> often addressed through receptor stabilization coatings such as silica-based materials and 
> polyvinyl alcohol (PV A), and cross-linking agents like glutaraldehyde or carbodiimide that 
> protect these sensitive elements from the harsh conditions of the wound environment118, 134, 
> 135. Furthermore, coatings, including hydrogel-based coatings for adjustable permeability,

**한국어 해석**　PEG, 하이드로겔, 나피온, 키토산 등 보호 코팅은 표면 친수성·전하·다공성을 조절해 단백질 흡착과 세포 부착을 줄인다. PVDF·PTFE 여과막은 표적 물질을 통과시키고 더 큰 간섭 물질은 배제한다. 실리카·폴리비닐알코올 코팅이나 가교제는 항체·효소 같은 수용체를 상처 환경으로부터 보호하는 데 쓰인다. 마지막에 투과성을 조절하는 하이드로겔 코팅을 소개하며 다음 청크로 이어진다.

**청크 496 · 실제 검색 3위**　nihms-2086081.pdf · PDF 14쪽

> in light emission (exemplified by changes in fluorescence or luminescence). Notably, these 
> alterations are directly associated with the levels of analyte molecules.
> In the realm of wound care, optical sensors, predominantly colorimetric ones, have been 
> developed to monitor crucial parameters including temperature, pH and small molecules 
> such as oxygen and amino acids119. The benefits of employing colorimetric sensors 
> in wound care include direct visual detection, design simplicity, cost effectiveness, and 
> ease of operation. Nevertheless, when compared to electrochemical sensors, colorimetric 
> sensors exhibit a slower response time and require an external readout system to 
> achieve quantitative measurements. Their dependence on visual color transformations 
> resulting from chemical reactions requires a duration to gather observable alterations, 
> which must subsequently be quantified by an external system. This stands in contrast to

**한국어 해석**　형광 등 발광 변화가 분석물 분자 수준과 연관된다는 앞 문장이 이어진다. 광학 센서, 특히 비색 센서로 온도·pH·산소·아미노산 등을 관찰할 수 있다. 눈으로 확인 가능하고 단순하며 경제적이지만 전기화학 센서에 비해 반응이 느리고 정량화에 외부 판독 장치가 필요하다. 색 변화가 나타날 때까지 기다린 후 외부 기기로 수치화해야 하기 때문이다. 끝 문장은 다음 부분으로 이어진다.

</details>

## 9. 새 피부가 상처 가장자리에서 자라 들어온다고 하던데, 그 세포들은 언제부터 움직이고 언제 멈추나요?

지정 청크 **1위** · ON 충실성 **2/2점**

| 확인 항목 | 문항별 대조 |
|---|---|
| **기준 314** | 314는 정상 치유에서 손상 후 수 시간 이내 가장자리에서 중앙으로 이동하며 서로 물리적으로 접촉하면 이동을 멈춘다고 설명한다. |
| 검색 1위 · **314** · 4쪽 | 이동 시작 시점·방향과 접촉 억제에 의한 정지를 직접 제시한다. |
| 검색 2위 · **368** · 7쪽 | 세포들이 만나 연속층을 이루면 이동에서 증식으로 전환한다. |
| 검색 3위 · **367** · 7쪽 | 세포가 부착을 풀고 단층을 형성해 이동하며 뒤쪽에서 새 세포가 공급되는 과정을 설명한다. |
| **공통 답변** | 수 시간 이내 시작하고 서로 만나면 멈춘다는 두 요소가 일치한다. |
| **OFF와 문헌 대조** | ‘보통 12~24시간’으로 범위를 좁히고 제공되지 않은 wound_healing.pdf를 인용한다. 세 청크에 그 시간 범위는 없다. |
| **ON과 검색 근거 대조** | 314로 시작·방향·정지를, 368로 접촉 후 증식 전환을 설명한다. |
| **누락·적용 범위** | ON은 질문의 두 요소와 출처를 모두 반영했다. 원문에서 ‘3일 이내’는 다른 세포의 증식에 관한 내용이므로 이동 시점에서 제외한 것이 적절하다. |

<details><summary>두 답변 전문 · 당시 출력 그대로</summary>

**RAG OFF**

새로운 피부 세포가 상처 가장자리에서 움직이기 시작하는 시기와 멈추는 시기는 다음과 같습니다.

* **움직이는 시기:** 상처가 난 후 **수 시간 이내**(보통 12~24시간 안팎)에 상처 가장자리에 있던 표피 세포(각질형성세포)들이 본래의 형태를 바꾸어 이동(상피화)하기 시작합니다.
* **멈추는 시기:** 이 세포들은 서로 마주 보고 있는 반대편 세포들과 **서로 만나서 부딪힐 때** 이동을 멈춥니다. 이를 '접촉 저해' 현상이라고 합니다. 세포들이 서로 닿아 빈틈이 메워지면 더 이상 이동하지 않고 원래의 층을 이루며 멈추게 됩니다.

---
참고자료: `wound_healing.pdf` (PDF 페이지 번호는 문서에 따라 다를 수 있습니다)

**RAG ON**

제공해주신 자료에 따르면, 상처가 난 후 피부 세포(각질세포 또는 상피세포)가 움직이기 시작하는 시기와 멈추는 시기는 다음과 같습니다.

* **움직이기 시작하는 때:** 피부가 다친 후 **몇 시간 이내**에 상처 가장자리에서 중앙을 향해 이동하기 시작합니다. (*Physiology, Wound Healing - StatPearls - NCBI Bookshelf.pdf*, PDF 4쪽)
* **움직임을 멈추는 때:** 이동하던 세포들이 서로 **물리적인 접촉을 하게 되면** 멈추게 됩니다. 주변 세포들과 만나 하나의 층을 이루면 이동을 멈추고 증식하는 단계로 바뀝니다. (*Physiology, Wound Healing - StatPearls - NCBI Bookshelf.pdf*, PDF 4쪽; *Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf*, PDF 7쪽)

</details>

<details><summary>이 문항의 기준·검색 청크 전문 · 영어 원문과 한국어 해석</summary>

**청크 314 · 사전 기준 / 실제 검색 1위**　Physiology, Wound Healing - StatPearls - NCBI Bookshelf.pdf · PDF 4쪽

> repair, anti-inflammatory macrophages.[39] Keratinocytes also activate fibroblasts through a
> feedback loop by producing fibronectin, tenascin C, and laminin 332.[40] During normal wound
> healing, keratinocytes begin migrating centrally from wound edges within hours of tissue injury,
> and epithelial stem cells begin proliferating from the basal layer of the epidermis and hair follicle
> root sheaths within 3 days.[41] The keratinocytes migrate over the wound edge until they make
> physical contact with each other. This contact inhibition from neighboring keratinocytes halts
> migration.[6]
> The final step of the proliferation phase is granulation tissue formation.[2] Fibroblasts migrate to
> the wound site and proliferate in response to growth factors produced by macrophages and other
> immune cells.[2][8] These fibroblasts produce MMPs that degrade the present fibrin clot.[42]
> Fibroblasts then synthesize a provisional matrix containing collagen type III,

**한국어 해석**　항염증성 대식세포에 관한 앞 문장 뒤, 각질형성세포가 피브로넥틴 등을 만들어 섬유아세포를 활성화한다고 설명한다. 정상 치유에서 각질형성세포는 조직 손상 후 수 시간 내 가장자리에서 중앙으로 이동하기 시작하고 상피 줄기세포는 3일 안에 표피 기저층과 모낭 뿌리집에서 증식을 시작한다. 이동하던 각질형성세포끼리 물리적으로 접촉하면 접촉 억제로 이동을 멈춘다. 이어 육아조직 형성과 성장인자에 반응한 섬유아세포의 이동·증식, MMP에 의한 피브린 응괴 분해, III형 콜라겐을 포함한 임시 기질 합성을 설명한다.

**청크 368 · 실제 검색 2위**　Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf · PDF 7쪽

> cells (cells that are actively migrating are incapable of proliferation). Epithelial cells in the
> leading edge of the monolayer produce and secrete proteolytic enzymes (MMPs) which enable
> the cells to penetrate scab, surface necrosis, or eschar. Migration continues until the epithelial
> cells contact other advancing cells to form a confluent sheet. Once this contact has been made,
> the entire epithelial mono layer enters a proliferative mode and the stratified layers of the
> epidermis are re-established and begin to mature to restore barrier function. TGF-β is one growth
> factor that can speed up the maturation (differentiation and keratinization) of the epidermal
> layers. The intercellular desmosomes and the hemi-desmosome attachments to the newly formed
> basement membrane are also re-established. Epithelialization is the clinical hallmark of healing
> but it is not the final event – remodelling of the granulation tissue is yet to occur.

**한국어 해석**　활발히 이동 중인 세포는 증식하지 못한다. 선두의 상피세포는 단백질분해효소(MMP)를 분비해 딱지·표면 괴사 조직을 통과한다. 전진하던 세포들이 만나 연속된 층을 이루면 이동 단계에서 증식 단계로 바뀌고 표피 층이 재형성·성숙해 장벽 기능을 회복한다. TGF-β는 분화와 각질화를 촉진할 수 있다. 데스모솜과 기저막 부착도 다시 형성된다. 상피화 후에도 육아조직 재형성이 남는다.

**청크 367 · 실제 검색 3위**　Principles of Wound Healing - Mechanisms of Vascular Disease - NCBI Bookshelf.pdf · PDF 7쪽

> attached to their neighboring cells by intercellular connectors called desmosomes and to the
> basement membrane by hemi-desmosomes. When growth factors such as epidermal growth
> factor (EGF), keratinocyte growth factor (KGF) and TGF-α are released during the healing
> process, they bind to receptors on these epithelial cells and stimulate migration and proliferation.
> The binding of the growth factors triggers the desmosomes and hemi-desmosomes to dissolve so
> the cells can detach in preparation for migration. Integrin receptors are then expressed and the
> normally cuboidal basal epithelial cells flatten in shape and begin to migrate as a monolayer over
> the newly deposited granulation tissue, following along collagen fibers. Proliferation of the basal
> epithelial cells near the wound margin supply new cells to the advancing monolayer apron of
> cells (cells that are actively migrating are incapable of proliferation). Epithelial cells in the

**한국어 해석**　상피세포들은 데스모솜으로 이웃 세포에, 헤미데스모솜으로 기저막에 붙어 있다. EGF, KGF, TGF-α 등이 수용체에 결합하면 이동·증식이 촉진되고 결합 구조가 풀린다. 바닥층 세포가 납작해져 콜라겐 섬유를 따라 새 육아조직 위로 단층을 이뤄 이동한다. 상처 경계 근처에서 기저 상피세포가 증식해 전진하는 층에 새 세포를 공급한다. 이동 중인 세포 자체는 활발히 증식하지 못한다.

</details>

## 종합 판독

3번과 6번은 지정 ID를 모두 놓쳤지만 3번의 대체 문단은 치유 지연을 직접 설명했고 6번은 pH의 단독 진단 능력을 뒷받침하지 못했다. 같은 기준 487을 2위로 검색한 2번과 7번에서도 결과가 갈렸다. 2번은 비교 대상의 범위를 넓혔고, 7번은 장점·한계·단위를 원문 범위 안에서 설명했다.

ON은 2점 6개, 1점 2개, 0점 1개로 평균 14/9 ≈ 1.56점이었다. OFF도 여러 문항에서 핵심 결론에 도달했지만 신규 문항 7~9는 제공되지 않은 첨부 파일을 언급했다. 1번에서는 ON 답변이 근거에 충실하면서도 주변 피부 관리가 빠졌다. 단일 LLM 평가자가 소수 문항의 1회 출력을 판독한 결과이며 임상 안전성이나 의료 정확도를 측정하지 않았다.

[2차 세션 원본](세션원본.txt) · [사전 기준](문항과_사전기준.md) · [저장된 청크 목록](../../DressingExpert/RAGtexts/chunks.json)
