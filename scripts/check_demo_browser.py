"""선택 사항: 설치된 Chrome과 표준 라이브러리로 실제 정적 UI를 검사한다.

로컬 임시 HTTP 서버만 사용한다. 원본 HTML에 같은 출처의 검사 스크립트 두 개를
메모리에서 삽입하며 저장소 파일·CSP·실행 산출물은 변경하지 않는다.
"""
import argparse
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "/repository-preview"
BOOT = r"""
window.__probeErrors = [];
window.addEventListener('error', e => window.__probeErrors.push(String(e.message || e.type)));
window.addEventListener('unhandledrejection', e => window.__probeErrors.push(String(e.reason)));
window.addEventListener('securitypolicyviolation', e => window.__probeErrors.push('CSP: ' + e.violatedDirective));
"""
PROBE = r"""
(() => {
  const result = {page: location.pathname, actual_viewport: {width:innerWidth, height:innerHeight},
                  scenarios: [], links: [], errors: []};
  const assert = (ok, message) => {if (!ok) throw new Error(message);};
  const get = selector => {const node = document.querySelector(selector);
    assert(node, 'Missing ' + selector); return node;};
  const text = selector => get(selector).textContent;
  try {
    if (location.pathname.endsWith('legacy.html')) {
      for (const value of ['complete', 'partial', 'summary']) {
        get('#scenario').value = value;
        get('#scenario').dispatchEvent(new Event('change', {bubbles:true}));
        assert(text('#scenario-status').trim(), 'Legacy scenario missing status');
      }
      for (const tab of document.querySelectorAll('[role=tab]')) {
        tab.click(); assert(tab.getAttribute('aria-selected') === 'true', 'Legacy tab');
      }
      result.legacy_scenarios = 3;
    } else {
      const data = window.CORE_EVIDENCE;
      assert(data && Array.isArray(data.scenarios), 'Core artifact not loaded');
      const required = ['valid_evidence', 'retry_recovery', 'conflicting_evidence',
                        'invalid_citation_span', 'configuration_evidence_replay'];
      for (const id of required) assert(data.scenarios.some(s => s.id === id), 'Missing scenario ' + id);
      assert(get('#scenario').options.length === data.scenarios.length, 'Scenario options');
      for (const scenario of data.scenarios) {
        get('#scenario').value = scenario.id;
        get('#scenario').dispatchEvent(new Event('change', {bubbles:true}));
        assert(text('#run-state').includes(scenario.run.state), scenario.id + ' state');
        assert(Number(text('#tool-calls')) === scenario.run.calls, scenario.id + ' calls');
        assert(Number(text('#replay-external-calls')) === scenario.replay.external_calls, 'Replay calls');
        const verdict = scenario.run.verification.accepted ? 'ACCEPT' : 'REJECT';
        assert(text('#verification-verdict').includes(verdict), scenario.id + ' final verification');
        const timeline = [...document.querySelectorAll('#timeline button[data-event-index]')];
        assert(timeline.length === scenario.run.trajectory.length, scenario.id + ' timeline length');
        timeline.forEach((button, index) => {
          button.click();
          assert(JSON.stringify(JSON.parse(text('#event-detail'))) ===
            JSON.stringify(scenario.run.trajectory[index]), scenario.id + ' raw event ' + index);
        });
        const records = scenario.run.replay_bundle.records;
        const attempts = [...document.querySelectorAll('#attempt-select [data-attempt-index]')];
        assert(attempts.length === records.length, scenario.id + ' attempt count');
        let spans = 0;
        records.forEach((record, index) => {
          attempts[index].click();
          assert(text('#attempt-verdict').includes(record.verification.accepted ? 'ACCEPT' : 'REJECT'),
            scenario.id + ' attempt verdict ' + index);
          assert(Number(get('#accepted-claims').dataset.count) === scenario.run.claims.length, 'Accepted claim count');
          assert(Number(get('#attempt-claims').dataset.count) === record.claims.length, 'Candidate claim count');
          assert(Number(get('#provenance').dataset.count) === record.verification.provenance.length, 'Provenance count');
          for (const [name, value] of Object.entries(record.verification.signals))
            assert(get('#verification-signals [data-signal="' + name + '"] .badge').textContent === String(value),
              'Wrong verification signal ' + name);
          const renderedClaims = [...document.querySelectorAll('#accepted-claims pre')].map(n => JSON.parse(n.textContent));
          assert(JSON.stringify(renderedClaims) === JSON.stringify(scenario.run.claims), 'Accepted claim mapping');
          const candidates = [...document.querySelectorAll('#attempt-claims pre')].map(n => JSON.parse(n.textContent));
          assert(JSON.stringify(candidates) === JSON.stringify(record.claims), 'Candidate mapping');
          for (const provenance of record.verification.provenance)
            for (const value of [provenance.claim_hash, provenance.source_hash, provenance.tool_version])
              assert(text('#provenance').includes(value), 'Missing actual provenance');
          if (!record.verification.accepted)
            assert(!document.querySelector('#evidence-details .span-accepted'), 'Rejected citation shown as accepted');
          for (const reason of record.verification.reasons)
            assert(text('#rejection-reasons').includes(reason), 'Missing rejection ' + reason);
          for (const observation of record.observations) {
            assert(text('#tool-observations').includes(observation.tool), 'Missing tool');
            assert(text('#tool-observations').includes(observation.tool_version), 'Missing tool version');
            for (const evidence of observation.evidence) {
              const cards = [...document.querySelectorAll('#evidence-details .evidence-card')];
              const card = cards.find(c => c.dataset.evidenceId === evidence.evidence_id);
              assert(card, 'Missing evidence ' + evidence.evidence_id);
              assert(card.querySelector('.source-body').textContent === evidence.body, 'Changed source body');
              const sourceMark = card.querySelector('.source-body mark');
              assert(sourceMark && Number(sourceMark.dataset.start) === evidence.start &&
                Number(sourceMark.dataset.end) === evidence.end, 'Source offsets differ from record');
              const matching = record.claims.filter(c => c.evidence_id === evidence.evidence_id);
              const claimBodies = [...card.querySelectorAll('.claim-body')];
              assert(claimBodies.length === matching.length, 'Candidate source mapping');
              claimBodies.forEach((body, claimIndex) => {
                const mark = body.querySelector('mark'), claim = matching[claimIndex];
                assert(body.textContent === evidence.body, 'Changed candidate source body');
                assert(mark && Number(mark.dataset.start) === claim.start && Number(mark.dataset.end) === claim.end,
                  'Claim offsets differ from record');
              });
              for (const mark of card.querySelectorAll('mark')) {
                const start = Number(mark.dataset.start), end = Number(mark.dataset.end);
                assert(Number.isInteger(start) && Number.isInteger(end), 'Missing span offsets');
                assert(mark.textContent === Array.from(evidence.body).slice(start, end).join(''), 'Wrong exact span');
                spans++;
              }
            }
          }
        });
        for (const tab of document.querySelectorAll('[role=tab]')) {
          tab.click(); assert(tab.getAttribute('aria-selected') === 'true', 'Core tab');
        }
        for (const id of ['scenario-source', 'scenario-execution', 'scenario-test', 'scenario-ci']) {
          const link = get('#' + id); assert(link.getAttribute('href'), 'Missing ' + id);
          result.links.push(link.href);
        }
        for (const name of ['source', 'execution', 'test'])
          assert(get('#scenario-' + name).href === new URL(scenario.links[name], location.href).href,
            'Wrong artifact link ' + name);
        assert(get('#scenario-ci').href === data.scope.ci_url, 'Wrong CI link');
        for (const name of ['plan_hash', 'policy_hash', 'registry_hash', 'integrity_hash'])
          assert(text('#configuration-hashes').includes(scenario.run.replay_bundle[name]), 'Missing configuration ' + name);
        assert(spans > 0, scenario.id + ' no exact evidence spans');
        result.scenarios.push({id: scenario.id, state: scenario.run.state,
          trajectory_events: timeline.length, attempts: records.length, spans,
          replay_external_calls: scenario.replay.external_calls});
      }
      // Arrow navigation must move to and select another detail tab.
      const tabs = [...document.querySelectorAll('[role=tab]')];
      tabs[0].click(); tabs[0].focus();
      tabs[0].dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowRight', bubbles:true}));
      assert(tabs[1].getAttribute('aria-selected') === 'true', 'Keyboard tab navigation');
      assert(document.documentElement.scrollWidth <= window.innerWidth + 1, 'Viewport overflows');
    }
    result.links.push(...[...document.querySelectorAll('a[href]')].map(a => a.href));
    const outside = performance.getEntriesByType('resource').filter(entry =>
      new URL(entry.name).origin !== location.origin);
    assert(!outside.length, 'Unexpected external resource request');
  } catch (error) {result.errors.push(String(error.stack || error));}
  result.errors.push(...window.__probeErrors);
  result.ok = !result.errors.length;
  const output = document.createElement('pre'); output.id = 'browser-probe-result';
  output.textContent = JSON.stringify(result); document.body.append(output);
})();
"""


class ProbeServer(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if not path.startswith(PREFIX + "/"):
            self.send_error(404)
            return
        path = path[len(PREFIX):]
        if path.endswith("/__probe-boot.js"):
            return self.send_bytes(BOOT.encode(), "text/javascript")
        if path.endswith("/__probe-check.js"):
            return self.send_bytes(PROBE.encode(), "text/javascript")
        if path in ("/demo/", "/demo/index.html", "/demo/legacy.html"):
            name = "legacy.html" if path.endswith("legacy.html") else "index.html"
            markup = (ROOT / "demo" / name).read_text()
            markup = markup.replace("<head>", '<head>\n<script src="__probe-boot.js"></script>', 1)
            markup = markup.replace("</head>", '<script src="__probe-check.js" defer></script>\n</head>', 1)
            return self.send_bytes(markup.encode(), "text/html; charset=utf-8")
        self.path = path
        super().do_GET()

    def send_bytes(self, data, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside, self.result = False, ""

    def handle_starttag(self, tag, attrs):
        if tag == "pre" and dict(attrs).get("id") == "browser-probe-result":
            self.inside = True

    def handle_endtag(self, tag):
        if tag == "pre":
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.result += data


def check_links(links, origin):
    """외부 GitHub URL은 요청하지 않고 배포 내 링크를 실제 HTTP로 확인한다."""
    checked = []
    for link in sorted(set(links)):
        parsed = urlsplit(link)
        if not link.startswith(origin + "/"):
            continue
        with urlopen(link.split("#", 1)[0], timeout=5) as response:
            if response.status != 200:
                raise ValueError("local link failed: " + parsed.path)
        checked.append(parsed.path)
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", help="Chrome/Chromium executable; auto-detected by default")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/browser-validation.json")
    args = parser.parse_args()
    browser = args.browser or next((shutil.which(name) for name in
        ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser") if shutil.which(name)), None)
    if not browser:
        parser.error("Chrome/Chromium is required for this optional browser check; core commands use Python only")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(ProbeServer, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = "http://127.0.0.1:" + str(server.server_port)
    results = []
    try:
        for page, viewport in (("/demo/", "1440,1000"), ("/demo/", "500,844"),
                               ("/demo/legacy.html", "1440,1000")):
            with tempfile.TemporaryDirectory(prefix="harness-browser-") as profile:
                command = [browser, "--headless=new", "--disable-gpu", "--disable-dev-shm-usage",
                           "--no-sandbox", "--no-first-run", "--no-default-browser-check",
                           "--disable-background-networking", "--disable-component-update", "--disable-sync",
                           "--user-data-dir=" + profile, "--window-size=" + viewport,
                           "--virtual-time-budget=3000", "--dump-dom", origin + PREFIX + page]
                process = subprocess.run(command, capture_output=True, text=True, timeout=40)
                if process.returncode:
                    raise RuntimeError("Chrome failed (exit " + str(process.returncode) + ")")
                parsed = ResultParser()
                parsed.feed(process.stdout)
                if not parsed.result:
                    raise RuntimeError("Browser probe did not complete")
                result = json.loads(parsed.result)
                result["viewport"] = viewport
                result["local_links_checked"] = check_links(result.pop("links"), origin)
                results.append(result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    output = {"kind": "actual Chrome static UI check; synthetic data; no live API",
              "ok": all(result["ok"] for result in results), "results": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
