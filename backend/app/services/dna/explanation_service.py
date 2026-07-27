from __future__ import annotations

from app.services.dna.config import EvidenceStatus


def build_dimension_explanation(dimension: str, features: dict[str, object]) -> str:
    if dimension == "DEBUGGING":
        if features.get("error_recovery_rate", 0.0) >= 0.8 and features.get("repeated_error_rate", 1.0) <= 0.2:
            return "Strong recovery from errors with few repeated mistakes."
        if features.get("error_recovery_rate", 0.0) < 0.4:
            return "Debugging evidence is still developing, focusing on recovery from errors."
        return "Debugging behavior shows moderate recovery after failures."

    if dimension == "CONSISTENCY":
        return "Activity has been reasonably regular, with sustained coding days and balanced weeks."

    if dimension == "LEARNING_VELOCITY":
        return "Recent progress is reflected by solve rate and difficulty progression improvements."

    if dimension == "OPTIMIZATION":
        return "Optimization evidence is based on runtime and memory improvement after accepted solutions."

    if dimension == "LOGIC":
        return "Logic score reflects problem accuracy, first-attempt success, and difficulty performance."

    if dimension == "PROBLEM_SOLVING_BREADTH":
        return "Breadth reflects how many topics are attempted meaningfully and solved successfully."

    return "This dimension is based on available coding performance evidence."


def build_summary_explanation(overall_score: float | None, evidence_status: EvidenceStatus) -> str:
    if overall_score is None:
        return "Coding DNA profile is not available due to insufficient evidence."
    if evidence_status == EvidenceStatus.LIMITED_DATA:
        return "The profile is available but based on limited coding activity."
    return "The profile is generated from available coding behavior and performance evidence."
