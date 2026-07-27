from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.assessment import Assessment, AssessmentAttempt, AssessmentQuestion, AssessmentResult
from app.models.user import User, UserRole
from app.schemas.assessment import (
    AssessmentDetailResponse, AssessmentHistoryItem, AssessmentHistoryResponse,
    AssessmentQuestionResponse, AssessmentResponse, AssessmentResultResponse,
    PerformanceAnalysis, StartAssessmentResponse, SubmitAssessmentRequest,
)

router = APIRouter(prefix="/student/assessments", tags=["student-assessments"])


@router.get("", response_model=list[AssessmentResponse])
def list_assessments(
    assessment_type: str | None = Query(None),
    difficulty: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    query = db.query(Assessment).filter(Assessment.is_active.is_(True))
    if assessment_type:
        query = query.filter(Assessment.assessment_type == assessment_type)
    if difficulty:
        query = query.filter(Assessment.difficulty == difficulty)
    return query.order_by(Assessment.created_at.desc()).all()


@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id, Assessment.is_active.is_(True)).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).order_by(AssessmentQuestion.order_index).all()
    return AssessmentDetailResponse(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        assessment_type=assessment.assessment_type,
        difficulty=assessment.difficulty,
        time_limit_minutes=assessment.time_limit_minutes,
        passing_score=assessment.passing_score,
        total_questions=assessment.total_questions,
        questions=[AssessmentQuestionResponse(
            id=q.id,
            question_type=q.question_type,
            question_text=q.question_text,
            options=q.options,
            points=q.points,
            order_index=q.order_index,
        ) for q in questions],
    )


@router.post("/{assessment_id}/start", response_model=StartAssessmentResponse)
def start_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id, Assessment.is_active.is_(True)).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Check for incomplete attempt
    existing = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.student_id == current_user.id,
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.is_completed.is_(False),
    ).first()
    if existing:
        questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).order_by(AssessmentQuestion.order_index).all()
        return StartAssessmentResponse(
            attempt_id=existing.id,
            started_at=existing.started_at,
            time_limit_minutes=assessment.time_limit_minutes,
            questions=[AssessmentQuestionResponse(
                id=q.id, question_type=q.question_type, question_text=q.question_text,
                options=q.options, points=q.points, order_index=q.order_index,
            ) for q in questions],
        )

    attempt = AssessmentAttempt(student_id=current_user.id, assessment_id=assessment_id)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).order_by(AssessmentQuestion.order_index).all()
    return StartAssessmentResponse(
        attempt_id=attempt.id,
        started_at=attempt.started_at,
        time_limit_minutes=assessment.time_limit_minutes,
        questions=[AssessmentQuestionResponse(
            id=q.id, question_type=q.question_type, question_text=q.question_text,
            options=q.options, points=q.points, order_index=q.order_index,
        ) for q in questions],
    )


@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
def submit_assessment(
    assessment_id: int,
    payload: SubmitAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.student_id == current_user.id,
        AssessmentAttempt.assessment_id == assessment_id,
        AssessmentAttempt.is_completed.is_(False),
    ).order_by(AssessmentAttempt.started_at.desc()).first()
    if not attempt:
        raise HTTPException(status_code=400, detail="No active attempt found. Start the assessment first.")

    # Evaluate answers
    total_points = 0
    earned_points = 0
    results = []

    for answer in payload.answers:
        question = db.query(AssessmentQuestion).filter(AssessmentQuestion.id == answer.question_id).first()
        if not question:
            continue

        total_points += question.points
        is_correct = question.correct_answer and question.correct_answer.strip().lower() == answer.answer.strip().lower()
        if is_correct:
            earned_points += question.points

        result = AssessmentResult(
            attempt_id=attempt.id,
            question_id=question.id,
            student_answer=answer.answer,
            is_correct=is_correct,
            points_earned=question.points if is_correct else 0,
            feedback="Correct!" if is_correct else f"Incorrect. Expected: {question.correct_answer}",
        )
        db.add(result)
        results.append({
            "question_id": question.id,
            "question_text": question.question_text,
            "student_answer": answer.answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "points_earned": question.points if is_correct else 0,
            "feedback": result.feedback,
        })

    score = (earned_points / max(total_points, 1)) * 100
    passed = score >= assessment.passing_score
    now = datetime.now(timezone.utc)
    time_taken = int((now - attempt.started_at).total_seconds())

    attempt.score = score
    attempt.passed = passed
    attempt.submitted_at = now
    attempt.time_taken_seconds = time_taken
    attempt.is_completed = True
    db.commit()

    return AssessmentResultResponse(
        attempt_id=attempt.id,
        score=score,
        passed=passed,
        total_questions=len(payload.answers),
        correct_answers=sum(1 for r in results if r["is_correct"]),
        time_taken_seconds=time_taken,
        submitted_at=now,
        results=results,
    )


@router.get("/results/history", response_model=AssessmentHistoryResponse)
def get_assessment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.student_id == current_user.id,
        AssessmentAttempt.is_completed.is_(True),
    ).order_by(AssessmentAttempt.submitted_at.desc()).all()

    items = []
    for attempt in attempts:
        assessment = db.query(Assessment).filter(Assessment.id == attempt.assessment_id).first()
        items.append(AssessmentHistoryItem(
            attempt_id=attempt.id,
            assessment_id=attempt.assessment_id,
            assessment_title=assessment.title if assessment else "Unknown",
            score=attempt.score,
            passed=attempt.passed,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
        ))

    return AssessmentHistoryResponse(items=items)


@router.get("/results/{attempt_id}", response_model=AssessmentResultResponse)
def get_assessment_result(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.id == attempt_id,
        AssessmentAttempt.student_id == current_user.id,
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Result not found")

    results = db.query(AssessmentResult).filter(AssessmentResult.attempt_id == attempt_id).all()
    return AssessmentResultResponse(
        attempt_id=attempt.id,
        score=attempt.score or 0.0,
        passed=attempt.passed,
        total_questions=len(results),
        correct_answers=sum(1 for r in results if r.is_correct),
        time_taken_seconds=attempt.time_taken_seconds,
        submitted_at=attempt.submitted_at,
        results=[{
            "question_id": r.question_id,
            "student_answer": r.student_answer,
            "is_correct": r.is_correct,
            "points_earned": r.points_earned,
            "feedback": r.feedback,
        } for r in results],
    )


@router.get("/performance/analysis", response_model=PerformanceAnalysis)
def get_performance_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.student_id == current_user.id,
        AssessmentAttempt.is_completed.is_(True),
    ).all()

    if not attempts:
        return PerformanceAnalysis()

    total = len(attempts)
    avg_score = sum(a.score or 0 for a in attempts) / total
    passed_count = sum(1 for a in attempts if a.passed)
    pass_rate = (passed_count / total) * 100

    # Determine strengths/weaknesses based on results
    mcq_correct = 0
    mcq_total = 0
    for attempt in attempts:
        results = db.query(AssessmentResult).filter(AssessmentResult.attempt_id == attempt.id).all()
        questions = [db.query(AssessmentQuestion).filter(AssessmentQuestion.id == r.question_id).first() for r in results]
        for r, q in zip(results, questions):
            if q and q.question_type == "MCQ":
                mcq_total += 1
                if r.is_correct:
                    mcq_correct += 1

    strengths = []
    weaknesses = []
    if mcq_total > 0:
        mcq_rate = (mcq_correct / mcq_total) * 100
        if mcq_rate >= 70:
            strengths.append("Multiple Choice Questions")
        else:
            weaknesses.append("Multiple Choice Questions")

    recommendations = [
        "Practice more coding questions to improve problem-solving skills",
        "Review fundamental concepts in weaker areas",
        "Take timed assessments to improve speed and accuracy",
    ]

    return PerformanceAnalysis(
        total_assessments=total,
        average_score=round(avg_score, 2),
        pass_rate=round(pass_rate, 2),
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
    )

