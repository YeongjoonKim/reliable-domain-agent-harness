# System fact summary

2026-10-03 코드·기존 실행 기록·읽기 전용 관리자 화면 대조 기준입니다.
운영 상담, 별도 관리자 Scientific Runtime, 공개 Core의 실행·평가 범위를 구분합니다.

| 책임 | 운영 상담 / 관리 | Scientific 관리자 Runtime | 독립 Public Core |
|---|---|---|---|
| 입력·계획 | LLM 질문 이해·TurnState·coverage/search/answer plan | goal·limits·모델 계획 | 명시 Need·Plan·대체 시도 |
| 도구 | 기존 SQL·Vector·KG·웹·Vision 경로 | 공식 SQL·공개 vector·학술 어댑터 | 합성 lookup·수치 계산 |
| 문맥 | 최근 대화·장기 기억·Context Pack | goal 기반 별도 실행 | 명시 요청; 경량 데모의 session 메모리는 별도 |
| 검증 | evidence gate·답변 verifier·repair | 모델 근거 판정·span ID·원문 검증 | 정형 claim·단위·시점·exact span/hash |
| 기록 | 요청 timing·검색량·usage·품질 로그 | PostgreSQL run·step·evidence | trajectory·provenance·replay bundle |
| 재현 | 요청 추적과 정책 이력 | 저장 관측·판정 재검증 | configuration/evidence replay |
| 평가 | 품질 이슈→회귀 worker→사람 승인 | 합성 실행 계약·저장된 live 실행 | 24-case paired synthetic evaluation |
| 실행 제어 | 관리자 권한·서명 서비스/배치 요청·호스트 워커 | 관리자 소유권·제한 실행 | tool 예산·Docker 계산 격리 |
| MCP | 일반 도구 API와 구분 | 내부 형태 adapter | 실제 stdio subset |

[현재 아키텍처](architecture/01_system_architecture.svg) ·
[운영 대응표](actual-engineering.md) · [실행 제어](execution-control.md) ·
[Scientific 근거](scientific-execution.md) · [Public Core](public-core.md).

## Catalog and adapter counts

기존 Tools 캡처는 소스 45개, capability 26개를 표시합니다.
명시 Typed Adapter는 implemented 14개 / unconnected 12개로 집계됐습니다.
이는 캡처 시점의 카탈로그·어댑터 구성이며 특정 요청의 실제 호출 수가 아닙니다.
기존 상담의 모든 도구 경로가 새 Typed Executor로 이관됐다는 의미도 아닙니다.
