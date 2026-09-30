# Evidence and evaluation limits

The test suite runs without model calls, private data, databases or network access.
It checks complete and partial results, budgets, deduplication, timeout/error/empty
distinction, request rejection, cancellation propagation, unchanged summary sources,
session/subject isolation and tampered claims.

Fixture correctness is assumed for this example; checking a value against a fixture
does not validate that source against the real world. A deterministic artifact digest
does not freeze environment dependencies. The dashboard has separately authored
static examples, not measured latency or production success rates.

Failure analysis: changed fact value → correspondence check rejects; slow tool →
timeout is recorded while another result survives; summary with new search needs →
request is rejected. Fixing these contracts does not prove language-model accuracy.

Future evaluation needs independent task labels, paraphrases, multi-turn corrections,
source freshness, adversarial inputs and paired cost/quality measurements.
