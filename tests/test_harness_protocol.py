"""프로토콜 실제 왕복과 Docker 실행 정책 계약을 분리해서 검증한다."""
import json
import subprocess
import sys
import unittest
from src.harness.sandbox import SandboxPolicy, command


class ProtocolTests(unittest.TestCase):
    def exchange(self, messages):
        result = subprocess.run([sys.executable, "-m", "src.harness.mcp_adapter"],
            input="\n".join(json.dumps(message) for message in messages) + "\n",
            text=True, capture_output=True, timeout=5, check=True)
        self.assertEqual(result.stderr, "")
        return [json.loads(line) for line in result.stdout.splitlines()]

    def init(self):
        return [dict(jsonrpc="2.0", id=1, method="initialize", params=dict(
            protocolVersion="2025-11-25", capabilities={}, clientInfo=dict(name="test", version="1"))),
            dict(jsonrpc="2.0", method="notifications/initialized")]

    def test_actual_stdio_roundtrip(self):
        responses = self.exchange(self.init() + [dict(jsonrpc="2.0", id=2, method="tools/list"),
            dict(jsonrpc="2.0", id=3, method="tools/call", params=dict(
                name="numerical_analysis", arguments={"values": [1, 2, 3]}))])
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(len(responses[1]["result"]["tools"]), 3)
        evidence = responses[2]["result"]["structuredContent"]["evidence"]
        self.assertEqual(next(row for row in evidence if row["metric"] == "mean")["value"], 2)

    def test_uninitialized_call_rejected(self):
        result = self.exchange([dict(jsonrpc="2.0", id=1, method="tools/list")])
        self.assertIn("error", result[0])

    def test_unknown_method_and_tool(self):
        results = self.exchange(self.init() + [dict(jsonrpc="2.0", id=2, method="unknown"),
            dict(jsonrpc="2.0", id=3, method="tools/call", params=dict(name="missing"))])
        self.assertEqual([row["error"]["code"] for row in results[1:]], [-32601, -32602])

    def test_bad_numeric_input(self):
        results = self.exchange(self.init() + [dict(jsonrpc="2.0", id=3, method="tools/call",
            params=dict(name="numerical_analysis", arguments={"values": [1, True]}))])
        self.assertEqual(results[-1]["error"]["code"], -32602)

    def test_sandbox_command_policy_not_isolation_test(self):
        policy = SandboxPolicy("sha256:" + "a" * 64)
        args = command(policy, "public-harness-test", "print(1)")
        for option in ("--network=none", "--read-only", "--user=65534:65534", "--memory=128m",
                       "--cpus=0.5", "--pids-limit=32", "--cap-drop=ALL", "--pull=never"):
            self.assertIn(option, args)
        self.assertNotIn("--volume", args)

    def test_sandbox_requires_local_immutable_image(self):
        with self.assertRaises(ValueError):
            SandboxPolicy("python:latest")
