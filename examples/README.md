# Synthetic example

Structured requests use session, subject, needs and optional mode. The fictional glassleaf metrics are growth and moisture. Summary mode reuses the same scope without new calls.

Run `python3 -m src.sample_agent` from the repository root.
Default examples use no network, credentials or GPU.

The Public Core is separate from that legacy example. Its normal commands write
`outputs/recovery.json`, `outputs/paired-evaluation.json` and `outputs/evaluation-cases.json`.
The tracked files here are reviewed historical snapshots; explicitly pass
`--update-examples` to the relevant `src.harness.demo` or `src.harness.evaluation`
command to replace them. Default runs do not refresh these files.

The [Core Evidence Explorer](../demo/index.html) uses its own generated
[execution artifact](../demo/core-evidence.json). See the
[export and check commands](../docs/public-core.md#run-and-explore).
