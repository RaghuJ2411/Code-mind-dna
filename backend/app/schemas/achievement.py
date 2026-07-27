from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    badge_icon: str | None = None
    category: str
    criteria_type: str
    criteria_value: int
    xp_reward: int
    earned: bool = False
    earned_at: datetime | None = None

    class Config:
        from_attributes = True


class StudentAchievementResponse(BaseModel):
    id: int
    achievement_id: int
    achievement_name: str
    badge_icon: str | None = None
    category: str
    earned_at: datetime
    is_displayed: bool

    class Config:
        from_attributes = True


class CodingMilestoneResponse(BaseModel):
    id: int
    milestone_type: str
    current_value: int
    target_value: int
    achieved: bool
    achieved_at: datetime | None = None

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    student_name: str
    score: float
    achievements_count: int
    problems_solved: int


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry] = Field(default_factory=list)

