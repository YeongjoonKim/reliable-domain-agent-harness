"""명시적으로 선택한 로컬 Docker에서만 격리 실행한다. 호스트 실행 대체는 없다."""
from dataclasses import dataclass
import os
import re
import selectors
import subprocess
import time
from uuid import uuid4


@dataclass(frozen=True)
class SandboxPolicy:
    image: str
    timeout: float = 10
    output_limit: int = 65536

    def __post_init__(self):
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", self.image):
            raise ValueError("explicit local image ID required")
        if not 0.1 <= self.timeout <= 60 or not 1024 <= self.output_limit <= 1048576:
            raise ValueError("invalid sandbox budget")


def command(policy, name, code):
    return ["docker", "run", "--pull=never", "--name", name, "--network=none", "--read-only",
            "--user=65534:65534", "--cap-drop=ALL", "--security-opt=no-new-privileges",
            "--cpus=0.5", "--memory=128m", "--memory-swap=128m", "--pids-limit=32",
            "--log-driver=none", "--tmpfs=/work:rw,nosuid,nodev,noexec,size=16m,mode=1777",
            "--workdir=/work", "--env=PYTHONDONTWRITEBYTECODE=1", policy.image,
            "python", "-I", "-c", code]


def run_python(code, policy):
    if not isinstance(code, str) or len(code.encode()) > 32768:
        raise ValueError("bounded code required")
    name = "public-harness-" + uuid4().hex
    started = time.monotonic()
    streams, status, proc = {"stdout": bytearray(), "stderr": bytearray()}, "ok", None
    cleanup = False
    try:
        # 코드 문자열은 shell을 거치지 않으며 호스트 환경이나 디렉터리를 전달하지 않는다.
        proc = subprocess.Popen(command(policy, name, code), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ, "stdout")
            selector.register(proc.stderr, selectors.EVENT_READ, "stderr")
            while selector.get_map():
                if time.monotonic() - started > policy.timeout:
                    status = "timeout"
                    break
                for key, _ in selector.select(0.02):
                    chunk = os.read(key.fileobj.fileno(), 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    remaining = policy.output_limit - sum(map(len, streams.values()))
                    streams[key.data].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        status = "output_limit"
                        break
                if status != "ok":
                    break
        if status != "ok":
            proc.kill()
        proc.wait(timeout=2)
        if status == "ok" and proc.returncode:
            status = "execution_error"
    finally:
        if proc is not None:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=2)
            proc.stdout.close()
            proc.stderr.close()
        # 이번 실행에서 만든 정확한 이름만 정리한다. 다른 컨테이너는 건드리지 않는다.
        removed = subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
        cleanup = removed.returncode == 0
    return dict(status=status, exit_code=proc.returncode, cleanup=cleanup,
                stdout=streams["stdout"].decode("utf-8", errors="replace"),
                stderr=streams["stderr"].decode("utf-8", errors="replace"), image=policy.image,
                latency_ms=round((time.monotonic() - started) * 1000, 3))
