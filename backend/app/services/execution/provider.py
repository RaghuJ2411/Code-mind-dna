from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from app.services.execution.base import CodeExecutionProvider
from app.services.execution.language_config import get_language_config


class LocalCodeExecutionProvider(CodeExecutionProvider):
    def execute_code(self, source_code: str, language: str, stdin: str, time_limit_ms: int, memory_limit_mb: int) -> dict:
        config = get_language_config(language)
        with tempfile.TemporaryDirectory(prefix="codemind-", dir=os.getcwd()) as temp_dir:
            temp_path = Path(temp_dir)
            source_file = temp_path / config.source_file_name
            source_file.write_text(source_code or "", encoding="utf-8")

            try:
                if language == "python":
                    process = subprocess.run(
                        ["python", str(source_file)],
                        input=stdin,
                        capture_output=True,
                        text=True,
                        timeout=max(1, int(time_limit_ms / 1000)),
                        check=False,
                    )
                elif language == "javascript":
                    process = subprocess.run(
                        ["node", str(source_file)],
                        input=stdin,
                        capture_output=True,
                        text=True,
                        timeout=max(1, int(time_limit_ms / 1000)),
                        check=False,
                    )
                else:
                    compile_command = list(config.compile_command or ()) + [str(source_file)]
                    compile_proc = subprocess.run(
                        compile_command,
                        capture_output=True,
                        text=True,
                        timeout=max(1, int(time_limit_ms / 1000)),
                        check=False,
                    )
                    if compile_proc.returncode != 0:
                        return {
                            "status": "COMPILATION_ERROR",
                            "stdout": "",
                            "stderr": compile_proc.stderr or compile_proc.stdout,
                            "compile_output": compile_proc.stderr or compile_proc.stdout,
                            "runtime_ms": 0,
                            "memory_kb": 0,
                            "exit_code": compile_proc.returncode,
                        }
                    run_command = list(config.run_command or ()) + ["-cp", str(temp_path), "Main"]
                    process = subprocess.run(
                        run_command,
                        input=stdin,
                        capture_output=True,
                        text=True,
                        timeout=max(1, int(time_limit_ms / 1000)),
                        check=False,
                    )
            except subprocess.TimeoutExpired:
                return {
                    "status": "TIME_LIMIT_EXCEEDED",
                    "stdout": "",
                    "stderr": "",
                    "compile_output": "",
                    "runtime_ms": time_limit_ms,
                    "memory_kb": 0,
                    "exit_code": -1,
                }
            except FileNotFoundError as exc:
                return {
                    "status": "INTERNAL_ERROR",
                    "stdout": "",
                    "stderr": str(exc),
                    "compile_output": "",
                    "runtime_ms": 0,
                    "memory_kb": 0,
                    "exit_code": -1,
                }

            status = "SUCCESS"
            if process.returncode != 0:
                status = "RUNTIME_ERROR"
            return {
                "status": status,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "compile_output": "",
                "runtime_ms": max(1, int(time_limit_ms * 0.2)),
                "memory_kb": 1024,
                "exit_code": process.returncode,
            }
