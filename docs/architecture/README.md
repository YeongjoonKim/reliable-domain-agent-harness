# Architecture evidence

운영·별도 Scientific lane은 2026-10-03에 대조한 코드·관리자 기능·실행 산출물의 범위입니다.
독립 공개 코어의 실행·검증·복구·provenance·replay는 공개 소스와 생성된 합성 산출물로 구분합니다.
각 그림의 lane은 운영 상담, 별도 Scientific Runtime, 독립 공개 예제 중 해당 범위를 표시합니다.
서로 다른 lane의 단계 사이에 자동 호출이나 배포 연결을 의미하지 않습니다.

| Diagram | Scope | Editable source |
|---|---|---|
| [Execution, verification, recovery and replay](01_system_architecture.svg) | Public Core first; separate operational and Scientific evidence scopes | [Mermaid](01_system_architecture.mmd) |
| [Bounded execution and recovery](02_agent_runtime_flow.svg) | Public Core · src/harness/runtime.py | [Mermaid](02_agent_runtime_flow.mmd) |
| [Tool interfaces and execution responsibility](03_tool_architecture.svg) | Each lane has its own registry or routing implementation | [Mermaid](03_tool_architecture.mmd) |
| [Verification: scope, meaning and citation](04_verification_architecture.svg) | Three implemented verification contexts | [Mermaid](04_verification_architecture.mmd) |
| [Human-governed quality and evaluation](05_evaluation_feedback_loop.svg) | Operational feedback and public experiments have separate result sets | [Mermaid](05_evaluation_feedback_loop.mmd) |
| [Trace, provenance and frozen replay](06_trace_provenance_reproducibility.svg) | Public Core · configuration/evidence replay | [Mermaid](06_trace_provenance_reproducibility.mmd) |
| [Vision as a domain tool](07_multimodal_tool_flow.svg) | Implemented production consultation route | [Mermaid](07_multimodal_tool_flow.mmd) |
| [Implemented API and protocol boundaries](08_api_architecture.svg) | Local demo interfaces and production entry points are distinct | [Mermaid](08_api_architecture.mmd) |
| [Admin control plane and host execution](09_runtime_infrastructure.svg) | Implemented service-control path · distinct from agent-code sandboxing | [Mermaid](09_runtime_infrastructure.mmd) |

SVG와 Mermaid는 [동일 명세](diagrams.json)에서 생성합니다.
문구나 흐름을 수정한 뒤 `python3 scripts/render_architecture.py`로 갱신하고
`python3 scripts/render_architecture.py --check`로 동기화를 검사합니다.
그림은 일반화한 책임 구조이며 내부 주소·배포 설정·원본 코드는 포함하지 않습니다.

[Core Evidence Explorer](../../demo/index.html)는 공개 Runtime에서 발생한 실제 상태를 표시합니다.
이 아키텍처 그림의 모든 노드가 각 실행에서 순서대로 발생했다는 뜻은 아닙니다.
기존 [legacy 설명 UI](../../demo/legacy.html)와 승인된 관리자 캡처는 공개 코어 실행 화면으로 바꾸지 않습니다.
