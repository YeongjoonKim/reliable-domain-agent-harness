# Implemented API and protocol interfaces

회사 endpoint를 문서는 아닙니다. 새로 정의한 공개 Contract입니다.

| Interface | Implementation | Input / output | Execution |
|---|---|---|---|
| Public Core | src/harness/runtime.py | Need / Plan → result / trajectory / provenance | 독립 Python Runtime |
| MCP stdio subset | src/harness/mcp_adapter.py | initialize, ping, tools/list, tools/call | 실제 child process 표준 입출력 |
| Numerical tool | src/harness/scientific.py | 정형 숫자 → 계산·근거 | registry를 통한 계산 |
| Local demo dispatch | src/sample_agent.py | session / subject / needs / mode → status / claims / events | in-process 호출 |
| Local health contract | src/sample_agent.py | offline_mock, production_connected=false | in-process 조회 |
| Management evidence | 관리자 UI와 읽기 전용 캡처 | 서비스 상태 / run / checkpoint / 배치 | [별도 운영 구현](execution-control.md) |

## 실행되는 demo contract

- `POST /api/demo/agent/query`: session, subject, needs와 선택 mode만 허용합니다.
- `GET /api/demo/health`: offline_mock와 production_connected=false를 반환합니다.
- 알 수 없는 필드/metric 또는 초과 예산: 400.
- 다른 경로: 404.

```json
{"session":"public-demo","subject":"glassleaf","needs":["growth","moisture"]}
```

Agent 응답은 complete / partial / unresolved로 구분됩니다. Summary mode는 같은
session과 subject에 저장된 검증본을 재사용하며 새 sources를 만들지 않습니다.
저장본이 없으면 missing_context입니다.

두 경로는 [dispatch 함수](../src/sample_agent.py)의 분기이며 **HTTP 서버가 아닙니다**.
tenant authorization, 요청 크기 제한, rate limit, transport cancellation, trace 보관과
개인정보 retention은 운영 transport를 붙이기 전에 설계해야 합니다.
실행되는 Trace 조회·평가 HTTP endpoint는 없습니다.

## MCP and execution

`python3 -m src.harness.mcp_adapter`는 표준 입력의 JSON-RPC를 읽고 표준 출력에 응답합니다.
등록된 수치 도구의 permission·schema·timeout 경계를 사용합니다.
[프로토콜 범위와 실행 검증](public-core.md#minimal-real-mcp) 및
[인터페이스 도식](architecture/08_api_architecture.svg)을 함께 제공합니다.

실제 관리자 API는 서비스 제어·배치·모델 관리·Scientific 실행을 별도 권한으로 연결합니다.
[공개 화면과 제어 책임](execution-control.md)은 독립 Python 예제의 transport 기능과 구별됩니다.
