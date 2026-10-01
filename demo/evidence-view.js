"use strict";
// 설명 카드는 정적이며 이 영역만 공개 Python 실행 snapshot을 표시한다.
function showEvidence() {
  const snapshot = window.PUBLIC_EVIDENCE;
  const mode = document.querySelector("#scenario").value;
  const selected = document.querySelector('[role="tab"][aria-selected="true"]').dataset.view;
  const result = snapshot.cases[mode];
  const byView = {
    overview: {status: result.status, answer: result.answer, sources: result.sources},
    tools: {calls: result.tool_calls, tool_status: result.tool_status || "No new tool call"},
    verification: {probe_checks: snapshot.probe_checks, claims: result.claims || "Reused verified answer"},
    evaluation: {probe_checks: snapshot.probe_checks, scope: "Five executed contract probes; not model accuracy"},
    trace: {events: result.events, sources: result.sources},
    reproducibility: {artifact_sha256: result.artifact_sha256 || "Summary reuses prior answer", scope: snapshot.scope}
  };
  document.querySelector("#execution-evidence").textContent = JSON.stringify(byView[selected], null, 2);
}
document.querySelector("#scenario").addEventListener("change", showEvidence);
document.querySelectorAll('[role="tab"]').forEach(tab => {
  tab.addEventListener("click", showEvidence);
  tab.addEventListener("keydown", showEvidence);
});
showEvidence();
