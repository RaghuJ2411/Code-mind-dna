from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.execution import Submission, SubmissionVerdict
from app.models.problem import CodeDraft, DifficultyLevel, Problem, TestCase, TopicType
from app.models.user import User, UserRole
from app.schemas.problem import (
    CodeDraftResponse,
    CodeDraftSave,
    ProblemCreate,
    ProblemDetailResponse,
    ProblemListItem,
    ProblemUpdate,
    SampleTestCaseResponse,
    TestCaseCreate,
)

router = APIRouter(tags=["problems"])
admin_router = APIRouter(prefix="/admin", tags=["admin-problems"])


def _serialize_problem(problem: Problem, current_user: User | None = None, db: Session | None = None) -> ProblemListItem:
    if current_user and db is not None:
        submissions = (
            db.query(Submission)
            .filter(Submission.student_id == current_user.id, Submission.problem_id == problem.id)
            .order_by(Submission.created_at.desc())
            .all()
        )
        if any(submission.verdict == SubmissionVerdict.ACCEPTED for submission in submissions):
            status = "SOLVED"
        elif submissions:
            status = "ATTEMPTED"
        else:
            status = "NOT_ATTEMPTED"
        return ProblemListItem(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            difficulty=problem.difficulty,
            topic=problem.topic,
            status=status,
            attempt_count=len(submissions),
            accepted_at=next((submission.created_at for submission in submissions if submission.verdict == SubmissionVerdict.ACCEPTED), None),
        )
    return ProblemListItem(id=problem.id, title=problem.title, slug=problem.slug, difficulty=problem.difficulty, topic=problem.topic)


def _serialize_problem_detail(problem: Problem) -> ProblemDetailResponse:
    sample_cases = [
        SampleTestCaseResponse(
            id=test_case.id,
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            explanation=test_case.explanation,
            is_sample=test_case.is_sample,
            order_index=test_case.order_index,
            created_at=test_case.created_at,
        )
        for test_case in sorted(problem.test_cases, key=lambda item: item.order_index)
        if test_case.is_sample
    ]
    return ProblemDetailResponse(
        id=problem.id,
        title=problem.title,
        slug=problem.slug,
        description=problem.description,
        difficulty=problem.difficulty,
        topic=problem.topic,
        constraints=problem.constraints,
        input_format=problem.input_format,
        output_format=problem.output_format,
        starter_code=problem.starter_code or {},
        time_limit_ms=problem.time_limit_ms,
        memory_limit_mb=problem.memory_limit_mb,
        sample_test_cases=sample_cases,
    )


@router.get("/problems", response_model=dict)
def list_problems(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    difficulty: DifficultyLevel | None = None,
    topic: TopicType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value, UserRole.ADMIN.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    query = db.query(Problem).filter(Problem.is_active.is_(True))
    if search:
        pattern = f"%{search}%"
        query = query.filter((Problem.title.ilike(pattern)) | (Problem.description.ilike(pattern)) | (Problem.slug.ilike(pattern)))
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    if topic:
        query = query.filter(Problem.topic == topic)

    total = query.count()
    items = query.order_by(Problem.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_serialize_problem(problem, current_user=current_user, db=db) for problem in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max((total + page_size - 1) // page_size, 1),
    }


@router.get("/problems/{slug}", response_model=ProblemDetailResponse)
def get_problem_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value, UserRole.ADMIN.value)),
):
    problem = db.query(Problem).filter(Problem.slug == slug, Problem.is_active.is_(True)).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return _serialize_problem_detail(problem)


@router.get("/problems/{problem_id}/draft", response_model=CodeDraftResponse)
def get_problem_draft(
    problem_id: int,
    language: str = Query(default="python"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    draft = (
        db.query(CodeDraft)
        .filter(CodeDraft.student_id == current_user.id, CodeDraft.problem_id == problem_id, CodeDraft.language == language.lower())
        .first()
    )
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return draft


@router.put("/problems/{problem_id}/draft", response_model=CodeDraftResponse)
def save_problem_draft(
    problem_id: int,
    payload: CodeDraftSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    problem = db.query(Problem).filter(Problem.id == problem_id, Problem.is_active.is_(True)).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    existing = (
        db.query(CodeDraft)
        .filter(
            CodeDraft.student_id == current_user.id,
            CodeDraft.problem_id == problem_id,
            CodeDraft.language == payload.language.lower(),
        )
        .first()
    )
    if existing:
        existing.code = payload.code
        existing.updated_at = None
        draft = existing
    else:
        draft = CodeDraft(student_id=current_user.id, problem_id=problem_id, language=payload.language.lower(), code=payload.code)
        db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@admin_router.post("/problems", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_problem(
    payload: ProblemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    if db.query(Problem).filter(Problem.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Problem slug already exists")
    problem = Problem(
        title=payload.title,
        slug=payload.slug,
        description=payload.description,
        difficulty=payload.difficulty,
        topic=payload.topic,
        constraints=payload.constraints,
        input_format=payload.input_format,
        output_format=payload.output_format,
        starter_code=payload.starter_code,
        time_limit_ms=payload.time_limit_ms,
        memory_limit_mb=payload.memory_limit_mb,
        created_by=current_user.id,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return {
        "id": problem.id,
        "title": problem.title,
        "slug": problem.slug,
        "difficulty": problem.difficulty,
        "topic": problem.topic,
        "is_active": problem.is_active,
    }


@admin_router.get("/problems")
def list_admin_problems(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    difficulty: DifficultyLevel | None = None,
    topic: TopicType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    query = db.query(Problem)
    if search:
        pattern = f"%{search}%"
        query = query.filter((Problem.title.ilike(pattern)) | (Problem.description.ilike(pattern)) | (Problem.slug.ilike(pattern)))
    if difficulty:
        query = query.filter(Problem.difficulty == difficulty)
    if topic:
        query = query.filter(Problem.topic == topic)
    total = query.count()
    items = query.order_by(Problem.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_serialize_problem(problem) for problem in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max((total + page_size - 1) // page_size, 1),
    }


@admin_router.get("/problems/{problem_id}")
def get_admin_problem(problem_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return {
        "id": problem.id,
        "title": problem.title,
        "slug": problem.slug,
        "description": problem.description,
        "difficulty": problem.difficulty,
        "topic": problem.topic,
        "constraints": problem.constraints,
        "input_format": problem.input_format,
        "output_format": problem.output_format,
        "starter_code": problem.starter_code or {},
        "time_limit_ms": problem.time_limit_ms,
        "memory_limit_mb": problem.memory_limit_mb,
        "is_active": problem.is_active,
        "test_cases": [
            {
                "id": test_case.id,
                "input_data": test_case.input_data,
                "expected_output": test_case.expected_output,
                "explanation": test_case.explanation,
                "is_sample": test_case.is_sample,
                "order_index": test_case.order_index,
                "created_at": test_case.created_at,
            }
            for test_case in sorted(problem.test_cases, key=lambda item: item.order_index)
        ],
    }


@admin_router.put("/problems/{problem_id}")
def update_problem(problem_id: int, payload: ProblemUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    if payload.slug and payload.slug != problem.slug and db.query(Problem).filter(Problem.slug == payload.slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Problem slug already exists")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(problem, field, value)
    problem.updated_at = None
    db.commit()
    db.refresh(problem)
    return {"id": problem.id, "slug": problem.slug, "is_active": problem.is_active}


@admin_router.delete("/problems/{problem_id}")
def deactivate_problem(problem_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN.value))):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    problem.is_active = False
    db.commit()
    return {"message": "Problem deactivated"}


@admin_router.post("/problems/{problem_id}/test-cases", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_test_case(
    problem_id: int,
    payload: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    test_case = TestCase(
        problem_id=problem_id,
        input_data=payload.input_data,
        expected_output=payload.expected_output,
        explanation=payload.explanation,
        is_sample=payload.is_sample,
        order_index=payload.order_index,
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return {"id": test_case.id, "is_sample": test_case.is_sample}


@admin_router.put("/test-cases/{test_case_id}")
def update_test_case(
    test_case_id: int,
    payload: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    test_case.input_data = payload.input_data
    test_case.expected_output = payload.expected_output
    test_case.explanation = payload.explanation
    test_case.is_sample = payload.is_sample
    test_case.order_index = payload.order_index
    db.commit()
    db.refresh(test_case)
    return {"message": "Test case updated"}


@admin_router.delete("/test-cases/{test_case_id}")
def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN.value)),
):
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found")
    db.delete(test_case)
    db.commit()
    return {"message": "Test case deleted"}


__all__ = ["router", "admin_router"]
