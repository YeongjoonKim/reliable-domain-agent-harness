# Independently authored architecture

이 도식 모음은 초기 lightweight reference의 상태를 보존합니다. 최신 실행 코어와 구현 상태는 [Public Core](../public-core.md) 및 저장소 README 상단에 있습니다.

These SVGs and matching Mermaid sources describe generic engineering responsibilities,
not the topology or names of a private platform.

- IMPLEMENTED: implemented in this public sample only.
- PARTIAL: a limited demonstration, not end-to-end verification.
- PROPOSED: reference architecture or future work.

Synthetic/mock describes the data or dependency. PARTIAL nodes with mock tools do not
imply a live external connector; IMPLEMENTED always refers to the offline sample.

Both formats are authored from the same node/edge definitions. SVG is the directly viewable
asset; Mermaid is an editable source, not a claim that a Mermaid renderer produced the SVG.
No company diagrams, screenshot crops, server inventory or scale numbers are included.

- [Generic system architecture](01_system_architecture.svg) · [Mermaid](01_system_architecture.mmd)
- [Bounded execution flow](02_agent_runtime_flow.svg) · [Mermaid](02_agent_runtime_flow.mmd)
- [Heterogeneous tool contracts](03_tool_architecture.svg) · [Mermaid](03_tool_architecture.mmd)
- [Verification boundaries](04_verification_architecture.svg) · [Mermaid](04_verification_architecture.mmd)
- [Human-governed quality loop](05_evaluation_feedback_loop.svg) · [Mermaid](05_evaluation_feedback_loop.mmd)
- [Three different evidence questions](06_trace_provenance_reproducibility.svg) · [Mermaid](06_trace_provenance_reproducibility.mmd)
- [Vision as an uncertain tool](07_multimodal_tool_flow.svg) · [Mermaid](07_multimodal_tool_flow.mmd)
- [Public sample API boundaries](08_api_architecture.svg) · [Mermaid](08_api_architecture.mmd)
- [Logical runtime pattern](09_runtime_infrastructure.svg) · [Mermaid](09_runtime_infrastructure.mmd)
