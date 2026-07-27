"""
Data Quality Service

Validates and ensures consistency of analytics data.
Detects anomalies and data quality issues.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.execution import Submission, SubmissionVerdict


class DataQualityService:
    """Validate and monitor analytics data quality."""

    def __init__(self, db: Session):
        self.db = db

    def validate_daily_analytics(self, daily: StudentDailyAnalytics) -> dict:
        """Validate a daily analytics record for logical consistency."""
        issues = []
        warnings = []

        # Check logical relationships
        if daily.problems_solved > daily.problems_attempted:
            issues.append("problems_solved cannot exceed problems_attempted")

        if daily.easy_solved > daily.easy_attempted:
            issues.append("easy_solved cannot exceed easy_attempted")
        if daily.medium_solved > daily.medium_attempted:
            issues.append("medium_solved cannot exceed medium_attempted")
        if daily.hard_solved > daily.hard_attempted:
            issues.append("hard_solved cannot exceed hard_attempted")

        # Check negative values
        for field in [
            "problems_attempted",
            "problems_solved",
            "submissions_count",
            "runs_count",
            "active_minutes",
        ]:
            if getattr(daily, field) < 0:
                issues.append(f"{field} cannot be negative")

        # Check reasonable ranges
        if daily.active_minutes > 1440:  # More than 24 hours
            warnings.append("active_minutes exceeds 24 hours (unusual)")

        if daily.submissions_count > 1000:
            warnings.append("submissions_count is unusually high")

        # Check consistency with error counts
        if (
            daily.wrong_answer_count
            + daily.compilation_error_count
            + daily.runtime_error_count
            + daily.time_limit_count
            > daily.submissions_count
        ):
            issues.append(
                "sum of error counts cannot exceed submissions_count"
            )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

    def validate_weekly_analytics(self, weekly: StudentWeeklyAnalytics) -> dict:
        """Validate a weekly analytics record for logical consistency."""
        issues = []
        warnings = []

        # Check logical relationships
        if weekly.problems_solved > weekly.problems_attempted:
            issues.append("problems_solved cannot exceed problems_attempted")

        if weekly.solve_rate < 0.0 or weekly.solve_rate > 1.0:
            issues.append("solve_rate must be between 0 and 1")

        for field in ["easy_solve_rate", "medium_solve_rate", "hard_solve_rate"]:
            value = getattr(weekly, field)
            if value < 0.0 or value > 1.0:
                issues.append(f"{field} must be between 0 and 1")

        # Check negative values
        for field in [
            "problems_attempted",
            "problems_solved",
            "submissions_count",
            "runs_count",
            "active_minutes",
            "active_days",
        ]:
            if getattr(weekly, field) < 0:
                issues.append(f"{field} cannot be negative")

        # Check reasonable ranges
        if weekly.active_days > 7:
            issues.append("active_days cannot exceed 7 for a week")

        if weekly.active_minutes > 10080:  # More than 7*24 hours
            warnings.append("active_minutes exceeds 7 days (unusual)")

        # Check consistency: if problems_attempted > 0, solve_rate should match
        if weekly.problems_attempted > 0:
            calculated_solve_rate = weekly.problems_solved / weekly.problems_attempted
            if abs(calculated_solve_rate - weekly.solve_rate) > 0.01:
                issues.append(
                    f"solve_rate inconsistent: calculated {calculated_solve_rate:.2f}, "
                    f"but got {weekly.solve_rate:.2f}"
                )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

    def detect_anomalies_in_daily(self, student_id: int, num_days: int = 7) -> dict:
        """Detect anomalies in recent daily analytics."""
        recent_records = (
            self.db.query(StudentDailyAnalytics)
            .filter(StudentDailyAnalytics.student_id == student_id)
            .order_by(StudentDailyAnalytics.analytics_date.desc())
            .limit(num_days)
            .all()
        )

        anomalies = []

        if not recent_records:
            return {"anomalies": anomalies}

        # Calculate statistics
        active_minutes = [r.active_minutes for r in recent_records]
        submissions = [r.submissions_count for r in recent_records]

        avg_minutes = sum(active_minutes) / len(active_minutes) if active_minutes else 0
        avg_submissions = sum(submissions) / len(submissions) if submissions else 0

        # Standard deviation approximation
        if avg_minutes > 0:
            std_minutes = (
                sum((x - avg_minutes) ** 2 for x in active_minutes) / len(active_minutes)
            ) ** 0.5
        else:
            std_minutes = 0

        if avg_submissions > 0:
            std_submissions = (
                sum((x - avg_submissions) ** 2 for x in submissions)
                / len(submissions)
            ) ** 0.5
        else:
            std_submissions = 0

        # Check for outliers (> 2 std devs from mean)
        for record in recent_records:
            if std_minutes > 0 and abs(record.active_minutes - avg_minutes) > 2 * std_minutes:
                anomalies.append(
                    {
                        "date": record.analytics_date.isoformat(),
                        "type": "active_minutes_outlier",
                        "value": record.active_minutes,
                        "avg": avg_minutes,
                    }
                )

            if (
                std_submissions > 0
                and abs(record.submissions_count - avg_submissions)
                > 2 * std_submissions
            ):
                anomalies.append(
                    {
                        "date": record.analytics_date.isoformat(),
                        "type": "submissions_outlier",
                        "value": record.submissions_count,
                        "avg": avg_submissions,
                    }
                )

            # Check for suspiciously high error rate
            total_errors = (
                record.wrong_answer_count
                + record.compilation_error_count
                + record.runtime_error_count
                + record.time_limit_count
            )
            if record.submissions_count > 0:
                error_rate = total_errors / record.submissions_count
                if error_rate > 0.9:
                    anomalies.append(
                        {
                            "date": record.analytics_date.isoformat(),
                            "type": "high_error_rate",
                            "value": error_rate,
                        }
                    )

        return {"anomalies": anomalies}

    def validate_all_student_analytics(self, student_id: int) -> dict:
        """Run all validation checks on a student's analytics."""
        daily_records = (
            self.db.query(StudentDailyAnalytics)
            .filter(StudentDailyAnalytics.student_id == student_id)
            .all()
        )

        weekly_records = (
            self.db.query(StudentWeeklyAnalytics)
            .filter(StudentWeeklyAnalytics.student_id == student_id)
            .all()
        )

        daily_issues = []
        daily_warnings = []
        for record in daily_records:
            validation = self.validate_daily_analytics(record)
            if validation["issues"]:
                daily_issues.append(
                    {
                        "date": record.analytics_date.isoformat(),
                        "issues": validation["issues"],
                    }
                )
            if validation["warnings"]:
                daily_warnings.append(
                    {
                        "date": record.analytics_date.isoformat(),
                        "warnings": validation["warnings"],
                    }
                )

        weekly_issues = []
        weekly_warnings = []
        for record in weekly_records:
            validation = self.validate_weekly_analytics(record)
            if validation["issues"]:
                weekly_issues.append(
                    {
                        "week": record.week_start.isoformat(),
                        "issues": validation["issues"],
                    }
                )
            if validation["warnings"]:
                weekly_warnings.append(
                    {
                        "week": record.week_start.isoformat(),
                        "warnings": validation["warnings"],
                    }
                )

        anomalies = self.detect_anomalies_in_daily(student_id)

        return {
            "valid": len(daily_issues) == 0 and len(weekly_issues) == 0,
            "daily_issues": daily_issues,
            "daily_warnings": daily_warnings,
            "weekly_issues": weekly_issues,
            "weekly_warnings": weekly_warnings,
            "anomalies": anomalies["anomalies"],
        }

    def generate_quality_report(self) -> dict:
        """Generate a data quality report for all students."""
        all_daily = self.db.query(StudentDailyAnalytics).all()
        all_weekly = self.db.query(StudentWeeklyAnalytics).all()

        daily_valid = sum(
            1 for record in all_daily
            if self.validate_daily_analytics(record)["valid"]
        )
        daily_total = len(all_daily)

        weekly_valid = sum(
            1 for record in all_weekly
            if self.validate_weekly_analytics(record)["valid"]
        )
        weekly_total = len(all_weekly)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "daily_records": {
                "total": daily_total,
                "valid": daily_valid,
                "invalid": daily_total - daily_valid,
                "validity_percentage": (daily_valid / daily_total * 100) if daily_total > 0 else 0,
            },
            "weekly_records": {
                "total": weekly_total,
                "valid": weekly_valid,
                "invalid": weekly_total - weekly_valid,
                "validity_percentage": (weekly_valid / weekly_total * 100) if weekly_total > 0 else 0,
            },
        }
