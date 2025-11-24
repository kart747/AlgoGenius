"""
Improved SandboxManager using docker-py with stricter isolation and clearer error handling.

Features:
- Configurable images via environment variables: PY_IMAGE, CPP_IMAGE, JAVA_IMAGE
- read-only /code mount for user code
- compile into /tmp inside container
- network disabled, memory limit, capability drops, user override
- wall-clock timeout enforcement
"""
from __future__ import annotations
import os
import time
import tempfile
import textwrap
import threading
from pathlib import Path
from typing import Dict, Optional

import docker
from docker.errors import ContainerError, APIError, ImageNotFound

DEFAULT_PY_IMAGE = os.getenv("PY_IMAGE", "python:3.11-slim")
DEFAULT_CPP_IMAGE = os.getenv("CPP_IMAGE", "gcc:13.2.0-bookworm")
DEFAULT_JAVA_IMAGE = os.getenv("JAVA_IMAGE", "eclipse-temurin:17-jdk")


class SandboxManager:
    _GLOBAL_IMAGE_CACHE = set()
    _GLOBAL_IMAGE_LOCK = threading.Lock()

    def __init__(self, py_image: Optional[str] = None, cpp_image: Optional[str] = None, java_image: Optional[str] = None):
        self.client = docker.from_env()
        self.py_image = py_image or DEFAULT_PY_IMAGE
        self.cpp_image = cpp_image or DEFAULT_CPP_IMAGE
        self.java_image = java_image or DEFAULT_JAVA_IMAGE
        self.mem_limit = "100m"
        self.timeout = float(os.getenv("SANDBOX_TIMEOUT_SEC", "25"))
        self.cap_drop = ["ALL"]
        self.user = os.getenv("SANDBOX_USER", "nobody")
        self._ensured_images = SandboxManager._GLOBAL_IMAGE_CACHE
        self._image_lock = SandboxManager._GLOBAL_IMAGE_LOCK

    def _ensure_image(self, image: str) -> Optional[Dict]:
        """Pull the image once outside of the per-run timeout budget."""
        with self._image_lock:
            if image in self._ensured_images:
                return None
            try:
                # Avoid expensive pulls when the image already exists locally.
                self.client.images.get(image)
            except ImageNotFound:
                try:
                    self.client.images.pull(image)
                except ImageNotFound:
                    return {"status": "Error", "output": f"Image not found: {image}", "exit_code": -1, "runtime_ms": 0.0}
                except APIError as exc:
                    return {"status": "Error", "output": f"Docker API error while pulling {image}: {exc}", "exit_code": -1, "runtime_ms": 0.0}
            except APIError as exc:
                return {"status": "Error", "output": f"Docker API error while checking {image}: {exc}", "exit_code": -1, "runtime_ms": 0.0}

            self._ensured_images.add(image)
            return None

    def _run_container(self, image: str, command: str, mounts: Dict[str, Dict], env: Dict[str, str]) -> Dict:
        container = None
        try:
            ensure_error = self._ensure_image(image)
            if ensure_error:
                return ensure_error

            start = time.time()
            container = self.client.containers.run(
                image=image,
                command=["/bin/sh", "-lc", command],
                volumes=mounts,
                environment=env or {},
                network_disabled=True,
                mem_limit=self.mem_limit,
                read_only=True,
                user=self.user,
                cap_drop=self.cap_drop,
                tmpfs={"/tmp": "rw,nosuid,nodev,exec"},
                detach=True,
                stdout=True,
                stderr=True,
                tty=False,
                remove=False,
            )

            deadline = start + self.timeout
            while True:
                container.reload()
                state = container.attrs.get("State", {})
                if not state.get("Running"):
                    break
                if time.time() > deadline:
                    try:
                        container.kill()
                    except Exception:
                        pass
                    return {"status": "Error", "output": f"Timeout after {self.timeout}s", "exit_code": -1, "runtime_ms": (time.time() - start) * 1000.0}
                time.sleep(0.02)

            exit_code = container.attrs.get("State", {}).get("ExitCode", -1)
            logs = container.logs(stdout=True, stderr=True)
            output = logs.decode("utf-8", errors="replace")
            runtime_ms = (time.time() - start) * 1000.0
            return {"status": "Success", "output": output, "exit_code": int(exit_code), "runtime_ms": float(runtime_ms)}

        except ContainerError as e:
            runtime_ms = (time.time() - start) * 1000.0
            err_out = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, (bytes, bytearray)) else str(e)
            return {"status": "Error", "output": err_out, "exit_code": getattr(e, 'exit_status', -1), "runtime_ms": float(runtime_ms)}
        except APIError as e:
            return {"status": "Error", "output": f"Docker API error: {str(e)}", "exit_code": -1, "runtime_ms": 0.0}
        except Exception as e:
            return {"status": "Error", "output": f"Unexpected error: {str(e)}", "exit_code": -1, "runtime_ms": 0.0}
        finally:
            try:
                if container is not None:
                    container.remove(force=True)
            except Exception:
                pass

    def run_python(self, code: str, input_data: Optional[str]) -> Dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            host_dir = Path(tmpdir)
            file = host_dir / "main.py"
            file.write_text(code, encoding="utf-8")
            mounts = {str(host_dir): {"bind": "/code", "mode": "ro"}}
            env = {
                "USER_INPUT": input_data or "",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONUNBUFFERED": "1",
            }
            cmd = 'printf "%s" "$USER_INPUT" | python3 -B -u /code/main.py'
            return self._run_container(self.py_image, cmd, mounts, env)

    def run_cpp(self, code: str, input_data: Optional[str]) -> Dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            host_dir = Path(tmpdir)
            file = host_dir / "main.cpp"
            file.write_text(code, encoding="utf-8")
            mounts = {str(host_dir): {"bind": "/code", "mode": "ro"}}
            env = {"USER_INPUT": input_data or ""}
            cmd = textwrap.dedent("""
                g++ /code/main.cpp -O2 -std=c++17 -o /tmp/a.out 2>/tmp/compile_err || true
                if [ -f /tmp/a.out ]; then
                    printf "%s" "$USER_INPUT" | /tmp/a.out
                else
                    cat /tmp/compile_err
                    exit 1
                fi
            """)
            return self._run_container(self.cpp_image, cmd, mounts, env)

    def run_java(self, code: str, input_data: Optional[str]) -> Dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            host_dir = Path(tmpdir)
            file = host_dir / "Main.java"
            file.write_text(code, encoding="utf-8")
            mounts = {str(host_dir): {"bind": "/code", "mode": "ro"}}
            env = {"USER_INPUT": input_data or ""}
            cmd = textwrap.dedent("""
                mkdir -p /tmp && javac /code/Main.java -d /tmp 2>/tmp/compile_err || true
                if ls /tmp | grep -q "Main.class"; then
                    printf "%s" "$USER_INPUT" | java -cp /tmp Main
                else
                    cat /tmp/compile_err
                    exit 1
                fi
            """)
            return self._run_container(self.java_image, cmd, mounts, env)




