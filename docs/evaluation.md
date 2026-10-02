# Evaluation / 평가 범위

현재 새 코어의 전체 57 test methods, 24 synthetic conformance scenarios 및 동일 데이터의 paired evaluation은 [Public Core](public-core.md)에 있습니다. 아래는 보존된 초기 데모 평가입니다.

## 공개 코어 비교 평가

동일한 합성 입력·초기 도구·결정적 후보 생성기에서 verification/retry 유무를 비교했습니다.
기록된 task success는 baseline 8/24, Harness 24/24이며 평균 도구 호출은 1.083회에서 1.333회로 늘었습니다.
Conformance와 비교 평가가 같은 24개 시나리오를 사용하므로 독립 holdout이 아닙니다.
이 수치는 설계된 실패에 대한 제어 흐름 평가이며 농업 정확도·LLM 성능 비교로 해석하지 않습니다.
[결과 JSON](../examples/paired-evaluation.json)과 [지표 정의](public-core.md#paired-synthetic-evaluation)를 제공합니다.

## 초기 경량 데모

23개 테스트: 행동 계약 14개, 실행 snapshot 2개, 저장소 검사기 7개입니다. timeout/error/empty, 부분 결과 보존, 요약의 검색 생략, session/subject 격리, 변조한 claim 거부와 취소 전파를 검사합니다.

exporter의 5개 probe는 실제 계산한 계약 확인이며 모델 정확도나 독립 benchmark가 아닙니다. UI의 화면 전환과 Python 평가 실행은 서로 다른 작업입니다.

fixture의 정확성은 이 예제의 전제입니다. exact match는 현실 세계의 사실 여부를 보장하지 않습니다. 후속 평가는 paraphrase, 다중 턴 정정, freshness, 적대적 입력과 비용/품질의 paired 비교를 필요로 합니다. 인간 승인 없는 배포 변경이나 Agent RL은 구현하지 않았습니다.
