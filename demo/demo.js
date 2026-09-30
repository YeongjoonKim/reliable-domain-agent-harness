"use strict";

// 화면 데이터는 운영 기록이 아닌 독립적으로 작성한 합성 시나리오다.
const scenarios = {
  complete: {status: "SUPPORTED · SYNTHETIC", calls: "2 mock calls", evidence: "2 fixture references",
    steps: ["Validate fictional scope", "Plan two unique lookups", "Collect two mock facts",
      "Check values and scope", "Return a supported synthetic answer"]},
  partial: {status: "PARTIAL · SYNTHETIC", calls: "2 attempted mock calls", evidence: "1 fixture reference",
    steps: ["Validate fictional scope", "Start independent mock lookups", "Record one timeout",
      "Keep the supported sibling result", "Expose the unresolved requirement"]},
  summary: {status: "REUSED · SYNTHETIC", calls: "0 new calls", evidence: "Existing fixture references only",
    steps: ["Validate summary mode", "Read the exact fictional session and subject",
      "Reuse the prior verified text", "Add no new sources", "Return the stored summary"]}
};
const views = {
  overview: {title:"Boundaries before answers", kicker:"DOMAIN-BOUNDED RUNTIME",
    summary:"A readable reference architecture, not a replica of a private system.",
    cards:[["Contract","IMPLEMENTED","Structured input and a finite budget."],
      ["Evidence","SYNTHETIC","Values have scope, units and fixture references."],
      ["Interpretation","PROPOSED","Natural-language planning needs its own evaluation."]]},
  tools: {title:"Observe outcomes, not just payloads", kicker:"RUNTIME & TOOLS",
    summary:"A timeout and an empty result mean different things.",
    cards:[["Reference lookup","PARTIAL","One invented metric, no real database."],
      ["Observation lookup","PARTIAL","Independent execution preserves partial results."],
      ["External connectors","PROPOSED","No web, vector or graph service is connected."]]},
  verification: {title:"Citations are necessary, not sufficient", kicker:"VERIFICATION",
    summary:"This example checks exact fixture correspondence, not universal truth.",
    cards:[["Scope","CHECKED","The subject must match the evidence."],
      ["Value and unit","CHECKED","A changed fact is rejected."],
      ["Semantic truth","NOT GUARANTEED","No model judge or real-world fact checker."]]},
  evaluation: {title:"Test failures before calling them success", kicker:"EVALUATION",
    summary:"The Python tests exercise contracts. This UI does not run those tests.",
    cards:[["Failure injection","UNIT TESTS","Empty, timeout and error paths."],
      ["Memory boundary","UNIT TESTS","Different sessions and subjects do not share results."],
      ["Deployment review","PROPOSED","A human decision, not autonomous policy learning."]]},
  trace: {title:"What happened? What supported it?", kicker:"TRACE & EVIDENCE",
    summary:"The sequence below is illustrative logical order, not wall-clock performance.",
    cards:[["Trace","LOGICAL ORDER","No invented production timestamps."],
      ["Provenance","FIXTURE LINKS","Limited to claim-to-synthetic-record correspondence."],
      ["Replay","PROPOSED","Hashes alone do not restore an external environment."]]},
  reproducibility: {title:"Make the missing conditions visible", kicker:"REPRODUCIBILITY",
    summary:"A deterministic toy fixture is not the same as a reproducible live AI service.",
    cards:[["Synthetic inputs","AVAILABLE","Authored fixtures and stable artifact digests."],
      ["Model revision","NOT APPLICABLE","No language model is loaded here."],
      ["Full live replay","PROPOSED","Would require frozen tools, evidence and memory."]]}
};
let currentView = "overview";
const tabs = Array.from(document.querySelectorAll("[role=tab]"));
function render() {
  const scenario = scenarios[document.querySelector("#scenario").value];
  const view = views[currentView];
  document.querySelector("#scenario-status").textContent = scenario.status;
  document.querySelector("#panel-kicker").textContent = view.kicker;
  document.querySelector("#panel-title").textContent = view.title;
  document.querySelector("#panel-summary").textContent = view.summary;
  document.querySelector("#panel").setAttribute("aria-labelledby", "tab-" + currentView);
  const cards = document.querySelector("#cards");
  cards.replaceChildren();
  view.cards.forEach(([title, tag, description]) => {
    const card = document.createElement("article");
    card.className = "card";
    const badge = document.createElement("span"); badge.className = "tag"; badge.textContent = tag;
    const heading = document.createElement("h3"); heading.textContent = title;
    const text = document.createElement("p"); text.textContent = description;
    card.append(badge, heading, text); cards.append(card);
  });
  document.querySelector("#detail-title").textContent = scenario.calls + " · " + scenario.evidence;
  const steps = document.querySelector("#steps"); steps.replaceChildren();
  scenario.steps.forEach(value => { const li=document.createElement("li"); li.textContent=value; steps.append(li); });
  tabs.forEach(tab => { const selected=tab.dataset.view===currentView;
    tab.setAttribute("aria-selected", String(selected)); tab.tabIndex=selected?0:-1; });
}
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => { currentView=tab.dataset.view; render(); });
  tab.addEventListener("keydown", event => {
    let next;
    if(event.key==="ArrowRight") next=(index+1)%tabs.length;
    if(event.key==="ArrowLeft") next=(index+tabs.length-1)%tabs.length;
    if(event.key==="Home") next=0;
    if(event.key==="End") next=tabs.length-1;
    if(next!==undefined) {event.preventDefault(); tabs[next].click(); tabs[next].focus();}
  });
});
document.querySelector("#scenario").addEventListener("change", render);
render();
