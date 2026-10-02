# System Fact Summary

2026-10-02 실제 소스·관리자 기능 재검토 기준. [단계별 구현 근거](actual-engineering.md).

| 영역 | Actual Engineering Experience | Public Reference / Demo |
|---|---|---|
| Interpretation | LLM 질문 이해·이력·TurnState·라우팅 | 구조화 입력 검증 |
| Planning | coverage plan·검색 agent·answer planner | 유한 도구 계획 |
| Tool categories | 구조화 DB·Vector·KG·웹·Vision | 두 합성 lookup |
| Context / Memory | 최근 대화·장기 기억·Context Pack | session/subject 프로세스 메모리 |
| Evidence | 근거 gate·도메인 자료·등록정보 연결 | exact subject/value/unit 검사 |
| Verification | response verifier·repair·품질 이슈 | 정형 claim 계약 |
| Evaluation | 회귀 worker·케이스·실행 이력·정책 승인 | 단위 테스트와 exporter probe |
| Observability | 단계 시간·검증 상태·LLM usage | 논리 이벤트·artifact hash |
| Model runtime | 로컬 모델 serving과 애플리케이션 | GPU 없이 실행 |
| Report / Vision | 빌더·진단 도구의 상담 연결 | 별도 공개 저장소의 예제 |

Typed executor의 상담 통합은 PARTIAL이며 MCP prototype·claim provenance/replay·Scientific 확장은 별도 범위입니다.
실제 관리 기능의 화면과 Harness 설명 화면을 구분해 [갤러리](screenshots.md)에 표시합니다.
