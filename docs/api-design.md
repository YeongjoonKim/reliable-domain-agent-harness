# Public API Design

회사 endpoint를 옮긴 문서가 아니라 새로 정의한 공개 계약입니다.

| API Domain | Responsibility | Main Input | Main Output | Status |
|---|---|---|---|---|
| Agent API | 요청 실행 | session, subject, needs, mode | status, claims, sources, missing, events | IMPLEMENTED / in-process |
| Retrieval API | 요구별 근거 회수 | subject, metric | fact / empty / timeout / error | PARTIAL / mock |
| Vision API | 시각 후보 수신 | image / metadata | candidates, uncertainty | PROPOSED |
| Evaluation API | 회귀 품질 검사 | cases, expected constraints | checks, failures | PARTIAL / Python tests only |
| Admin / Engineering API | 실행 관찰 | 공개 snapshot | 정적 UI | PARTIAL / no HTTP |
| Reporting API | 근거 보고 | observations, period | insights, source references | PROPOSED here / separate sample |
| Health / Runtime API | 실행 모드 | 없음 | offline_mock, production_connected | IMPLEMENTED / in-process |

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
