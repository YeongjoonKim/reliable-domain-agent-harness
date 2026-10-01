# Design Decisions

도구 호출 수·중복·deadline을 실행 계약으로 제한하고 독립 호출만 병렬화합니다. 요약은 검색과 분리하여 출처가 늘어나지 않게 합니다. 출처 존재 여부가 아니라 subject/value/unit의 일치를 검사합니다.

공개 예제의 자연어 해석은 미구현입니다. 키워드 규칙으로 해석 LLM을 구현한 것처럼 보이게 하지 않습니다. 무한 반복 대신 한 차례 실행과 미해결 요구를 반환합니다.

화면의 설명 카드는 정적입니다. 추가한 Executed Python snapshot은 공개 exporter의 계산 결과이며 tests/test_evidence.py가 저장본과 재계산을 비교합니다. live 운영 관찰로 주장하지 않습니다.
