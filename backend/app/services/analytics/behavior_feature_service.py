"""
Behavior Feature Extraction Service

Calculates behavioral features from raw data (submissions, events, sessions).
All metrics are deterministic, based on real data, no random values.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
import statistics

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.execution import CodingEvent, CodingSession, Submission, SubmissionVerdict
from app.models.problem import Problem, DifficultyLevel
from app.models.user import User


class BehaviorFeatureService:
    """Extract behavioral features from student activity data."""

    def __init__(self, db: Session):
        self.db = db

    # ========================= ACTIVE TIME CALCULATION =========================

    def calculate_active_session_minutes(self, session: CodingSession) -> int:
        """
        Calculate active minutes for a session, excluding idle gaps.
        
        Idle threshold: CODING_SESSION_IDLE_MINUTES
        """
        if session.ended_at is None:
            return 0

        total_seconds = max(0.0, (session.ended_at - session.started_at).total_seconds())
        
        # If session duration is less than idle threshold, count all time
        idle_threshold_seconds = settings.coding_session_idle_minutes * 60
        if total_seconds <= idle_threshold_seconds:
            return int(total_seconds / 60)
        
        # Otherwise, cap the duration at idle threshold to avoid counting dead time
        return settings.coding_session_idle_minutes

    @staticmethod
    def _coerce_activity_date(value: object) -> date | None:
        """Normalize database date values across SQLite/Postgres drivers."""
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise TypeError(f"Unsupported activity date value: {value!r}")

    def calculate_total_active_minutes(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> int:
        """Calculate total active coding minutes for a student."""
        query = self.db.query(CodingSession).filter(CodingSession.student_id == student_id, CodingSession.ended_at.isnot(None))

        if start_date:
            query = query.filter(CodingSession.started_at >= start_date)
        if end_date:
            query = query.filter(CodingSession.started_at < end_date)

        sessions = query.all()
        return sum(self.calculate_active_session_minutes(session) for session in sessions)

    # ========================= ACTIVITY METRICS =========================

    def calculate_activity_metrics(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
        """Calculate activity-related metrics."""
        query_base = self.db.query(Submission).filter(Submission.student_id == student_id)

        if start_date:
            query_base = query_base.filter(Submission.created_at >= start_date)
        if end_date:
            query_base = query_base.filter(Submission.created_at < end_date)

        # Get all submissions
        submissions = query_base.all()

        # Unique problems attempted
        attempted_problems = len(set(s.problem_id for s in submissions))

        # Unique problems solved (ACCEPTED verdict)
        solved_problems = len(set(s.problem_id for s in submissions if s.verdict == SubmissionVerdict.ACCEPTED))

        # Total submissions
        total_submissions = len(submissions)

        # Total runs
        runs = self.db.query(CodingEvent).filter(CodingEvent.student_id == student_id, CodingEvent.event_type == "RUN_CODE")
        if start_date:
            runs = runs.filter(CodingEvent.created_at >= start_date)
        if end_date:
            runs = runs.filter(CodingEvent.created_at < end_date)
        total_runs = runs.count()

        # Active minutes
        active_minutes = self.calculate_total_active_minutes(student_id, start_date, end_date)

        # Active days
        active_days_query = (
            self.db.query(func.count(func.distinct(func.date(CodingSession.started_at))))
            .filter(CodingSession.student_id == student_id, CodingSession.ended_at.isnot(None))
        )
        if start_date:
            active_days_query = active_days_query.filter(CodingSession.started_at >= start_date)
        if end_date:
            active_days_query = active_days_query.filter(CodingSession.started_at < end_date)
        active_days = active_days_query.scalar() or 0

        return {
            "problems_attempted": attempted_problems,
            "problems_solved": solved_problems,
            "total_submissions": total_submissions,
            "total_runs": total_runs,
            "active_minutes": active_minutes,
            "active_days": active_days,
        }

    # ========================= SUCCESS METRICS =========================

    def calculate_success_metrics(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
        """Calculate success-related metrics."""
        query = self.db.query(Submission).filter(Submission.student_id == student_id)

        if start_date:
            query = query.filter(Submission.created_at >= start_date)
        if end_date:
            query = query.filter(Submission.created_at < end_date)

        submissions = query.all()

        if not submissions:
            return {
                "solve_rate": 0.0,
                "first_attempt_acceptance_rate": 0.0,
                "average_attempts_to_solve": 0.0,
                "median_attempts_to_solve": 0.0,
            }

        # Unique attempted problems
        attempted_problems = set(s.problem_id for s in submissions)
        attempted_count = len(attempted_problems)

        # Unique solved problems
        solved_submissions = [s for s in submissions if s.verdict == SubmissionVerdict.ACCEPTED]
        solved_problems = set(s.problem_id for s in solved_submissions)
        solved_count = len(solved_problems)

        # Solve rate
        solve_rate = solved_count / attempted_count if attempted_count > 0 else 0.0

        # First attempt acceptance rate
        first_submissions = {}
        for s in submissions:
            if s.problem_id not in first_submissions or s.attempt_number < first_submissions[s.problem_id].attempt_number:
                first_submissions[s.problem_id] = s

        first_accepted = sum(1 for s in first_submissions.values() if s.verdict == SubmissionVerdict.ACCEPTED)
        first_attempt_acceptance_rate = first_accepted / len(first_submissions) if first_submissions else 0.0

        # Average attempts to solve
        attempts_per_problem = {}
        for s in solved_submissions:
            if s.problem_id not in attempts_per_problem:
                attempts_per_problem[s.problem_id] = s.attempt_number

        average_attempts = sum(attempts_per_problem.values()) / len(attempts_per_problem) if attempts_per_problem else 0.0

        # Median attempts (simplified: sort and take middle)
        sorted_attempts = sorted(attempts_per_problem.values()) if attempts_per_problem else []
        if sorted_attempts:
            mid = len(sorted_attempts) // 2
            median_attempts = sorted_attempts[mid]
        else:
            median_attempts = 0.0

        return {
            "solve_rate": solve_rate,
            "first_attempt_acceptance_rate": first_attempt_acceptance_rate,
            "average_attempts_to_solve": average_attempts,
            "median_attempts_to_solve": float(median_attempts),
        }

    # ========================= DEBUGGING METRICS =========================

    def calculate_debugging_metrics(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
        """Calculate debugging behavior metrics."""
        query = self.db.query(Submission).filter(Submission.student_id == student_id)

        if start_date:
            query = query.filter(Submission.created_at >= start_date)
        if end_date:
            query = query.filter(Submission.created_at < end_date)

        submissions = query.order_by(Submission.problem_id, Submission.attempt_number).all()

        if not submissions:
            return {
                "total_wrong_answers": 0,
                "total_compilation_errors": 0,
                "total_runtime_errors": 0,
                "total_time_limit_errors": 0,
                "error_recovery_rate": 0.0,
                "repeated_error_rate": 0.0,
            }

        # Error counts
        wrong_answer_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.WRONG_ANSWER)
        compilation_error_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.COMPILATION_ERROR)
        runtime_error_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.RUNTIME_ERROR)
        time_limit_count = sum(1 for s in submissions if s.verdict == SubmissionVerdict.TIME_LIMIT_EXCEEDED)

        # Error recovery rate
        recovery_sequences = 0
        recoverable_sequences = 0

        for problem_id in set(s.problem_id for s in submissions):
            problem_submissions = [s for s in submissions if s.problem_id == problem_id]
            problem_submissions.sort(key=lambda x: x.attempt_number)

            error_sequence = False
            for i, s in enumerate(problem_submissions):
                is_error = s.verdict in {
                    SubmissionVerdict.WRONG_ANSWER,
                    SubmissionVerdict.COMPILATION_ERROR,
                    SubmissionVerdict.RUNTIME_ERROR,
                    SubmissionVerdict.TIME_LIMIT_EXCEEDED,
                }

                if is_error and not error_sequence:
                    error_sequence = True
                elif not is_error and error_sequence:
                    error_sequence = False
                    if s.verdict == SubmissionVerdict.ACCEPTED:
                        recovery_sequences += 1
                    recoverable_sequences += 1
                elif is_error and error_sequence:
                    recoverable_sequences += 1

        error_recovery_rate = recovery_sequences / recoverable_sequences if recoverable_sequences > 0 else 0.0

        # Repeated error rate
        repeated_errors = 0
        total_error_transitions = 0

        for problem_id in set(s.problem_id for s in submissions):
            problem_submissions = [s for s in submissions if s.problem_id == problem_id]
            problem_submissions.sort(key=lambda x: x.attempt_number)

            for i in range(len(problem_submissions) - 1):
                current = problem_submissions[i]
                next_sub = problem_submissions[i + 1]

                current_is_error = current.verdict in {
                    SubmissionVerdict.WRONG_ANSWER,
                    SubmissionVerdict.COMPILATION_ERROR,
                    SubmissionVerdict.RUNTIME_ERROR,
                    SubmissionVerdict.TIME_LIMIT_EXCEEDED,
                }
                next_is_error = next_sub.verdict in {
                    SubmissionVerdict.WRONG_ANSWER,
                    SubmissionVerdict.COMPILATION_ERROR,
                    SubmissionVerdict.RUNTIME_ERROR,
                    SubmissionVerdict.TIME_LIMIT_EXCEEDED,
                }

                if current_is_error and next_is_error and current.verdict == next_sub.verdict:
                    repeated_errors += 1

                if current_is_error and next_is_error:
                    total_error_transitions += 1

        repeated_error_rate = repeated_errors / total_error_transitions if total_error_transitions > 0 else 0.0

        return {
            "total_wrong_answers": wrong_answer_count,
            "total_compilation_errors": compilation_error_count,
            "total_runtime_errors": runtime_error_count,
            "total_time_limit_errors": time_limit_count,
            "error_recovery_rate": error_recovery_rate,
            "repeated_error_rate": repeated_error_rate,
            "recoverable_sequences": recoverable_sequences,
        }

    # ========================= DIFFICULTY METRICS =========================

    def calculate_difficulty_metrics(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
        """Calculate performance metrics by difficulty level."""
        query = self.db.query(Submission).join(Problem).filter(Submission.student_id == student_id)

        if start_date:
            query = query.filter(Submission.created_at >= start_date)
        if end_date:
            query = query.filter(Submission.created_at < end_date)

        submissions = query.all()

        metrics = {}
        for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
            difficulty_subs = [
                s for s in submissions if s.problem and s.problem.difficulty == difficulty
            ]

            attempted = len(set(s.problem_id for s in difficulty_subs))
            solved = len(
                set(
                    s.problem_id
                    for s in difficulty_subs
                    if s.verdict == SubmissionVerdict.ACCEPTED
                )
            )
            solve_rate = solved / attempted if attempted > 0 else 0.0

            # Average attempts
            attempts = [
                s.attempt_number
                for s in difficulty_subs
                if s.verdict == SubmissionVerdict.ACCEPTED
            ]
            avg_attempts = sum(attempts) / len(attempts) if attempts else 0.0

            metrics[difficulty.value.lower()] = {
                "attempted": attempted,
                "solved": solved,
                "solve_rate": solve_rate,
                "average_attempts": avg_attempts,
            }

        # Calculate weighted difficulty (for progression analysis)
        weight_map = {DifficultyLevel.EASY: 1, DifficultyLevel.MEDIUM: 2, DifficultyLevel.HARD: 3}
        solved_problem_difficulties = {
            s.problem_id: s.problem.difficulty
            for s in submissions
            if s.problem and s.verdict == SubmissionVerdict.ACCEPTED
        }
        weighted_sum = sum(weight_map[difficulty] for difficulty in solved_problem_difficulties.values())
        accepted_count = len(solved_problem_difficulties)
        weighted_difficulty = weighted_sum / accepted_count if accepted_count > 0 else 0.0

        metrics["weighted_difficulty"] = weighted_difficulty

        return metrics

    # ========================= OPTIMIZATION METRICS =========================

    def calculate_optimization_metrics(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> dict:
        """Calculate optimization and efficiency metrics."""
        query = self.db.query(Submission).filter(Submission.student_id == student_id)

        if start_date:
            query = query.filter(Submission.created_at >= start_date)
        if end_date:
            query = query.filter(Submission.created_at < end_date)

        submissions = query.order_by(Submission.problem_id, Submission.attempt_number).all()
        if not submissions:
            return {
                "optimization_comparable_pairs": 0,
                "runtime_improvement": None,
                "memory_improvement": None,
                "post_acceptance_refinement": None,
                "execution_efficiency_stability": None,
            }

        accepted_by_problem: dict[int, list[Submission]] = {}
        for submission in submissions:
            if submission.verdict != SubmissionVerdict.ACCEPTED:
                continue
            accepted_by_problem.setdefault(submission.problem_id, []).append(submission)

        runtime_changes = []
        memory_changes = []
        refinement_counts = []
        stability_values = []

        for problem_id, accepted_subs in accepted_by_problem.items():
            if len(accepted_subs) < 2:
                continue

            # Compare first and last accepted submissions for improvements.
            first = accepted_subs[0]
            last = accepted_subs[-1]

            if first.runtime_ms is not None and last.runtime_ms is not None and first.runtime_ms > 0:
                runtime_changes.append((first.runtime_ms - last.runtime_ms) / first.runtime_ms)
            if first.memory_kb is not None and last.memory_kb is not None and first.memory_kb > 0:
                memory_changes.append((first.memory_kb - last.memory_kb) / first.memory_kb)

            if len(accepted_subs) > 2:
                refinement_counts.append(len(accepted_subs) - 1)

            runtimes = [s.runtime_ms for s in accepted_subs if s.runtime_ms is not None]
            if len(runtimes) > 1:
                variation = statistics.pstdev(runtimes)
                stability_values.append(max(0.0, 1.0 - min(1.0, variation / (max(runtimes) or 1.0))))

        comparable_pairs = len(runtime_changes)
        runtime_improvement = sum(runtime_changes) / comparable_pairs if comparable_pairs else None
        memory_improvement = sum(memory_changes) / len(memory_changes) if memory_changes else None
        post_acceptance_refinement = (sum(refinement_counts) / len(refinement_counts)) if refinement_counts else None
        execution_efficiency_stability = (sum(stability_values) / len(stability_values)) if stability_values else None

        return {
            "optimization_comparable_pairs": comparable_pairs,
            "runtime_improvement": runtime_improvement,
            "memory_improvement": memory_improvement,
            "post_acceptance_refinement": post_acceptance_refinement,
            "execution_efficiency_stability": execution_efficiency_stability,
        }

    # ========================= TOPIC METRICS =========================

    def calculate_topic_metrics(self, student_id: int, start_date: datetime | None = None, end_date: datetime | None = None) -> list[dict]:
        """Calculate per-topic performance."""
        query = self.db.query(Submission).join(Problem).filter(Submission.student_id == student_id)

        if start_date:
            query = query.filter(Submission.created_at >= start_date)
        if end_date:
            query = query.filter(Submission.created_at < end_date)

        submissions = query.all()

        # Group by topic
        topics_data = {}
        for s in submissions:
            if s.problem:
                topic = s.problem.topic.value
                if topic not in topics_data:
                    topics_data[topic] = []
                topics_data[topic].append(s)

        results = []
        for topic, topic_subs in topics_data.items():
            attempted = len(set(s.problem_id for s in topic_subs))
            solved = len(
                set(
                    s.problem_id
                    for s in topic_subs
                    if s.verdict == SubmissionVerdict.ACCEPTED
                )
            )
            solve_rate = solved / attempted if attempted > 0 else 0.0

            # Average attempts
            attempts = [
                s.attempt_number
                for s in topic_subs
                if s.verdict == SubmissionVerdict.ACCEPTED
            ]
            avg_attempts = sum(attempts) / len(attempts) if attempts else 0.0

            # Classification based on evidence threshold
            min_attempts = settings.min_topic_attempts_for_classification
            if attempted < min_attempts:
                classification = "INSUFFICIENT_DATA"
            elif solve_rate >= 0.8:
                classification = "STRONG_CANDIDATE"
            elif solve_rate >= 0.5:
                classification = "DEVELOPING"
            else:
                classification = "WEAK_CANDIDATE"

            results.append(
                {
                    "topic": topic,
                    "attempted": attempted,
                    "solved": solved,
                    "solve_rate": solve_rate,
                    "average_attempts": avg_attempts,
                    "classification": classification,
                }
            )

        return sorted(results, key=lambda x: x["solve_rate"], reverse=True)

    # ========================= CONSISTENCY METRICS =========================

    def calculate_consistency_metrics(self, student_id: int) -> dict:
        """Calculate consistency metrics."""
        now = datetime.now(timezone.utc)
        today = now.date()

        sessions = (
            self.db.query(func.date(CodingSession.started_at).label("activity_date"))
            .filter(CodingSession.student_id == student_id, CodingSession.ended_at.isnot(None))
            .distinct()
            .order_by("activity_date")
            .all()
        )

        dates = sorted(
            normalized
            for normalized in (self._coerce_activity_date(row[0]) for row in sessions)
            if normalized is not None
        )
        active_days_7 = sum(1 for activity_date in dates if activity_date >= today - timedelta(days=6))
        active_days_30 = sum(1 for activity_date in dates if activity_date >= today - timedelta(days=29))

        current_streak = 0
        longest_streak = 0

        if dates:
            streak = 1
            for i in range(1, len(dates)):
                if (dates[i] - dates[i - 1]).days == 1:
                    streak += 1
                else:
                    longest_streak = max(longest_streak, streak)
                    streak = 1
            longest_streak = max(longest_streak, streak)

            if dates[-1] == today:
                current_streak = 1
                cursor = today
                active_date_set = set(dates)
                while (cursor - timedelta(days=1)) in active_date_set:
                    current_streak += 1
                    cursor -= timedelta(days=1)

        # Measure consistency over the last eight weeks.
        recent_window_start = today - timedelta(days=55)
        weekly_buckets: dict[tuple[int, int], int] = {}
        for activity_date in dates:
            if activity_date < recent_window_start:
                continue
            iso_year, iso_week, _ = activity_date.isocalendar()
            weekly_buckets[(iso_year, iso_week)] = weekly_buckets.get((iso_year, iso_week), 0) + 1

        weekly_counts = list(weekly_buckets.values()) or [0]
        weekly_stddev = statistics.pstdev(weekly_counts) if len(weekly_counts) > 1 else 0.0
        weekly_consistency_ratio = max(0.0, 1.0 - min(1.0, weekly_stddev / 7.0))

        return {
            "active_days_last_7": active_days_7,
            "active_days_last_30": active_days_30,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "weekly_consistency_ratio": round(weekly_consistency_ratio, 4),
        }

    # ========================= PROGRESSION METRICS =========================

    def calculate_progression_metrics(self, student_id: int) -> dict:
        """Calculate learning velocity and progression indicators."""
        now = datetime.now(timezone.utc)
        previous_period_start = now - timedelta(days=60)
        previous_period_end = now - timedelta(days=30)
        recent_period_start = now - timedelta(days=30)

        previous_metrics = self.calculate_success_metrics(
            student_id, previous_period_start, previous_period_end
        )
        recent_metrics = self.calculate_success_metrics(
            student_id, recent_period_start, now
        )

        previous_difficulty = self.calculate_difficulty_metrics(
            student_id, previous_period_start, previous_period_end
        )
        recent_difficulty = self.calculate_difficulty_metrics(
            student_id, recent_period_start, now
        )

        attempt_efficiency_delta = 0.0
        if previous_metrics["average_attempts_to_solve"] > 0:
            attempt_efficiency_delta = (
                previous_metrics["average_attempts_to_solve"]
                - recent_metrics["average_attempts_to_solve"]
            )

        solve_rate_delta = (
            recent_metrics["solve_rate"] - previous_metrics["solve_rate"]
        )

        solve_time_improvement_minutes = 0.0  # Would need timing data

        difficulty_progression_delta = (
            recent_difficulty["weighted_difficulty"]
            - previous_difficulty["weighted_difficulty"]
        )

        return {
            "attempt_efficiency_delta": attempt_efficiency_delta,
            "solve_rate_delta": solve_rate_delta,
            "solve_time_improvement_minutes": solve_time_improvement_minutes,
            "difficulty_progression_delta": difficulty_progression_delta,
        }

    # ========================= COMPREHENSIVE PROFILE =========================

    def build_behavior_profile(self, student_id: int, date_range_days: int = 30) -> dict:
        """Build a complete behavior profile for a student."""
        start_date = datetime.now(timezone.utc) - timedelta(days=date_range_days)
        end_date = datetime.now(timezone.utc)

        # Determine evidence status
        activity = self.calculate_activity_metrics(student_id, start_date, end_date)
        attempted = activity["problems_attempted"]

        if attempted == 0:
            evidence_status = "NO_DATA"
        elif attempted < 5:
            evidence_status = "LIMITED_DATA"
        else:
            evidence_status = "SUFFICIENT_DATA"

        return {
            "evidence_status": evidence_status,
            "activity": activity,
            "success": self.calculate_success_metrics(student_id, start_date, end_date),
            "debugging": self.calculate_debugging_metrics(student_id, start_date, end_date),
            "difficulty": self.calculate_difficulty_metrics(student_id, start_date, end_date),
            "topics": self.calculate_topic_metrics(student_id, start_date, end_date),
            "consistency": self.calculate_consistency_metrics(student_id),
            "progression": self.calculate_progression_metrics(student_id),
        }
