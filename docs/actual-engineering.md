# Existing Production Consultation Architecture ↔ Implementation Evidence

운영 상담, 별도 비공개 Scientific Harness, 독립 Public Core의 구현 범위를 구분합니다.
아래 대응표는 2026-10-02 기준 운영 코드·component catalog·관리자 UI의 책임을 정리합니다.

2026-10-03에는 [관리자 API·호스트 실행 제어](execution-control.md)와
[실제 Scientific 실행·선택 근거·사용량](scientific-execution.md)을 추가 대조했습니다.
현재 [아키텍처 모음](architecture/README.md)은 운영 상담·Scientific Runtime·Public Core를 각각 표시합니다.

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

운영 상담 전체에 claim graph와 step I/O·환경 snapshot을 일관되게 연결하는 Replay는 후속 과제입니다.
단계 duration을 더한 값을 실제 end-to-end latency나 병렬 waterfall로 해석하지 않습니다.

## Separate Scientific Harness

비공개 `scientific_harness/semantic_review.py`는 원래 goal과 계획의 요구사항 각각을
검색 근거에 대조합니다. 서버가 원문을 길이 제한 구간으로 나누면 LLM이 evidence ID·span ID를
선택하고, 서버가 ID 유효성·인용 누락·원문 일치를 검사합니다. 모델이 인용문을 다시 생성하지 않도록 한 구조입니다.
의미적 지지 여부는 모델의 판정이며 독립 정답으로 취급하지 않습니다.

`runtime.py`는 이 검토 결과와 모델 호출 정보를 실행 기록에 연결합니다.
Docker 계산 도구와 configuration/evidence replay도 별도로 구현돼 있으며,
기존 상담 경로 전체의 전환 여부와는 구분합니다.
2026-10-02 선택 회귀 suite는 229개 통과, 합성 제어 사례 20개는 conformance 확인 범위입니다.

## Independent Public Core

공개 코어는 운영 소스를 복사하지 않은 독립 구현입니다.
[`verifier.py`](../src/harness/verifier.py)는 정형 claim의 대상·지표·단위·값·시점을 대조하고,
claim과 연결된 exact evidence span과 source hash를 검증합니다.
자유서술에서 최적의 구간을 찾는 LLM 의미 탐색은 포함하지 않습니다.

[`sandbox.py`](../src/harness/sandbox.py)는 명시적 로컬 image ID, 네트워크 차단, 읽기 전용 파일시스템,
non-root UID, capability 제거, CPU·memory/swap·pids 제한과 격리된 tmpfs를 적용합니다.
실행 timeout·출력 제한·종료 상태·cleanup을 추적하며 호스트 실행 fallback은 없습니다.
Docker의 공유 커널·daemon 권한 등 보안 경계는 [상세 문서](public-core.md#sandbox-and-scientific-slice)에 남깁니다.

[`replay.py`](../src/harness/replay.py)는 설정·도구 버전·입출력 hash를 대조하고 저장된 근거로
Verifier를 재실행합니다. 외부 도구 재호출이나 LLM 생성의 bit-identical 재현을 보장하는 기능은 아닙니다.

## Repository Ownership of the Story

Harness는 실행 계약·도구 선택·근거·신뢰성·평가를 설명합니다.
Reporting은 수집·정규화·KREI 검수·리포트 생성, Multimodal은 Vision 실행과 상담 연결,
Fine-tuning은 데이터셋·학습·adapter·serving을 설명합니다.
