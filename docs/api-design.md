# Generic API design

This document is independently designed; it is not an inventory of internal endpoints.

| API domain | Responsibility | This sample |
|---|---|---|
| Agent | Task execution | In-process dispatch |
| Retrieval | Evidence search | Internal mock tool contract |
| Vision | Uncertain multimodal candidates | Design only |
| Evaluation | Quality evaluation | Unit tests, not an HTTP endpoint |
| Admin | Engineering observability | Standalone static dashboard |
| Report | Evidence-aware decision support | Separate sample |
| Health | Runtime mode | In-process response |

## Implemented sample contracts

- `POST /api/demo/agent/query`: accepts only session, subject, needs and optional mode.
  Unknown fields/metrics and exceeded budgets return 400. No SQL or URLs accepted.
- `GET /api/demo/health`: reports offline_mock and production_connected=false.
- All other paths return 404.

Both are Python dispatcher branches, **not network listeners**.
Authentication, durable traces and internet deployment are deliberately absent.
A production transport would need tenant authorization, size limits, cancellation,
rate limits and an explicit data-retention policy before exposure.

Trace retrieval and evaluation HTTP routes are future examples, not implemented endpoints.
