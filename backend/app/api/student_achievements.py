from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.achievement import Achievement, CodingMilestone, StudentAchievement
from app.models.execution import Submission, SubmissionVerdict
from app.models.user import User, UserRole
from app.schemas.achievement import (
    AchievementResponse, CodingMilestoneResponse, LeaderboardEntry,
    LeaderboardResponse, StudentAchievementResponse,
)

router = APIRouter(prefix="/student/achievements", tags=["student-achievements"])


@router.get("", response_model=list[AchievementResponse])
def list_achievements(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    query = db.query(Achievement).filter(Achievement.is_active.is_(True))
    if category:
        query = query.filter(Achievement.category == category)

    achievements = query.order_by(Achievement.category, Achievement.criteria_value).all()
    earned = {
        sa.achievement_id: sa.earned_at
        for sa in db.query(StudentAchievement).filter(StudentAchievement.student_id == current_user.id).all()
    }

    return [
        AchievementResponse(
            id=a.id,
            name=a.name,
            description=a.description,
            badge_icon=a.badge_icon,
            category=a.category,
            criteria_type=a.criteria_type,
            criteria_value=a.criteria_value,
            xp_reward=a.xp_reward,
            earned=a.id in earned,
            earned_at=earned.get(a.id),
        )
        for a in achievements
    ]


@router.get("/earned", response_model=list[StudentAchievementResponse])
def list_earned_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    earned = (
        db.query(StudentAchievement)
        .filter(StudentAchievement.student_id == current_user.id)
        .order_by(StudentAchievement.earned_at.desc())
        .all()
    )
    result = []
    for e in earned:
        achievement = db.query(Achievement).filter(Achievement.id == e.achievement_id).first()
        result.append(StudentAchievementResponse(
            id=e.id,
            achievement_id=e.achievement_id,
            achievement_name=achievement.name if achievement else "Unknown",
            badge_icon=achievement.badge_icon if achievement else None,
            category=achievement.category if achievement else "OTHER",
            earned_at=e.earned_at,
            is_displayed=e.is_displayed,
        ))
    return result


@router.get("/milestones", response_model=list[CodingMilestoneResponse])
def list_milestones(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    milestones = db.query(CodingMilestone).filter(
        CodingMilestone.student_id == current_user.id
    ).order_by(CodingMilestone.created_at.desc()).all()
    return [
        CodingMilestoneResponse(
            id=m.id,
            milestone_type=m.milestone_type,
            current_value=m.current_value,
            target_value=m.target_value,
            achieved=m.achieved,
            achieved_at=m.achieved_at,
        )
        for m in milestones
    ]


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    # Get top students by problems solved
    top_students = (
        db.query(
            Submission.student_id,
            User.full_name,
            Submission.student_id,
        )
        .join(User, Submission.student_id == User.id)
        .filter(Submission.verdict == SubmissionVerdict.ACCEPTED)
        .group_by(Submission.student_id, User.full_name)
        .order_by(__import__("sqlalchemy").func.count(Submission.id).desc())
        .limit(limit)
        .all()
    )

    entries = []
    for rank, (student_id, full_name, _) in enumerate(top_students, 1):
        solved = db.query(Submission).filter(
            Submission.student_id == student_id,
            Submission.verdict == SubmissionVerdict.ACCEPTED,
        ).count()
        achievements_count = db.query(StudentAchievement).filter(
            StudentAchievement.student_id == student_id
        ).count()

        # Calculate score based on solved problems and achievements
        score = solved * 10 + achievements_count * 50

        entries.append(LeaderboardEntry(
            rank=rank,
            student_id=student_id,
            student_name=full_name,
            score=score,
            achievements_count=achievements_count,
            problems_solved=solved,
        ))

    return LeaderboardResponse(entries=entries)

