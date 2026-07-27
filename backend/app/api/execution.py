from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.models.execution import CodingSession, Submission, SubmissionVerdict
from app.schemas.execution import CodingSessionStartResponse, ExecutionRequest, RunCodeResponse, SubmitCodeResponse, SubmissionDetailResponse, SubmissionListItem
from app.services.execution_service import ExecutionService

router = APIRouter(tags=["execution"])


def _get_active_session(db: Session, student_id: int, problem_id: int) -> CodingSession | None:
    return (
        db.query(CodingSession)
        .filter(CodingSession.student_id == student_id, CodingSession.problem_id == problem_id, CodingSession.ended_at.is_(None))
        .order_by(CodingSession.started_at.desc())
        .first()
    )


@router.post("/execution/run", response_model=RunCodeResponse)
def run_code(
    payload: ExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    service = ExecutionService(db, current_user)
    try:
        problem = service.validate_problem(payload.problem_id)
        language = service.validate_language(payload.language)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    if payload.source_code and len(payload.source_code) > 40000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Source code is too large")

    result = service.run_sample_tests(problem, language, payload.source_code)
    session = _get_active_session(db, current_user.id, problem.id)
    if session is None:
        session = CodingSession(student_id=current_user.id, problem_id=problem.id, language=language)
        db.add(session)
        db.flush()
    session.run_count += 1
    session.last_activity_at = None
    db.commit()
    service.record_behavior_event(db, problem, "RUN_CODE", {"passed_tests": result["passed"], "total_tests": result["total"]}, language)
    return RunCodeResponse(**result)


@router.post("/execution/submit", response_model=SubmitCodeResponse)
def submit_code(
    payload: ExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    service = ExecutionService(db, current_user)
    try:
        problem = service.validate_problem(payload.problem_id)
        language = service.validate_language(payload.language)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    if payload.source_code and len(payload.source_code) > 40000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Source code is too large")

    submission_count = db.query(Submission).filter(Submission.student_id == current_user.id, Submission.problem_id == problem.id).count()
    submission_result = service.run_submission(problem, language, payload.source_code)
    attempt_number = submission_count + 1
    verdict = submission_result["verdict"]
    submission = Submission(
        student_id=current_user.id,
        problem_id=problem.id,
        language=language,
        source_code=payload.source_code,
        verdict=SubmissionVerdict(verdict),
        passed_test_cases=submission_result["passed_test_cases"],
        total_test_cases=submission_result["total_test_cases"],
        runtime_ms=submission_result.get("runtime_ms"),
        memory_kb=submission_result.get("memory_kb"),
        attempt_number=attempt_number,
        error_type=verdict,
    )
    db.add(submission)

    session = _get_active_session(db, current_user.id, problem.id)
    if session is None:
        session = CodingSession(student_id=current_user.id, problem_id=problem.id, language=language)
        db.add(session)
        db.flush()
    session.submit_count += 1
    session.last_activity_at = None
    session.is_solved = verdict == "ACCEPTED"
    db.commit()
    db.refresh(submission)
    service.record_behavior_event(db, problem, "SUBMIT_CODE", {"passed_tests": submission_result["passed_test_cases"], "total_tests": submission_result["total_test_cases"], "attempt_number": attempt_number}, language)
    return SubmitCodeResponse(
        submission_id=submission.id,
        verdict=verdict,
        passed_test_cases=submission_result["passed_test_cases"],
        total_test_cases=submission_result["total_test_cases"],
        runtime_ms=submission_result.get("runtime_ms"),
        memory_kb=submission_result.get("memory_kb"),
        attempt_number=attempt_number,
        message="All evaluation tests passed." if verdict == "ACCEPTED" else f"{submission_result['passed_test_cases']} of {submission_result['total_test_cases']} evaluation tests passed.",
    )


@router.post("/coding-sessions/start", response_model=CodingSessionStartResponse)
def start_coding_session(
    payload: ExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    problem = db.query(Problem).filter(Problem.id == payload.problem_id, Problem.is_active.is_(True)).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    session = _get_active_session(db, current_user.id, problem.id)
    if session is None:
        session = CodingSession(student_id=current_user.id, problem_id=problem.id, language=payload.language)
        db.add(session)
        db.commit()
        db.refresh(session)
        return CodingSessionStartResponse(session_id=session.id, started_at=session.started_at, resumed=False)
    return CodingSessionStartResponse(session_id=session.id, started_at=session.started_at, resumed=True)


@router.get("/submissions/me", response_model=dict)
def list_my_submissions(
    page: int = 1,
    page_size: int = 10,
    problem_id: int | None = None,
    verdict: str | None = None,
    language: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 50), 1)
    query = db.query(Submission).filter(Submission.student_id == current_user.id)
    if problem_id is not None:
        query = query.filter(Submission.problem_id == problem_id)
    if verdict:
        query = query.filter(Submission.verdict == SubmissionVerdict(verdict))
    if language:
        query = query.filter(Submission.language == language.lower())
    total = query.count()
    items = query.order_by(Submission.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    payload = []
    for submission in items:
        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
        payload.append(
            SubmissionListItem(
                submission_id=submission.id,
                problem_id=submission.problem_id,
                problem_title=problem.title if problem else "Unknown",
                language=submission.language,
                verdict=submission.verdict.value,
                passed_test_cases=submission.passed_test_cases,
                total_test_cases=submission.total_test_cases,
                runtime_ms=submission.runtime_ms,
                memory_kb=submission.memory_kb,
                attempt_number=submission.attempt_number,
                created_at=submission.created_at,
            )
        )
    return {"items": payload, "page": page, "page_size": page_size, "total": total, "total_pages": max((total + page_size - 1) // page_size, 1)}


@router.get("/problems/{problem_id}/submissions/me", response_model=list[SubmissionListItem])
def list_problem_submissions(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    submissions = (
        db.query(Submission)
        .filter(Submission.student_id == current_user.id, Submission.problem_id == problem_id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    return [
        SubmissionListItem(
            submission_id=submission.id,
            problem_id=submission.problem_id,
            problem_title=problem.title if problem else "Unknown",
            language=submission.language,
            verdict=submission.verdict.value,
            passed_test_cases=submission.passed_test_cases,
            total_test_cases=submission.total_test_cases,
            runtime_ms=submission.runtime_ms,
            memory_kb=submission.memory_kb,
            attempt_number=submission.attempt_number,
            created_at=submission.created_at,
        )
        for submission in submissions
    ]


@router.get("/submissions/{submission_id}", response_model=SubmissionDetailResponse)
def get_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
    return SubmissionDetailResponse(
        submission_id=submission.id,
        problem_id=submission.problem_id,
        problem_title=problem.title if problem else "Unknown",
        language=submission.language,
        verdict=submission.verdict.value,
        passed_test_cases=submission.passed_test_cases,
        total_test_cases=submission.total_test_cases,
        runtime_ms=submission.runtime_ms,
        memory_kb=submission.memory_kb,
        attempt_number=submission.attempt_number,
        source_code=submission.source_code,
        created_at=submission.created_at,
    )
