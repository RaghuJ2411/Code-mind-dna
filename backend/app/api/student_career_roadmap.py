from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.career_roadmap import CareerRoadmap, RoadmapMilestone, WeeklyGoal, MonthlyGoal
from app.models.user import User, UserRole
from app.schemas.career_roadmap import (
    AISuggestionResponse, CareerRoadmapCreate, CareerRoadmapResponse,
    MonthlyGoalCreate, MonthlyGoalResponse, RoadmapMilestoneCreate,
    RoadmapMilestoneResponse, RoadmapMilestoneUpdate, WeeklyGoalCreate,
    WeeklyGoalResponse,
)

router = APIRouter(prefix="/student/career-roadmap", tags=["student-career-roadmap"])


@router.get("", response_model=CareerRoadmapResponse | None)
def get_roadmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_id == current_user.id,
        CareerRoadmap.is_active.is_(True),
    ).order_by(CareerRoadmap.created_at.desc()).first()

    if not roadmap:
        return None

    milestones = db.query(RoadmapMilestone).filter(
        RoadmapMilestone.roadmap_id == roadmap.id,
    ).order_by(RoadmapMilestone.order_index).all()

    return CareerRoadmapResponse(
        id=roadmap.id,
        career_goal=roadmap.career_goal,
        company_goal=roadmap.company_goal,
        target_role=roadmap.target_role,
        target_seniority=roadmap.target_seniority,
        timeline_months=roadmap.timeline_months,
        skills_required=roadmap.skills_required,
        current_skills=roadmap.current_skills,
        gap_analysis=roadmap.gap_analysis,
        ai_suggestions=roadmap.ai_suggestions,
        milestones=[
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "milestone_type": m.milestone_type,
                "target_date": str(m.target_date) if m.target_date else None,
                "is_completed": m.is_completed,
                "progress_pct": m.progress_pct,
                "order_index": m.order_index,
            }
            for m in milestones
        ],
        is_active=roadmap.is_active,
        created_at=roadmap.created_at,
    )


@router.post("", response_model=CareerRoadmapResponse, status_code=status.HTTP_201_CREATED)
def create_roadmap(
    payload: CareerRoadmapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    roadmap = CareerRoadmap(
        student_id=current_user.id,
        career_goal=payload.career_goal,
        company_goal=payload.company_goal,
        target_role=payload.target_role,
        target_seniority=payload.target_seniority,
        timeline_months=payload.timeline_months,
        skills_required=payload.skills_required,
        current_skills=payload.current_skills,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return CareerRoadmapResponse(
        id=roadmap.id,
        career_goal=roadmap.career_goal,
        company_goal=roadmap.company_goal,
        target_role=roadmap.target_role,
        target_seniority=roadmap.target_seniority,
        timeline_months=roadmap.timeline_months,
        skills_required=roadmap.skills_required,
        current_skills=roadmap.current_skills,
        is_active=roadmap.is_active,
        created_at=roadmap.created_at,
    )


@router.put("/{roadmap_id}", response_model=CareerRoadmapResponse)
def update_roadmap(
    roadmap_id: int,
    payload: CareerRoadmapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.id == roadmap_id,
        CareerRoadmap.student_id == current_user.id,
    ).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    roadmap.career_goal = payload.career_goal
    roadmap.company_goal = payload.company_goal
    roadmap.target_role = payload.target_role
    roadmap.target_seniority = payload.target_seniority
    roadmap.timeline_months = payload.timeline_months
    roadmap.skills_required = payload.skills_required
    roadmap.current_skills = payload.current_skills
    db.commit()
    db.refresh(roadmap)
    return CareerRoadmapResponse(
        id=roadmap.id,
        career_goal=roadmap.career_goal,
        company_goal=roadmap.company_goal,
        target_role=roadmap.target_role,
        target_seniority=roadmap.target_seniority,
        timeline_months=roadmap.timeline_months,
        skills_required=roadmap.skills_required,
        current_skills=roadmap.current_skills,
        is_active=roadmap.is_active,
        created_at=roadmap.created_at,
    )


@router.post("/{roadmap_id}/milestones", response_model=RoadmapMilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(
    roadmap_id: int,
    payload: RoadmapMilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.id == roadmap_id,
        CareerRoadmap.student_id == current_user.id,
    ).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    milestone = RoadmapMilestone(
        roadmap_id=roadmap_id,
        title=payload.title,
        description=payload.description,
        milestone_type=payload.milestone_type,
        target_date=payload.target_date,
        order_index=payload.order_index,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return RoadmapMilestoneResponse(
        id=milestone.id,
        roadmap_id=milestone.roadmap_id,
        title=milestone.title,
        description=milestone.description,
        milestone_type=milestone.milestone_type,
        target_date=milestone.target_date,
        is_completed=milestone.is_completed,
        completed_at=milestone.completed_at,
        progress_pct=milestone.progress_pct,
        order_index=milestone.order_index,
    )


@router.put("/milestones/{milestone_id}", response_model=RoadmapMilestoneResponse)
def update_milestone(
    milestone_id: int,
    payload: RoadmapMilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    milestone = db.query(RoadmapMilestone).filter(RoadmapMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.id == milestone.roadmap_id,
        CareerRoadmap.student_id == current_user.id,
    ).first()
    if not roadmap:
        raise HTTPException(status_code=403, detail="Access denied")

    if payload.progress_pct is not None:
        milestone.progress_pct = payload.progress_pct
    if payload.is_completed is not None:
        milestone.is_completed = payload.is_completed
        if payload.is_completed:
            milestone.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(milestone)
    return RoadmapMilestoneResponse(
        id=milestone.id,
        roadmap_id=milestone.roadmap_id,
        title=milestone.title,
        description=milestone.description,
        milestone_type=milestone.milestone_type,
        target_date=milestone.target_date,
        is_completed=milestone.is_completed,
        completed_at=milestone.completed_at,
        progress_pct=milestone.progress_pct,
        order_index=milestone.order_index,
    )


@router.get("/ai-suggestions", response_model=AISuggestionResponse)
def get_ai_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    roadmap = db.query(CareerRoadmap).filter(
        CareerRoadmap.student_id == current_user.id,
        CareerRoadmap.is_active.is_(True),
    ).first()

    if not roadmap:
        return AISuggestionResponse(
            suggestions=["Set your career goal to get personalized suggestions"],
            next_steps=["Create a career roadmap to begin"],
            resources=["Browse available courses and skill paths"],
        )

    suggestions = []
    if roadmap.gap_analysis:
        gaps = roadmap.gap_analysis if isinstance(roadmap.gap_analysis, dict) else {}
        for skill, status in gaps.items():
            if status == "missing":
                suggestions.append(f"Focus on learning {skill} which is required for your goal")

    return AISuggestionResponse(
        suggestions=suggestions or [
            f"Complete skill-building for {roadmap.career_goal}",
            "Practice more coding problems in required topics",
            "Build projects to demonstrate your skills",
        ],
        next_steps=[
            "Complete your current milestones",
            "Review and update your skills list",
            "Prepare for interviews with mock practice",
        ],
        resources=[
            "Recommended courses for your career path",
            "Practice problems matching your target role",
            "Interview preparation materials",
        ],
    )


@router.get("/weekly-goals", response_model=list[WeeklyGoalResponse])
def list_weekly_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return db.query(WeeklyGoal).filter(
        WeeklyGoal.student_id == current_user.id,
    ).order_by(WeeklyGoal.week_start.desc()).all()


@router.post("/weekly-goals", response_model=WeeklyGoalResponse, status_code=status.HTTP_201_CREATED)
def create_weekly_goal(
    payload: WeeklyGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    goal = WeeklyGoal(
        student_id=current_user.id,
        title=payload.title,
        description=payload.description,
        week_start=payload.week_start,
        week_end=payload.week_end,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return WeeklyGoalResponse(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        week_start=goal.week_start,
        week_end=goal.week_end,
        is_completed=goal.is_completed,
        completed_at=goal.completed_at,
    )


@router.get("/monthly-goals", response_model=list[MonthlyGoalResponse])
def list_monthly_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return db.query(MonthlyGoal).filter(
        MonthlyGoal.student_id == current_user.id,
    ).order_by(MonthlyGoal.month.desc()).all()


@router.post("/monthly-goals", response_model=MonthlyGoalResponse, status_code=status.HTTP_201_CREATED)
def create_monthly_goal(
    payload: MonthlyGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    goal = MonthlyGoal(
        student_id=current_user.id,
        title=payload.title,
        description=payload.description,
        month=payload.month,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return MonthlyGoalResponse(
        id=goal.id,
        title=goal.title,
        description=goal.description,
        month=goal.month,
        is_completed=goal.is_completed,
        completed_at=goal.completed_at,
    )

