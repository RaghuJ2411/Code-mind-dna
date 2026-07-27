from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.models.problem import Problem, TestCase
from app.models.user import User
from app.services.execution import LocalCodeExecutionProvider, normalize_execution_result, validate_language
from app.services.execution.base import CodeExecutionProvider
from app.services.execution_output import compare_outputs


class ExecutionService:
    def __init__(self, db: Any, current_user: User):
        self.db = db
        self.current_user = current_user
        self.provider: CodeExecutionProvider = self._build_provider()

    def _build_provider(self) -> CodeExecutionProvider:
        provider_name = (settings.code_execution_provider or "local").strip().lower()
        if provider_name != "local":
            return LocalCodeExecutionProvider()
        return LocalCodeExecutionProvider()

    def _execute_with_provider(self, source_code: str, language: str, stdin: str, time_limit_ms: int, memory_limit_mb: int) -> dict:
        return self.provider.execute_code(source_code, language, stdin, time_limit_ms, memory_limit_mb)

    def validate_problem(self, problem_id: int) -> Problem:
        problem = self.db.query(Problem).filter(Problem.id == problem_id, Problem.is_active.is_(True)).first()
        if not problem:
            raise ValueError("Problem not found")
        return problem

    def validate_language(self, language: str) -> str:
        return validate_language(language)

    def run_sample_tests(self, problem: Problem, language: str, source_code: str) -> dict:
        sample_cases = [
            test_case
            for test_case in sorted(problem.test_cases, key=lambda item: item.order_index)
            if test_case.is_sample
        ]
        results = []
        for index, test_case in enumerate(sample_cases, start=1):
            execution_result = normalize_execution_result(
                self._execute_with_provider(
                    source_code,
                    language,
                    test_case.input_data,
                    problem.time_limit_ms,
                    problem.memory_limit_mb,
                )
            )
            normalized_output = execution_result.get("stdout", "")
            expected_output = (test_case.expected_output or "").strip()
            actual_output = (normalized_output or "").strip()
            if execution_result.get("status") == "SUCCESS" and compare_outputs(expected_output, actual_output):
                passed = True
                status = "SUCCESS"
            elif execution_result.get("status") == "COMPILATION_ERROR":
                passed = False
                status = "COMPILATION_ERROR"
            elif execution_result.get("status") == "TIME_LIMIT_EXCEEDED":
                passed = False
                status = "TIME_LIMIT_EXCEEDED"
            elif execution_result.get("status") == "RUNTIME_ERROR":
                passed = False
                status = "RUNTIME_ERROR"
            else:
                passed = False
                status = "WRONG_ANSWER"
            results.append(
                {
                    "test_case_number": index,
                    "passed": passed,
                    "status": status,
                    "input": test_case.input_data,
                    "expected_output": test_case.expected_output,
                    "actual_output": normalized_output,
                    "runtime_ms": execution_result.get("runtime_ms"),
                    "memory_kb": execution_result.get("memory_kb"),
                    "error_message": self._classify_error(execution_result),
                }
            )
        passed = sum(1 for item in results if item["passed"])
        overall_status = "PARTIAL"
        if not results:
            overall_status = "NO_TESTS"
        elif passed == len(results):
            overall_status = "PASS"
        return {
            "overall_status": overall_status,
            "passed": passed,
            "total": len(results),
            "results": results,
        }

    def run_submission(self, problem: Problem, language: str, source_code: str) -> dict:
        evaluation_cases = [
            test_case
            for test_case in sorted(problem.test_cases, key=lambda item: item.order_index)
            if not test_case.is_sample
        ]
        if not evaluation_cases:
            evaluation_cases = [
                test_case
                for test_case in sorted(problem.test_cases, key=lambda item: item.order_index)
                if test_case.is_sample
            ]
        results = []
        for test_case in evaluation_cases:
            execution_result = normalize_execution_result(
                self._execute_with_provider(
                    source_code,
                    language,
                    test_case.input_data,
                    problem.time_limit_ms,
                    problem.memory_limit_mb,
                )
            )
            status = self._map_status(execution_result)
            if status == "SUCCESS":
                expected_output = (test_case.expected_output or "").strip()
                actual_output = (execution_result.get("stdout") or "").strip()
                if not compare_outputs(expected_output, actual_output):
                    status = "WRONG_ANSWER"
            results.append({"test_case": test_case, "status": status, "result": execution_result})
            if status in {"COMPILATION_ERROR", "TIME_LIMIT_EXCEEDED", "RUNTIME_ERROR"}:
                break
        passed = sum(1 for item in results if item["status"] == "SUCCESS")
        verdict = self._determine_verdict(results)
        return {
            "verdict": verdict,
            "passed_test_cases": passed,
            "total_test_cases": len(evaluation_cases),
            "runtime_ms": max((item["result"].get("runtime_ms") or 0) for item in results) if results else None,
            "memory_kb": max((item["result"].get("memory_kb") or 0) for item in results) if results else None,
            "results": results,
        }

    def _map_status(self, execution_result: dict) -> str:
        status = execution_result.get("status", "SUCCESS")
        if status == "COMPILATION_ERROR":
            return "COMPILATION_ERROR"
        if status == "TIME_LIMIT_EXCEEDED":
            return "TIME_LIMIT_EXCEEDED"
        if status == "RUNTIME_ERROR":
            return "RUNTIME_ERROR"
        if status == "SUCCESS":
            return "SUCCESS"
        return "INTERNAL_ERROR"

    def _determine_verdict(self, results: list[dict]) -> str:
        if not results:
            return "WRONG_ANSWER"
        if any(item["status"] == "COMPILATION_ERROR" for item in results):
            return "COMPILATION_ERROR"
        if any(item["status"] == "TIME_LIMIT_EXCEEDED" for item in results):
            return "TIME_LIMIT_EXCEEDED"
        if any(item["status"] == "RUNTIME_ERROR" for item in results):
            return "RUNTIME_ERROR"
        if all(item["status"] == "SUCCESS" for item in results):
            return "ACCEPTED"
        return "WRONG_ANSWER"

    def _classify_error(self, execution_result: dict) -> str | None:
        status = execution_result.get("status")
        if status == "COMPILATION_ERROR":
            return (execution_result.get("stderr") or execution_result.get("compile_output") or "Compilation failed.").strip()
        if status == "RUNTIME_ERROR":
            return (execution_result.get("stderr") or execution_result.get("compile_output") or "Runtime error.").strip()
        if status == "TIME_LIMIT_EXCEEDED":
            return "Time limit exceeded."
        return None

    def record_behavior_event(self, db: Any, problem: Problem, event_type: str, metadata: dict | None = None, language: str | None = None) -> None:
        from app.models.execution import CodingEvent

        event = CodingEvent(
            student_id=self.current_user.id,
            problem_id=problem.id,
            session_id=None,
            event_type=event_type,
            language=language or "python",
            metadata_json=metadata or {},
        )
        db.add(event)
        db.commit()
