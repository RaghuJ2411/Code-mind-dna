from __future__ import annotations

from app.services.execution.normalizer import normalize_output


def compare_outputs(expected_output: str, actual_output: str) -> bool:
    return normalize_output(expected_output) == normalize_output(actual_output)
