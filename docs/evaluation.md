# Evaluation / 평가 범위

23개 테스트: 행동 계약 14개, 실행 snapshot 2개, 저장소 검사기 7개입니다. timeout/error/empty, 부분 결과 보존, 요약의 검색 생략, session/subject 격리, 변조한 claim 거부와 취소 전파를 검사합니다.

exporter의 5개 probe는 실제 계산한 계약 확인이며 모델 정확도나 독립 benchmark가 아닙니다. UI의 화면 전환과 Python 평가 실행은 서로 다른 작업입니다.

fixture의 정확성은 이 예제의 전제입니다. exact match는 현실 세계의 사실 여부를 보장하지 않습니다. 후속 평가는 paraphrase, 다중 턴 정정, freshness, 적대적 입력과 비용/품질의 paired 비교를 필요로 합니다. 인간 승인 없는 배포 변경이나 Agent RL은 구현하지 않았습니다.
