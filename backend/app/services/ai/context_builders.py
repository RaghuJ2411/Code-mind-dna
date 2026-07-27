from typing import Dict, Any


def build_code_review_context(problem: dict, submission: dict) -> Dict[str, Any]:
    """Build a safe, minimal context dict for code review AI tasks.

    Both `problem` and `submission` must be sanitized by the caller. This function
    only selects allowed fields and organizes them into a predictable structure.
    """
    ctx = {
        "problem": {
            "id": problem.get("id"),
            "title": problem.get("title"),
            "description": problem.get("description"),
            "constraints": problem.get("constraints"),
            "difficulty": problem.get("difficulty"),
            "topics": problem.get("topics"),
        },
        "submission": {
            "language": submission.get("language"),
            # include student's source code (untrusted) but as its own field
            "source_code": submission.get("source_code"),
            "verdict": submission.get("verdict"),
            "safe_error": submission.get("safe_error"),
            "passed_test_count": submission.get("passed_test_count"),
            "total_test_count": submission.get("total_test_count"),
            "runtime_ms": submission.get("runtime_ms"),
            "memory_kb": submission.get("memory_kb"),
        },
    }
    return ctx
