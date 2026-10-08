"use strict";

(() => {
  const data = window.CORE_EVIDENCE;
  const byId = id => document.getElementById(id);
  const array = value => Array.isArray(value) ? value : [];
  const json = value => JSON.stringify(value, null, 2);
  const present = value => value === undefined || value === null ? "—" : String(value);
  const sourceRoot = "https://github.com/YeongjoonKim/reliable-domain-agent-harness";
  const signalLabels = {
    retrieval_success: "검색 결과의 존재",
    evidence_relevance: "정보 요구와의 적합성",
    claim_support: "주장 값의 근거 지지",
    citation_valid: "정확한 인용 범위와 hash"
  };
  let selectedScenario = null;
  let selectedAttempt = 0;
  let selectedEvent = 0;
  let activeView = "verification";

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = present(value);
    return node;
  }

  function text(id, value) { byId(id).textContent = present(value); }

  function badge(value, tone) {
    const node = element("span", "badge", value);
    if (tone) node.dataset.tone = tone;
    return node;
  }

  function verdict(report) {
    return report && typeof report.accepted === "boolean" ? (report.accepted ? "ACCEPT" : "REJECT") : "—";
  }

  function reportTone(report) {
    return report && typeof report.accepted === "boolean" ? (report.accepted ? "good" : "bad") : "";
  }

  function empty(container, message) { container.append(element("p", "empty-note", message)); }

  function keyValues(values, className = "key-value-grid") {
    const list = element("dl", className);
    Object.entries(values).forEach(([name, value]) => {
      const group = element("div");
      group.append(element("dt", "", name), element("dd", "", typeof value === "object" && value !== null ? json(value) : present(value)));
      list.append(group);
    });
    return list;
  }

  function rawDetails(label, payload) {
    const details = element("details", "raw-detail");
    details.append(element("summary", "", label), element("pre", "", json(payload)));
    return details;
  }

  function records() { return array(selectedScenario && selectedScenario.run.replay_bundle.records); }
  function currentRecord() { return records()[selectedAttempt]; }

  // Runtime appends EXECUTING once for each executed attempt; no state is added.
  function eventAttempts(events) {
    let attempt = -1;
    return events.map(event => {
      if (event.state === "EXECUTING") attempt += 1;
      return Math.max(0, Math.min(attempt, records().length - 1));
    });
  }

  function setView(view, focus = false) {
    activeView = view;
    document.querySelectorAll("[role=tab][data-view]").forEach(tab => {
      const selected = tab.dataset.view === view;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
      byId("panel-" + tab.dataset.view).hidden = !selected;
      if (selected && focus) tab.focus();
    });
  }

  function renderTimeline() {
    const events = array(selectedScenario.run.trajectory);
    const associations = eventAttempts(events);
    const list = byId("timeline");
    list.replaceChildren();
    text("event-count", events.length + " events");
    events.forEach((event, index) => {
      const item = element("li");
      const button = element("button");
      button.type = "button";
      button.dataset.eventIndex = String(index);
      button.dataset.attemptIndex = String(associations[index]);
      button.setAttribute("aria-pressed", String(index === selectedEvent));
      const heading = element("span", "event-title");
      heading.append(element("span", "", event.state), element("span", "event-sequence", "#" + present(event.sequence)));
      button.append(heading);
      const note = event.tool_name ? event.tool_name + " · " + present(event.error_type) : event.retry_reason || event.verification || event.error_type;
      if (note) {
        const detail = element("span", "event-note", note);
        if (event.verification === "REJECT" || event.error_type === "abstained") detail.dataset.tone = "bad";
        button.append(detail);
      }
      button.addEventListener("click", () => {
        selectedEvent = index;
        selectedAttempt = associations[index];
        updateSelection();
      });
      button.addEventListener("keydown", key => {
        const buttons = Array.from(list.querySelectorAll("button"));
        let next;
        if (key.key === "ArrowDown" || key.key === "ArrowRight") next = (index + 1) % buttons.length;
        if (key.key === "ArrowUp" || key.key === "ArrowLeft") next = (index + buttons.length - 1) % buttons.length;
        if (key.key === "Home") next = 0;
        if (key.key === "End") next = buttons.length - 1;
        if (next !== undefined) { key.preventDefault(); buttons[next].click(); buttons[next].focus(); }
      });
      item.append(button);
      list.append(item);
    });
  }

  function renderAttempts() {
    const group = byId("attempt-select");
    group.replaceChildren();
    records().forEach((record, index) => {
      const button = element("button", "", "Attempt " + present(record.attempt));
      button.type = "button";
      button.dataset.attemptIndex = String(index);
      button.setAttribute("aria-pressed", String(index === selectedAttempt));
      button.addEventListener("click", () => {
        selectedAttempt = index;
        const events = array(selectedScenario.run.trajectory);
        const associations = eventAttempts(events);
        const verifyIndex = events.findIndex((event, eventIndex) => event.state === "VERIFYING" && associations[eventIndex] === index);
        if (verifyIndex !== -1) selectedEvent = verifyIndex;
        updateSelection();
      });
      group.append(button);
    });
  }

  function renderSignals(report) {
    const signals = byId("verification-signals");
    signals.replaceChildren();
    Object.entries(report && report.signals || {}).forEach(([name, value]) => {
      const signal = element("div", "signal");
      signal.dataset.signal = name;
      const label = element("div");
      label.append(element("code", "", name));
      if (signalLabels[name]) label.append(element("span", "signal-description", signalLabels[name]));
      signal.append(label, badge(present(value), value === true ? "good" : value === false ? "bad" : ""));
      signals.append(signal);
    });
    const reasons = byId("rejection-reasons");
    reasons.replaceChildren();
    const entries = array(report && report.reasons);
    reasons.dataset.tone = reportTone(report);
    if (entries.length) {
      reasons.append(element("strong", "", "Rejection reasons"));
      const list = element("ul", "reason-list");
      entries.forEach(reason => list.append(element("li", "", reason)));
      reasons.append(list);
    } else reasons.append(element("span", "", report && report.accepted ? "검증 결과: 거부 사유 없음" : "기록된 거부 사유 없음"));
  }

  function renderObservations(record) {
    const container = byId("tool-observations");
    container.replaceChildren();
    const observations = array(record && record.observations);
    if (!observations.length) empty(container, "이 시도에 기록된 도구 관측이 없습니다.");
    observations.forEach(observation => {
      const card = element("article", "observation-card");
      const heading = element("div", "observation-title");
      heading.append(element("code", "", observation.tool), badge(observation.status, observation.status === "ok" ? "good" : "warning"));
      card.append(heading, element("p", "observation-meta", "version " + present(observation.tool_version) + " · " + array(observation.evidence).length + " evidence records · observed latency " + present(observation.latency_ms) + " ms"));
      card.append(rawDetails("도구 응답과 input / output hashes", observation));
      container.append(card);
    });
  }

  function spanBody(body, start, end, className, markClass) {
    const container = element("pre", className);
    const raw = typeof body === "string" ? body : "";
    const characters = Array.from(raw); // Python offsets count Unicode code points.
    if (!Number.isInteger(start) || !Number.isInteger(end) || start < 0 || start >= end || end > characters.length) {
      container.textContent = raw;
      return {node: container, valid: false};
    }
    const mark = element("mark", markClass, characters.slice(start, end).join(""));
    mark.dataset.start = String(start);
    mark.dataset.end = String(end);
    mark.setAttribute("aria-label", "원문 인용 범위 [" + start + ", " + end + ")");
    container.append(document.createTextNode(characters.slice(0, start).join("")), mark, document.createTextNode(characters.slice(end).join("")));
    return {node: container, valid: true};
  }

  function addSpan(card, label, row, start, end, className, markClass, status) {
    const heading = element("div", "span-heading");
    heading.append(element("span", "", label + " [" + present(start) + ", " + present(end) + ")"));
    if (status) heading.append(badge(status.label, status.tone));
    const range = spanBody(row.body, start, end, className, markClass);
    card.append(heading, range.node);
    if (!range.valid) card.append(element("p", "span-error", "기록된 범위가 원문에 유효하지 않아 임의로 자르지 않고 전체 원문을 표시합니다."));
  }

  function renderEvidence(record) {
    const container = byId("evidence-details");
    container.replaceChildren();
    const report = record && record.verification;
    const claims = array(record && record.claims);
    let count = 0;
    array(record && record.observations).forEach(observation => {
      array(observation.evidence).forEach(row => {
        count += 1;
        const card = element("article", "evidence-card");
        card.dataset.evidenceId = row.evidence_id;
        card.append(element("h5", "evidence-heading", present(row.source_id) + " / " + present(row.evidence_id)));
        card.append(element("p", "evidence-caption", present(row.subject) + " · " + present(row.metric) + " · " + present(row.value) + " " + present(row.unit) + " · " + present(row.observed)));
        addSpan(card, "Evidence source span", row, row.start, row.end, "source-body", "span-source");
        const matching = claims.filter(claim => claim.evidence_id === row.evidence_id);
        matching.forEach(claim => {
          const provenance = array(report && report.provenance).find(link => link.evidence_id === row.evidence_id &&
            link.source_id === row.source_id && array(link.evidence_span)[0] === claim.start && array(link.evidence_span)[1] === claim.end);
          const accepted = Boolean(report && report.accepted && provenance);
          // A report-level invalid_citation alone cannot identify every claim.
          const differs = claim.start !== row.start || claim.end !== row.end;
          const invalid = array(report && report.reasons).includes("invalid_citation") && differs && !provenance;
          const status = accepted ? {label: "ACCEPTED CITATION", tone: "good"} : invalid ? {label: "INVALID CITATION", tone: "bad"} : {label: "CANDIDATE · NOT ACCEPTED", tone: "warning"};
          addSpan(card, "Claim citation span", row, claim.start, claim.end, "claim-body", accepted ? "span-accepted" : invalid ? "span-invalid" : "span-candidate", status);
          card.append(rawDetails("후보 주장 / Candidate claim JSON", claim));
        });
        if (!matching.length) card.append(element("p", "panel-caption", "이 근거에 연결된 후보 주장이 없습니다."));
        card.append(keyValues({source_id: row.source_id, source_hash: row.source_hash, tool: observation.tool, tool_version: observation.tool_version}, "hash-list"));
        container.append(card);
      });
    });
    if (!count) empty(container, "이 시도에는 표시할 근거 원문이 없습니다.");
  }

  function claimCards(container, claims, message) {
    container.replaceChildren();
    container.dataset.count = String(claims.length);
    if (!claims.length) empty(container, message);
    claims.forEach(claim => {
      const card = element("article", "claim-card");
      card.append(element("p", "claim-line", present(claim.subject) + " / " + present(claim.metric) + " = " + present(claim.value) + " " + present(claim.unit)));
      card.append(element("pre", "", json(claim)));
      container.append(card);
    });
  }

  function renderClaims(record) {
    claimCards(byId("accepted-claims"), array(selectedScenario.run.claims), "최종 채택된 주장이 없습니다. 실패 시도의 후보는 최종 주장과 구분합니다.");
    claimCards(byId("attempt-claims"), array(record && record.claims), "이 시도에서 생성한 후보 주장이 없습니다.");
    const container = byId("provenance");
    container.replaceChildren();
    const links = array(record && record.verification && record.verification.provenance);
    container.dataset.count = String(links.length);
    if (!links.length) empty(container, "이 시도에는 승인된 provenance 연결이 없습니다.");
    links.forEach(link => {
      const card = element("article", "provenance-card");
      card.append(badge(link.verification_result, link.verification_result === "PASS" ? "good" : ""), keyValues(link, "hash-list"));
      container.append(card);
    });
  }

  function renderReplay() {
    const replay = selectedScenario.replay;
    const container = byId("replay-result");
    container.replaceChildren();
    if (!replay) empty(container, "이 artifact에 Replay 결과가 없습니다.");
    else {
      const heading = element("div", "replay-summary");
      heading.append(element("strong", "", replay.mode), badge("external_calls = " + present(replay.external_calls), replay.external_calls === 0 ? "good" : ""));
      container.append(heading);
      array(replay.reports).forEach((report, index) => {
        const card = element("article", "replay-report");
        card.append(element("span", "small-label", "SAVED ATTEMPT " + present(records()[index] && records()[index].attempt)), badge(verdict(report), reportTone(report)));
        if (array(report.reasons).length) {
          const list = element("ul", "reason-list");
          report.reasons.forEach(reason => list.append(element("li", "", reason)));
          card.append(list);
        }
        card.append(rawDetails("재실행한 검증 결과 JSON", report));
        container.append(card);
      });
      container.append(rawDetails("Replay 원본 JSON", replay));
    }
    const bundle = selectedScenario.run.replay_bundle;
    byId("configuration-hashes").replaceChildren(keyValues({schema_version: bundle.schema_version,
      plan_hash: bundle.plan_hash, policy_hash: bundle.policy_hash, registry_hash: bundle.registry_hash,
      integrity_hash: bundle.integrity_hash}, "hash-list"));
  }

  function renderPlan() {
    const bundle = selectedScenario.run.replay_bundle;
    const needs = byId("need-details");
    needs.replaceChildren();
    array(bundle.needs).forEach(need => {
      const card = element("article", "need-card");
      card.append(keyValues(need));
      needs.append(card);
    });
    if (!array(bundle.needs).length) empty(needs, "기록된 Information Need가 없습니다.");
    const plan = byId("plan-details");
    plan.replaceChildren();
    array(bundle.plan).forEach((calls, index) => {
      const card = element("article", "plan-group");
      card.append(element("span", "small-label", "PLAN ATTEMPT " + index), element("pre", "", json(calls)));
      plan.append(card);
    });
    text("policy-details", json(bundle.policy));
  }

  function linkValue(value) {
    if (typeof value === "string") return value;
    if (value && typeof value === "object") return value.href || value.url || value.path;
    return null;
  }

  function setLink(id, value, fallback) {
    const href = linkValue(value) || fallback;
    const anchor = byId(id);
    if (typeof href === "string" && !/^(?:javascript|data|vbscript):/i.test(href.trim())) {
      anchor.setAttribute("href", href);
      anchor.hidden = false;
    } else anchor.hidden = true;
  }

  function updateSelection() {
    document.querySelectorAll("#timeline button").forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.eventIndex) === selectedEvent)));
    document.querySelectorAll("#attempt-select button").forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.attemptIndex) === selectedAttempt)));
    text("event-detail", json(array(selectedScenario.run.trajectory)[selectedEvent]));
    const record = currentRecord();
    const report = record && record.verification;
    text("attempt-title", record ? "Attempt " + present(record.attempt) + " / verification" : "시도별 검증 기록 없음");
    text("attempt-verdict", verdict(report));
    byId("attempt-verdict").dataset.tone = reportTone(report);
    renderSignals(report);
    renderObservations(record);
    renderEvidence(record);
    renderClaims(record);
  }

  function selectScenario(id) {
    const scenario = data.scenarios.find(item => item.id === id);
    if (!scenario || !scenario.run || !scenario.run.replay_bundle) return;
    selectedScenario = scenario;
    selectedAttempt = 0;
    selectedEvent = 0;
    byId("scenario").value = scenario.id;
    text("case-id", "RECORDED CASE / " + present(scenario.case_id));
    text("scenario-title", scenario.title);
    text("scenario-description", scenario.description);
    const run = scenario.run;
    text("run-state", run.state);
    byId("run-state").dataset.tone = run.state === "FAILED" || run.state === "CANCELLED" ? "bad" : "good";
    const events = array(run.trajectory);
    const last = events[events.length - 1];
    text("run-state-note", last && last.error_type === "abstained" ? "검증되지 않은 주장 채택 보류" : "원본 Runtime의 최종 상태");
    text("tool-calls", run.calls);
    text("verification-verdict", verdict(run.verification));
    byId("verification-verdict").dataset.tone = reportTone(run.verification);
    text("replay-external-calls", scenario.replay && scenario.replay.external_calls);
    text("run-id", "run_id / " + present(events[0] && events[0].run_id));
    const links = scenario.links || {};
    setLink("scenario-source", links.source, sourceRoot + "/blob/main/src/harness/runtime.py");
    setLink("scenario-execution", links.execution, "core-evidence.json");
    setLink("scenario-test", links.test, sourceRoot + "/blob/main/tests/test_harness_integration.py");
    setLink("scenario-ci", links.ci || data.scope && data.scope.ci_url, sourceRoot + "/actions/workflows/ci.yml");
    renderTimeline();
    renderAttempts();
    updateSelection();
    renderReplay();
    renderPlan();
    setView(activeView);
  }

  function renderEvaluation() {
    const container = byId("evaluation-results");
    container.replaceChildren();
    const evaluation = data.evaluation || {};
    Object.entries(evaluation.summary || {}).forEach(([arm, result]) => {
      const card = element("article", "evaluation-card");
      card.dataset.arm = arm;
      card.append(element("span", "small-label", arm), element("strong", "", present(result.task_success) + " / " + present(result.cases)), element("p", "", "synthetic task outcomes"));
      card.append(element("p", "", "unsafe_answers = " + present(result.unsafe_answers)));
      container.append(card);
    });
    if (!container.children.length) empty(container, "이 artifact에 합성 평가 요약이 없습니다.");
  }

  document.querySelectorAll("[role=tab][data-view]").forEach((tab, index, tabs) => {
    tab.addEventListener("click", () => setView(tab.dataset.view));
    tab.addEventListener("keydown", event => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); setView(tabs[next].dataset.view, true); }
    });
  });

  if (!data || !Array.isArray(data.scenarios) || !data.scenarios.length) {
    text("data-status", "실행 artifact가 없습니다. scripts/export_demo.py로 생성한 core-evidence.js가 필요합니다.");
    byId("data-status").classList.add("error-note");
    byId("scenario").disabled = true;
    return;
  }
  const picker = byId("scenario");
  picker.replaceChildren();
  data.scenarios.forEach((scenario, index) => {
    const option = element("option", "", String(index + 1).padStart(2, "0") + " / " + scenario.title);
    option.value = scenario.id;
    picker.append(option);
  });
  picker.addEventListener("change", () => selectScenario(picker.value));
  text("data-status", data.scenarios.length + " recorded scenarios · schema " + present(data.schema_version));
  text("artifact-generated", "generated_at / " + present(data.generated_at));
  text("artifact-scope", typeof data.scope === "string" ? data.scope : json(data.scope));
  renderEvaluation();
  selectScenario(data.scenarios[0].id);
})();
