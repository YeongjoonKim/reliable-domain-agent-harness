# Evaluation / 평가 범위

2026-10-08 로컬 공개 검증은 **76 test methods 통과**입니다. 기존 57개에 산출물·CLI·HTML 링크 회귀 19개를 추가했습니다. 24 synthetic conformance scenarios와 동일 데이터의 paired evaluation은 [Public Core](public-core.md)에 있으며, commit별 CI와 브라우저 결과는 [검증 기록](validation.md)에서 구분합니다. 아래 초기 경량 데모 평가는 별도 보존 이력입니다.

## 공개 코어 비교 평가

동일한 합성 입력·초기 도구·결정적 후보 생성기에서 verification/retry 유무를 비교했습니다.
기록된 task success는 baseline 8/24, Harness 24/24이며 평균 도구 호출은 1.083회에서 1.333회로 늘었습니다.
Conformance와 비교 평가가 같은 24개 시나리오를 사용하므로 독립 holdout이 아닙니다.
이 수치는 설계된 실패에 대한 제어 흐름 평가이며 농업 정확도·LLM 성능 비교로 해석하지 않습니다.
[결과 JSON](../examples/paired-evaluation.json)과 [지표 정의](public-core.md#paired-synthetic-evaluation)를 제공합니다.

[Core Evidence Explorer](../demo/index.html)의 5개 시나리오는 이 코어의 실제 Runtime·verifier·replay를
실행해 생성한 저장 산출물을 탐색합니다. 별도의 5개 성능 benchmark나 브라우저의 live 실행은 아닙니다.
정상 근거·복구 성공과 충돌·잘못된 인용의 안전한 거부를 함께 표시하며, 모든 시나리오의 상태가
`COMPLETED`여야 하는 것은 아닙니다. 일반 평가 실행은 새 결과를 `outputs/`에 쓰며,
공식 예제 갱신은 명시적 `--update-examples`로 구분합니다.

## 초기 경량 데모

23개 테스트: 행동 계약 14개, 실행 snapshot 2개, 저장소 검사기 7개입니다. timeout/error/empty, 부분 결과 보존, 요약의 검색 생략, session/subject 격리, 변조한 claim 거부와 취소 전파를 검사합니다.

exporter의 5개 probe는 실제 계산한 계약 확인이며 모델 정확도나 독립 benchmark가 아닙니다. UI의 화면 전환과 Python 평가 실행은 서로 다른 작업입니다.

fixture의 정확성은 이 예제의 전제입니다. exact match는 현실 세계의 사실 여부를 보장하지 않습니다. 후속 평가는 paraphrase, 다중 턴 정정, freshness, 적대적 입력과 비용/품질의 paired 비교를 필요로 합니다. 인간 승인 없는 배포 변경이나 Agent RL은 구현하지 않았습니다.
