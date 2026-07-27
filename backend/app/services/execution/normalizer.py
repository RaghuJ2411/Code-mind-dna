from __future__ import annotations

import re


def normalize_output(output: str | None) -> str:
    if output is None:
        return ""
    output = output.replace("\r\n", "\n").replace("\r", "\n")
    output = output.rstrip(" \t")
    if output.endswith("\n"):
        output = output[:-1]
    return output


def normalize_execution_result(result: dict) -> dict:
    sanitized = dict(result)
    sanitized["stdout"] = normalize_output(result.get("stdout"))
    sanitized["stderr"] = normalize_output(result.get("stderr"))
    sanitized["compile_output"] = normalize_output(result.get("compile_output"))
    return sanitized
