# System Fact Summary

아래 public 열은 초기 lightweight demo 범위입니다. 새 독립 코어의 registry·검증·격리·재현·MCP 구현은 [현재 Public Core](public-core.md)를 기준으로 합니다. 기존 상담 executor와 별도 Scientific Harness의 범위를 혼동하지 않습니다.

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

## Catalog / Adapter 집계

관리자 Tools 캡처 기준 소스는 45개, capability는 26개입니다.
명시 Typed Adapter 연결은 implemented 14개 / unconnected 12개로 구분됩니다.
등록된 catalog 항목, adapter 구현, 특정 요청에서 실행된 도구는 서로 다른 집계입니다.
이 숫자는 화면 시점의 구성 정보이며 README에서는 실행 범위와 연결 상태 중심으로 설명합니다.
