"""MCP stdio의 초기화, 도구 목록과 호출 부분집합을 실제 JSON-RPC로 제공한다."""
import asyncio
import json
import sys
from .tools import make_registry


class Server:
    def __init__(self, registry=None):
        self.registry = registry or make_registry()
        self.initialized, self.ready = False, False

    async def handle(self, request):
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return self.error(None, -32600, "Invalid Request")
        identifier, method = request.get("id"), request.get("method")
        if "id" not in request:
            if method == "notifications/initialized" and self.initialized:
                self.ready = True
            return None
        params = request.get("params", {})
        if not isinstance(params, dict):
            return self.error(identifier, -32602, "Invalid params")
        if method == "initialize":
            if self.initialized or not all(key in params for key in ("protocolVersion", "capabilities", "clientInfo")):
                return self.error(identifier, -32602, "Invalid initialization")
            self.initialized = True
            result = dict(protocolVersion="2025-11-25", capabilities={"tools": {"listChanged": False}},
                          serverInfo={"name": "public-harness", "version": "1.0"})
        elif method == "ping":
            result = {}
        elif not self.ready:
            return self.error(identifier, -32600, "Initialize before tool access")
        elif method == "tools/list":
            result = {"tools": [dict(name=spec.name, description=spec.description,
                                     inputSchema=spec.input_schema, outputSchema=spec.output_schema)
                                for spec in self.registry.specs.values()]}
        elif method == "tools/call":
            if not isinstance(params.get("name"), str) or params["name"] not in self.registry.specs:
                return self.error(identifier, -32602, "Unknown tool")
            arguments = params.get("arguments", {})
            if not isinstance(arguments, dict):
                return self.error(identifier, -32602, "Invalid arguments")
            output = await self.registry.call(params["name"], arguments, ("read:synthetic", "compute:trusted"))
            if output["status"] == "schema_error":
                return self.error(identifier, -32602, "Invalid arguments")
            failed = output["status"] != "ok"
            body = {"evidence": output["evidence"]}
            result = dict(content=[dict(type="text", text=output["status"] if failed else json.dumps(body))],
                          isError=failed)
            if not failed:
                result["structuredContent"] = body
        else:
            return self.error(identifier, -32601, "Method not found")
        return dict(jsonrpc="2.0", id=identifier, result=result)

    @staticmethod
    def error(identifier, code, message):
        return dict(jsonrpc="2.0", id=identifier, error=dict(code=code, message=message))


def main():
    server = Server()
    while True:
        raw = sys.stdin.buffer.readline(65537)
        if not raw:
            break
        if len(raw) > 65536:
            # 크기 초과 프레임 뒤에 이어지는 바이트를 새 요청으로 해석하지 않는다.
            print(json.dumps(server.error(None, -32600, "Frame too large")), flush=True)
            break
        try:
            request = json.loads(raw)
            reply = asyncio.run(server.handle(request))
        except (ValueError, UnicodeError):
            reply = server.error(None, -32700, "Parse error")
        if reply is not None:
            print(json.dumps(reply, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
