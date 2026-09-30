# Reliable Domain Agent Harness & Verification

Planning · Tools · Evidence · Verification · Evaluation · Traceability

## 01 Overview

An offline **domain-bounded runtime** that separates tool outcomes from supported
claims. Structured requests become bounded parallel mock calls, scoped evidence,
verified template answers and execution traces. **14 behavioral regression tests**
exercise these boundaries; this is not a live LLM agent or production release.

This repository is a sanitized and reconstructed technical showcase based on engineering experience from a private production AI platform.
It does not contain proprietary source code, private data, internal APIs, or production configuration.

본 저장소는 비공개 운영 AI 시스템의 설계·개발 경험을 기반으로 독립 재구성한 공개 기술 예제입니다. 회사 소스, 비공개 데이터, 내부 API 및 운영 설정은 포함하지 않습니다.

## Key System Strengths

| Design decision | Why | Implementation evidence | Limitation |
|---|---|---|---|
| Bounded execution | Keep requests finite | `DemoRuntime`: budget, deduplication, deadlines | One structured pass, no semantic planner |
| Explicit tool outcomes | Preserve usable sibling results | found/empty/timeout/error states, async calls | Synthetic lookups, no external connectors |
| Evidence-aware generation | Reject unsupported values | Exact subject/value/unit claim checks | Templates, not arbitrary prose verification |
| Scoped summary memory | Avoid adding sources to a summary | Session + subject reuse tests | Process memory, no tenant authentication |
| Execution observability | Explain what happened | Logical events and artifact digest | No full external replay or measured production latency |

Evidence: [runtime](src/sample_agent.py), [behavioral tests](tests/test_sample.py).
Human-governed deployment, live vision integration and model serving are experience
context / reference design, **not implemented sample strengths**.

## System Fact Summary

| Area | Public sample | Status / boundary |
|---|---|---|
| Runtime / planner | Domain-bounded structured-request plan | IMPLEMENTED; no natural-language interpretation |
| Tool / knowledge | Two synthetic lookup categories | PARTIAL; vector, graph, web and vision connectors PROPOSED |
| Memory | Last answer per session and subject | PARTIAL; no durable identity or expiry |
| Verification | Request, evidence and exact claim constraints | IMPLEMENTED for fixture facts only |
| Evaluation | Offline regressions | IMPLEMENTED; deployment approval loop PROPOSED |
| Observability | Logical traces, fixture links, stable hash | PARTIAL; not end-to-end replay |
| Multimodal / model runtime | Reference integration boundaries | PROPOSED here; no model loaded |
| API categories | Agent and Health dispatcher | IMPLEMENTED in process; HTTP service PROPOSED |

[Generalized engineering context](docs/system-facts.md) is distinct from sample scope.
Status vocabulary: **IMPLEMENTED / PARTIAL / PROPOSED**. Synthetic/mock describes the
data or dependency, not an additional implementation status.

## 02 Problem

A retrieved record need not answer the question. Empty data, timeout and tool failure
are different outcomes. Summaries must preserve sources; separate sessions must not
silently share context. A citation alone cannot establish value or scope correctness.

## 03 Architecture

![Generic system architecture](docs/architecture/01_system_architecture.svg)

Structured request → validate/plan → select calls → execute/observe → assemble evidence
→ template generation → verify/review → respond or restrict. Language interpretation,
iterative re-search and model repair remain PROPOSED.
[Nine diagrams and Mermaid sources](docs/architecture/README.md).

## 04 Key Engineering Decisions

Independent calls run concurrently with finite budgets. Failed branches remain visible.
Summary mode makes no new searches. Evidence IDs survive into claims.
[Decisions and rejected alternatives](docs/design-decisions.md).

Traceability asks **what happened**; provenance asks **which facts contributed**;
reproducibility asks **whether conditions can be reconstructed**. Logical events,
fixture links and hashes implement only parts of these different requirements.

## 05 Implementation

[src/sample_agent.py](src/sample_agent.py) contains the runtime and two synthetic tools.
[API design](docs/api-design.md): Agent, Retrieval, Vision, Evaluation, Admin, Reporting
and Health are generic categories; only Agent and Health have in-process demo routes.
No HTTP listener, real registry rows, SQL, personal data or model runtime is included.

**What We Verify:** allowed request fields, budgets, known metrics, returned fact scope,
value/unit correspondence and unresolved requirements.

**What We Cannot Guarantee:** natural-language understanding, external truth/freshness,
semantic correctness of generated prose or adversarial model robustness.

## 06 Example

`python3 -m src.sample_agent` returns two invented glassleaf metrics, then a summary
with zero additional calls. The [Reconstructed Public Demo](demo/index.html) separately
illustrates complete/partial/summary states. It is authored static data, not a live
Python API, original screenshot or production uptime evidence.

## 07 Evaluation

14 behavioral tests cover budgets, deduplication, partial failure, timeout vs empty,
cancellation, changed claims and memory isolation. Repository-quality tests separately
exercise the checking tool. These counts are not answer-accuracy benchmarks.
[Evaluation](docs/evaluation.md) · [Local validation record](docs/validation.md).

## 08 Failure / Limitations

No live LLM, persistent memory, authentication, vector/graph database, repair model,
sandbox, multi-agent execution or Agent RL. Do not expose this example as a service.
The human-governed evaluation/feedback diagram is a proposed deployment workflow,
not automatic training. [Failure boundaries](docs/limitations.md).

## 09 Reproducibility

Python 3.10+ standard library; no install, credentials, GPU or network required.
Fixed synthetic facts and canonical hashes support deterministic comparisons,
not frozen external retrieval or full production replay.
[Maintenance and release](docs/maintenance.md).

## 10 Repository Structure

- `src/`: independent runtime.
- `tests/`: behavioral and repository-quality regressions.
- `examples/`: documented synthetic requests.
- `demo/`: offline illustrative dashboard.
- `docs/`: architecture, API, evaluation, decisions and limitations.
- `scripts/` and `.github/`: local checks and CI.

## 11 Quick Start

From this repository root:

```sh
python3 -m src.sample_agent
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

CI targets Python 3.10 and 3.12. Hosted CI and GitHub rendering are pending publication.

## 12 Research Relevance

Evaluate evidence recall per requirement, paraphrased/multi-turn request interpretation,
source freshness and paired quality/cost. A meaningful extension needs labeled cases,
not more agent roles by default.

MY CONTRIBUTION: author-confirmed engineering experience. PLATFORM CONTEXT: private
workflows, not disclosed implementation. PUBLIC RECONSTRUCTION: this independent sample.
FUTURE RESEARCH: explicitly unimplemented extensions.

[Publication review](PUBLICATION.md) · [License notice](LICENSE-NOTICE.md) ·
[Security](SECURITY.md). No open-source license has been selected.
