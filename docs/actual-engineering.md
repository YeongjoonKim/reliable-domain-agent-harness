# Existing Production Consultation Architecture ↔ Implementation Evidence

추가 확인(2026-10-02): 별도 비공개 Scientific Harness의 goal/claim 기반 의미 검토, 서버 선택 span(실제로 claim을 뒷받침하는 정확한 문장/구간), Docker 격리(Agent가 계산이나 Python 실행을 할때 독립적 컨테이너 격리), configuration/evidence replay 재실행 가능 경로를 검토했고 선택 회귀 suite 229개가 통과했습니다. 20개 합성 제어 사례는 conformance이며 성능 benchmark는 아닙니다. 아래 표는 기존 상담·관리 화면의 범위입니다. 새 공개 코어는 이를 복사하지 않고 독립 작성했으며 [Public Core](public-core.md)로 구분합니다.

검토일: 2026-10-02. 현재 코드와 component catalog, 실제 운영 관리자 UI를 함께 확인했습니다.
기존 Reference Architecture는 유지하고 아래 대응표로 실제 구현과 연결합니다.

| Harness stage | 실제 구현 책임 | 근거 화면 | 범위 |
|---|---|---|---|
| Entry / Lifecycle | 인증·소유권·요청 예산·취소 | Request Architecture | CONNECTED |
| Interpretation | QuestionUnderstanding, UnifiedRouter, TurnState | Architecture + Trace의 question understanding / intent | CONNECTED |
| Planning / Routing | search rewriter, coverage plan, search agent, answer planner | Runtime & Tools + Planner detail | CONNECTED |
| Typed execution | request contract / search plan / dependency retrieval | Executor detail | 구현됨, 상담 통합 PARTIAL |
| Capability Registry | agri_data_catalog의 소스·capability·필터 | Runtime & Tools | CONNECTED |
| Tool Execution | execute_agentic_search와 iteration 실행 | Runtime & Tools + 실제 search timing | CONNECTED |
| Retrieval | 구조화 DB, hybrid RAG, vector, semantic rerank, web, KG | Tools + Trace | CONNECTED |
| Context / Memory | memory utils, longterm memory, context pack, project context store | Memory Engineering View | CONNECTED; 개인 원문 공개 없음 |
| Evidence | evidence_gate, agri_evidence, response_pipeline | Verification Engineering View | CONNECTED |
| Generation | model runtime, answer planning, context injection | Architecture | CONNECTED |
| Verification / Repair | response_verifier, repair, 최종 SSE | Verification + Trace 상태 | CONNECTED |
| Trace | 단계별 timing, 품질 상태, LLM usage | 실제 요청 추적 + Harness Trace | CONNECTED |
| Evaluation / Feedback | 회귀 worker, 품질 보정 worker, 정책 검토·승인 | 실제 회귀 평가 및 승인 게이트 | CONNECTED |
| Report / Vision tools | report builder와 image diagnosis의 상담 연결 | 별도 Reporting / Multimodal evidence | CONNECTED |
| MCP / Replay / Scientific | 기존 상담 통합은 부분적; 별도 Scientific Harness 및 Public Core에서 구현·검증 | 상세문서 | 기존 상담: PARTIAL / Public Core: IMPLEMENTED 범위 별도 |

## What the Screens Mean

Architecture와 Harness Engineering View는 코드의 책임을 보여주는 설명 화면입니다.
요청 추적은 저장된 개별 실행의 관측이며 회귀 평가는 실제 케이스·실행 이력의 관리 기능입니다.
이 세 가지를 동일한 종류의 실행 증거로 취급하지 않습니다.

- 2026-10-02: 실제 Architecture, 요청 추적의 지표·단계별 시간, 회귀 평가 관리자 새 촬영.
- 2026-09-30: Harness Tools, Context/Memory, Verification 등 설명·관찰 화면.
- 모든 촬영은 조회 전용이며 신규 정책 승인·배포·평가 실행 없이 기존 기록을 사용했습니다.
- 질문/답변 원문과 계정 정보는 필요 영역 밖으로 크롭했습니다.

## Integration Boundary

기존 상담 경로는 LLM 질문 이해·여러 검색·근거 gate·검증/repair와 연결되어 있습니다.
동시에 새로운 typed executor의 상담 경로 통합은 PARTIAL로 남아 있습니다.
도구 목록에 등록된 항목, 명시 adapter 구현, 실제 요청에서 실행된 항목은 별도로 확인해야 합니다.

전체 claim graph와 step I/O·환경 snapshot이 일관되게 저장되는 replay는 후속 과제입니다.
단계 duration을 더한 값을 실제 end-to-end latency나 병렬 waterfall로 해석하지 않습니다.

## Repository Ownership of the Story

Harness는 실행 계약·도구 선택·근거·신뢰성·평가를 설명합니다.
Reporting은 수집·정규화·KREI 검수·리포트 생성, Multimodal은 Vision 실행과 상담 연결,
Fine-tuning은 데이터셋·학습·adapter·serving을 설명합니다.
