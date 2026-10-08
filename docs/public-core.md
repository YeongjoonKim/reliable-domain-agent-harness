# Public Harness Core

Independently authored with synthetic data; no private source, prompts, schemas or records
were copied. `src/sample_agent.py` and the original dashboard remain a separate lightweight
compatibility example. Their snapshots are not relabelled as executions of the new core.

## Run and explore

From the repository root, with Python 3.10+ and no external packages, credentials or GPU:

```sh
python3 -m src.harness.demo
python3 -m src.harness.evaluation
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

Normal core CLI runs write fresh results under ignored `outputs/`. Tracked `examples/`
are reviewed snapshots and require explicit `--update-examples` to replace.

| Command | Default output |
|---|---|
| `python3 -m src.harness.demo` | `outputs/recovery.json` |
| `python3 -m src.harness.evaluation` | `outputs/paired-evaluation.json` and `outputs/evaluation-cases.json` |
| `python3 scripts/export_demo.py` | `outputs/demo/core-evidence.json` and `outputs/demo/core-evidence.js` |

The exporter calls the real synthetic Runtime, verification and replay paths. Use
`python3 scripts/export_demo.py --update-demo` only to refresh reviewed `demo/` artifacts.
`python3 scripts/export_demo.py --check` reruns the core and compares the tracked demo
artifacts without writing; it checks semantic consistency while retaining raw run IDs,
timestamps and timings in the stored artifacts. `--check` and `--update-demo` are separate modes.

Optional actual-browser validation uses an installed Chrome/Chromium executable and
Python's standard library, without a browser automation package:

```sh
python3 scripts/check_demo_browser.py
```

It checks every scenario, raw timeline event, verification signal, accepted/candidate claim,
provenance, exact source/citation offsets and local link under a repository URL prefix.
Desktop and narrow-window checks record the actual viewport dimensions; the original
legacy scenarios are also exercised. Results go to ignored `outputs/browser-validation.json`.
CI runs this separate browser check on Python 3.12. It is not part of the Python-only quick start.

The [Core Evidence Explorer](../demo/index.html) displays generated Runtime artifacts,
not a live service or an LLM response. It includes valid evidence, irrelevant evidence with
recovery, conflict, invalid citation span, and configuration/evidence replay.
Rejected claims are not accepted answers; a failed run can be the expected safe abstention.

GitHub displays that HTML as source. To use the interactive explorer locally:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open [localhost:8000/demo/](http://localhost:8000/demo/) and follow the execution JSON,
source, test and CI links. [Full generated artifacts](../demo/core-evidence.json) retain
the underlying run and replay data. The browser selects stored scenarios; it does not
execute Python, contact external APIs or rerun tools.
The [legacy dashboard](../demo/legacy.html) keeps the original explanatory UI and its
separate `src/sample_agent.py` snapshot. Its proposed extensions are not the status of
implemented Public Core replay. [Static hosting status](validation.md#static-demo-and-pages).

## Execution and verification

`Need` preserves subject, metric, unit, as-of date and maximum age. `Plan` supplies bounded
alternative attempts; calls within each attempt execute concurrently. No hidden LLM planner.
Registry enforces permission, supported schema subset, timeout, version and retry policy.
Structured/document lookup use different tool contracts over a shared synthetic backend;
they are not two real data connectors. Numerical analysis is a third, computational tool.

Verification separates retrieval presence, information-need relevance, numerical claim support
and exact source span/hash. Canonical statements come from a trusted structured adapter.
This is **not free-text semantic entailment** or proof that an external publisher is truthful.
Same-period conflicting values fail closed; different fresh periods select the latest.
Stale/future matching rows currently cause conservative rejection. All requested claims must
pass; rejected attempts return no user-facing claims or accepted provenance.

`verification.provenance` links claim hash, source/evidence IDs, exact span, source hash,
tool/version and verdict. The cited body must contain the canonical assertion at that span.
Trajectory stores control information and hashes, not raw question/evidence bodies.
The separate replay export **does contain arguments and observations**: publish synthetic
bundles only. Replay verifies configuration/observation integrity and reruns verification with
zero external calls. Hashes detect accidental modification, not malicious recomputation.
No stochastic LLM reproducibility is claimed. Prompt hashes do not apply: zero LLM calls.

## Paired synthetic evaluation

[Dataset](../examples/evaluation-cases.json), [runner](../src/harness/evaluation.py),
[results](../examples/paired-evaluation.json).
24 cases = 12 categories × 2 fictional-subject/value variants. Both arms receive the same
fixtures, initial tools and deterministic candidate generator, including injected faults.
Baseline omits verification/retry; Harness can use predeclared fallback calls. This is a
**verification/recovery ablation**, not a comparison with a modern LLM service. Cases were
authored alongside code: no independent holdout, blinded judge or domain accuracy benchmark.

- Task success: oracle subject/metric/unit/value, or expected abstention. The oracle is
  separate from verifier output; abstention on an answerable case is failure.
- Unsafe answer: nonempty answer failing the case oracle, including scope/citation failures;
  not a synonym for factual hallucination rate.
- Calls: actual registry invocations, including failures/retries.
- Latency: one monotonic local measurement per arm, including injected timeouts; no
  significance, speedup or cross-machine performance claim.
- Recovery: six timeout/error/irrelevant-retry cases complete. Configured fallbacks are
  not autonomous discovery, self-improvement or learning.

Recorded task success is 8/24 vs 24/24, unsafe answers 12 vs 0, average calls 1.083 vs 1.333.
Measured latencies are in the JSON artifact. Reliability on designed failures costs more calls
and time. Conformance and evaluation reuse these cases and are not independent evidence.

## Test categories

On 2026-10-08, local validation passed **76 methods**: the preserved 57-method baseline
plus 11 actual-core export/integrity tests, 5 subprocess CLI/output tests and 3 HTML-link tests.
The 24 conformance scenarios are exercised inside one method, not counted as 24 extra methods.
Browser checks and historical Docker execution evidence are separate from that count.

The counts below describe the **2026-10-02, 57-method baseline**. They are not a claim
about the current revision's final count; use the commit-specific CI and [validation record](validation.md).

| Category | Executable evidence |
|---|---|
| Unit | `test_harness_unit.py`: 16 methods |
| Integration / regression | `test_harness_integration.py`: 11 methods including guide-vs-area regression |
| Conformance | One further method loops over 24 synthetic scenarios |
| Protocol / sandbox contract | `test_harness_protocol.py`: 6 methods; subprocess stdio and command contracts |
| Legacy / repository quality | Original 23 methods |
| Docker integration | Separate opt-in command; not counted in 57 default methods |
| Benchmark | No independent model/domain benchmark; paired synthetic evaluation only |

Private selected regression: **229 passed on 2026-10-02**, including 20 private synthetic
conformance cases. Not added to public counts and not reproducible through public CI.

## Sandbox and scientific slice

Approve/install a local Python 3.11 image, inspect its immutable image ID, then run:

```sh
python3 -m src.harness.docker_smoke --image sha256:YOUR_APPROVED_LOCAL_IMAGE_ID
```

Replace the placeholder with the actual 64-character local image ID. No image pull or host
execution fallback. [Actual validation](../examples/docker-validation.json) records the used ID,
non-root UID, read-only root, writable isolated scratch, blocked networking, deadline,
output cap, nonzero exit and cleanup. CPU 0.5, memory/swap 128 MiB, pids 32, dropped capabilities,
no-new-privileges, no host bind mounts. Resource flags are tested, not stress benchmarked.

Dataset → isolated statistics → dataset/result/image-linked artifact → independent
`fsum`-based recomputation → evidence rows → claim/span verifier. Dataset [2,4,6,8,10]
produces mean 6 and sample variance 10 with accepted provenance. MCP exposes the trusted
in-process tool; the isolated variant requires explicit `compute:isolated` registration.
Docker daemon access is privileged and containers share a kernel. This is not a complete
hostile multi-tenant sandbox. Thread-offloaded calls finish their own deadline/cleanup even
if the calling coroutine is cancelled; cancellation is not immediate container termination.

## Minimal real MCP

`python3 -m src.harness.mcp_adapter` uses newline-delimited JSON-RPC stdio: initialize,
initialized notification, ping, tools/list and tools/call. Tests launch a child process and
call numerical analysis over pipes. No stdout diagnostic chatter. The subset follows
[stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)
and [tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
No full conformance certification, independent client interoperability, HTTP/auth,
cancellation notifications or pagination. Schema validation supports the types, object fields,
array bounds and string lengths used by this registry, not the entire JSON Schema vocabulary.
