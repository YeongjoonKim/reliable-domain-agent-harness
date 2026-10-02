# Design Decisions

도구 호출 수·중복·deadline을 실행 계약으로 제한하고 독립 호출만 병렬화합니다. 요약은 검색과 분리하여 출처가 늘어나지 않게 합니다. 출처 존재 여부가 아니라 subject/value/unit의 일치를 검사합니다.

공개 예제는 구조화 요청부터 시작해 한 차례 유한 실행과 미해결 요구를 반환합니다. 실제 플랫폼의 LLM 질문 이해와는 입력 경계가 다릅니다.

공개 demo UI의 설명 카드와 Executed Python snapshot을 구분합니다. 후자는 exporter의 계산 결과이며 tests/test_evidence.py가 재계산을 비교합니다. 별도로 실제 관리자 캡처와 운영 Trace를 제공합니다.
