from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.analytics import StudentDailyAnalytics
from app.models.dna_profile import CodingDNAProfile
from app.models.execution import Submission, SubmissionVerdict
from app.models.mentor_alert import MentorRiskAlert
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.schemas.mentor import MentorIntelligenceResponse

router = APIRouter(prefix="/mentor/intelligence", tags=["mentor-intelligence"])


@router.get("/students", response_model=list[MentorIntelligenceResponse])
def list_student_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    results = []

    for student in students:
        # Get DNA profile
        dna = db.query(CodingDNAProfile).filter(
            CodingDNAProfile.student_id == student.id
        ).first()

        # Get solve rate
        total_submissions = db.query(Submission).filter(
            Submission.student_id == student.id
        ).count()
        accepted = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.verdict == SubmissionVerdict.ACCEPTED,
        ).count()
        solve_rate = (accepted / max(total_submissions, 1)) * 100

        # Get topic strengths/weaknesses
        strong_topics = []
        weak_topics = []
        skill_gaps = []

        # Find weak topics
        student_submissions = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.verdict != SubmissionVerdict.ACCEPTED,
        ).limit(5).all()
        for sub in student_submissions:
            if sub.problem_id:
                problem = db.query(Problem).filter(Problem.id == sub.problem_id).first()
                if problem and problem.topic:
                    weak_topics.append(problem.topic.value if hasattr(problem.topic, 'value') else str(problem.topic))

        # Find strong topics
        strong_subs = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.verdict == SubmissionVerdict.ACCEPTED,
        ).limit(5).all()
        for sub in strong_subs:
            if sub.problem_id:
                problem = db.query(Problem).filter(Problem.id == sub.problem_id).first()
                if problem and problem.topic:
                    strong_topics.append(problem.topic.value if hasattr(problem.topic, 'value') else str(problem.topic))

        # Risk assessment
        open_alerts = db.query(MentorRiskAlert).filter(
            MentorRiskAlert.student_id == student.id,
            MentorRiskAlert.status == "OPEN",
        ).count()
        risk_score = min(open_alerts * 20, 100)

        # Last active
        last_sub = db.query(Submission).filter(
            Submission.student_id == student.id
        ).order_by(Submission.created_at.desc()).first()

        # Engagement
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_activity = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.created_at >= thirty_days_ago,
        ).count()
        engagement = "HIGH" if recent_activity > 20 else "MODERATE" if recent_activity > 5 else "LOW"

        results.append(MentorIntelligenceResponse(
            student_id=student.id,
            student_name=student.full_name,
            coding_dna_score=dna.overall_score if dna else None,
            solve_rate=round(solve_rate, 2),
            skill_gaps=list(set(skill_gaps)),
            weak_topics=list(set(weak_topics)),
            strong_topics=list(set(strong_topics)),
            engagement_level=engagement,
            risk_score=risk_score,
            recommended_actions=_get_recommendations(risk_score, solve_rate, engagement),
            last_active=last_sub.created_at if last_sub else None,
        ))

    return results


@router.get("/{student_id}", response_model=MentorIntelligenceResponse)
def get_student_intelligence(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    student = db.query(User).filter(
        User.id == student_id,
        User.role == UserRole.STUDENT,
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    dna = db.query(CodingDNAProfile).filter(
        CodingDNAProfile.student_id == student.id
    ).first()

    total_submissions = db.query(Submission).filter(
        Submission.student_id == student.id
    ).count()
    accepted = db.query(Submission).filter(
        Submission.student_id == student.id,
        Submission.verdict == SubmissionVerdict.ACCEPTED,
    ).count()
    solve_rate = (accepted / max(total_submissions, 1)) * 100

    open_alerts = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.student_id == student.id,
        MentorRiskAlert.status == "OPEN",
    ).count()
    risk_score = min(open_alerts * 20, 100)

    last_sub = db.query(Submission).filter(
        Submission.student_id == student.id
    ).order_by(Submission.created_at.desc()).first()

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_activity = db.query(Submission).filter(
        Submission.student_id == student.id,
        Submission.created_at >= thirty_days_ago,
    ).count()
    engagement = "HIGH" if recent_activity > 20 else "MODERATE" if recent_activity > 5 else "LOW"

    return MentorIntelligenceResponse(
        student_id=student.id,
        student_name=student.full_name,
        coding_dna_score=dna.overall_score if dna else None,
        solve_rate=round(solve_rate, 2),
        skill_gaps=[],
        weak_topics=[],
        strong_topics=[],
        engagement_level=engagement,
        risk_score=risk_score,
        recommended_actions=_get_recommendations(risk_score, solve_rate, engagement),
        last_active=last_sub.created_at if last_sub else None,
    )


def _get_recommendations(risk_score: float, solve_rate: float, engagement: str) -> list[str]:
    recommendations = []
    if risk_score > 50:
        recommendations.append("High risk student - immediate intervention recommended")
        recommendations.append("Schedule one-on-one mentoring session")
    if solve_rate < 40:
        recommendations.append("Focus on fundamentals - recommend basic problem sets")
        recommendations.append("Review past mistakes and provide guided practice")
    if engagement == "LOW":
        recommendations.append("Student disengaged - send motivation and check-in message")
        recommendations.append("Assign smaller, achievable goals to rebuild momentum")
    if solve_rate >= 70:
        recommendations.append("Student performing well - consider advanced challenges")
    if not recommendations:
        recommendations.append("Continue monitoring - student is on track")
    return recommendations

