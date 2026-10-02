# Reliable Domain Agent Harness & Verification

### 질문 이해·검색·근거·검증·평가를 연결하는 Domain-bounded Agent Runtime

[![CI](https://github.com/YeongjoonKim/reliable-domain-agent-harness/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/YeongjoonKim/reliable-domain-agent-harness/actions/workflows/ci.yml)

## Actual Engineering Experience

농업 도메인 상담에서 질문·대화 맥락을 검색 계획으로 연결하고,
구조화 DB·Vector·KG·웹·Vision의 근거를 조합해 답변을 생성·검증하는 시스템을 개발했습니다.
관리자는 실행 Trace, 품질 이슈, 회귀 평가, 정책 승인으로 실패 원인과 개선 결과를 확인합니다.

![System architecture](docs/architecture/01_system_architecture.svg)

이 Reference Architecture에 실제 구현을 대응시킨 [단계별 Evidence Map](docs/actual-engineering.md)을 제공합니다.
아래는 **실제 플랫폼의 구현 경험**이며, 저장소의 독립 Python 예제와 범위를 구분했습니다.

## System Strengths

| Decision | 실제 구현과 이유 |
|---|---|
| Task / Context → Search Contract | 원문·이력·메모리에서 대상과 요구를 정리해 검색 범위를 계획 |
| Capability-based Retrieval | 도구가 지원하는 데이터·필터를 기준으로 실행 영역 선택 |
| Evidence-aware Generation | 검색 성공과 답변에 충분한 근거 확보를 구분 |
| Verification / Repair | 검증 결과를 답변 보정·품질 이슈 기록에 연결 |
| Human-governed Feedback | 실제 실패 사례를 회귀 평가와 정책 검토로 연결 |
| Execution Observability | 단계별 시간·검색량·검증 상태·사용량을 관리자에서 추적 |

## Implementation Evidence

설명 전용 Harness 메뉴와 **실제 운영 관리 기능**을 함께 보여줍니다.
2026-10-02 새 촬영본은 읽기 전용 API와 현재 UI를 격리된 검증 브라우저에서 연결했습니다.
2026-09-30 Harness 캡처는 동일 기능의 설명·관찰 화면으로 별도 표시합니다.

### 1. Request Architecture

**Purpose** — 사용자 입력부터 최종 응답·관찰까지 실행 책임을 확인합니다.

![Actual request architecture admin](docs/screenshots/admin-request-flow.png)

**What this demonstrates** — 실제 Architecture 관리자 메뉴의 질문 이해, 검색, 생성, 검증, SSE, Trace 연결.
**Architecture relation** — Entry → Interpretation → Retrieval → Generation → Verification → Response.

### 2. Planning & Tool Integration

**Purpose** — 검색 계획과 사용 가능한 데이터 도구의 관계를 검토합니다.

![Operational Harness runtime and tools](docs/screenshots/admin-tools.png)

**What this demonstrates** — 실제 capability catalog와 실행 경로 설명. 캡처 기준 45 sources / 26 capabilities.
명시 typed adapter는 14 implemented / 12 unconnected로 구분됩니다.
**Architecture relation** — Planning → Capability Registry → Tool Execution.

### 3. Context & Memory

**Purpose** — 질문 해석에 전달되는 맥락과 메모리 계층을 점검합니다.

![Operational context and memory engineering view](docs/screenshots/admin-memory.png)

**What this demonstrates** — 현재 코드의 대화 맥락·장기 기억·Context Pack 연결을 설명하는 Engineering View.
개인 메모리 원문을 열람하는 화면과 구분됩니다.
**Architecture relation** — Conversation / Memory → Interpretation / Context Pack.

### 4. Evidence & Verification

**Purpose** — 검색 결과의 존재와 근거 충족·최종 답변 검증을 구분합니다.

![Operational verification engineering view](docs/screenshots/admin-verification.png)

**What this demonstrates** — evidence gate, response verifier, repair와 품질 환류의 구현 대응.
**Architecture relation** — Evidence → Answer → Verification / Repair → Quality Issue.

### 5. Execution Trace

**Purpose** — 실제 요청에서 어느 단계에 시간이 소요됐는지 확인합니다.

![Actual request trace stage timings](docs/screenshots/admin-trace-timing.png)

**What this demonstrates** — 요청 추적 관리자의 저장된 search·intent·question understanding·RAG 단계 시간.
개인 질문·답변 원문은 크롭으로 제외했습니다.
**Architecture relation** — Runtime stages → Trace storage → Diagnosis.
이는 한 요청의 기록이며 전체 성능 평균이나 병렬 waterfall은 아닙니다.

### 6. Regression & Approval Gate

**Purpose** — 실제 품질 문제를 평가 케이스로 관리하고 정책 후보를 검토합니다.

![Actual regression management and execution history](docs/screenshots/admin-regression.png)

**What this demonstrates** — 회귀 케이스, 위험도·상태, 기준선/정책별 실행 이력과 성공·실패 상태.
새 평가나 승인을 실행하지 않고 보존된 이력을 조회했습니다.
**Architecture relation** — Quality Issue → Regression → Human Approval.

추가 상세 화면은 [Screenshot Gallery](docs/screenshots.md)에 있습니다.
수집·KREI·보고서 상세는 [Reporting](https://github.com/YeongjoonKim/ai-domain-intelligence-reporting),
이미지 모델과 상담 연결은 [Multimodal](https://github.com/YeongjoonKim/multimodal-domain-ai)에서 다룹니다.

## Actual Runtime / Public Reference / Lightweight Demo

| 구분 | 범위 |
|---|---|
| Actual Engineering Experience | LLM 질문 이해, 다중 검색, 맥락·메모리, evidence gate, 검증/repair, SSE, 운영 관리 |
| Public Reference Implementation | 계약·예산·결과 상태·근거 대응·검증을 독립 코드로 재구성 |
| Public Lightweight Demo | 구조화 요청 + 두 합성 도구 + session/subject 메모리 + 템플릿 답변 |

공개 예제의 흐름은 Validate → Plan → Deduplicate → Execute → Assemble → Verify → Respond입니다.
실패한 도구와 성공한 도구를 구분하며 요약 모드에서는 이전 검증본을 재사용합니다.
[실행 artifact](examples/execution.json) · [Runtime source](src/sample_agent.py) ·
[공개 API 계약](docs/api-design.md).

## Reproduce & Evaluation

Python 3.10+ 표준 라이브러리로 GPU·인증키 없이 실행합니다.

```sh
python3 -m src.sample_agent
python3 -m src.export_evidence
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

23개 공개 테스트와 5개 exporter probe는 계약·실패 처리·snapshot을 검증합니다.
운영 회귀 이력과 공개 테스트 수는 서로 다른 평가입니다.
[설계 결정](docs/design-decisions.md) · [평가 범위](docs/evaluation.md).

## Scope & Limitations

실제 서비스의 typed task executor는 기존 상담 경로와의 통합이 **PARTIAL**입니다.
MCP는 prototype이고 완전한 claim-level provenance / replay, Scientific Agent 확장은 후속 과제입니다.
공개 코드는 자연어 LLM·운영 DB·개인 메모리·외부 connector를 포함하지 않는 독립 reference입니다.
스크린샷의 구현 상태, 실제 실행 이력, 모델 품질 측정은 별도로 해석해야 합니다.

[System Facts](docs/system-facts.md) · [검증 기록](docs/validation.md) ·
[공개 경계](PUBLICATION.md) · [License notice](LICENSE-NOTICE.md) · [Security](SECURITY.md).
