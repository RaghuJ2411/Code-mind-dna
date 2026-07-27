from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.learning import (
    Bookmark, Certificate, CourseProgress, Enrollment, LearningCourse, Note
)
from app.models.user import User, UserRole
from app.schemas.learning import (
    BookmarkCreate, BookmarkResponse, CertificateResponse,
    CourseProgressResponse, EnrollmentResponse, LearningCourseResponse,
    LearningHistoryItem, LearningHistoryResponse, NoteCreate, NoteResponse, NoteUpdate
)

router = APIRouter(prefix="/student/learning", tags=["student-learning"])


@router.get("/courses", response_model=list[LearningCourseResponse])
def list_courses(
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    query = db.query(LearningCourse).filter(LearningCourse.is_active.is_(True))
    if category:
        query = query.filter(LearningCourse.category == category)
    if difficulty:
        query = query.filter(LearningCourse.difficulty == difficulty)
    if search:
        pattern = f"%{search}%"
        query = query.filter(LearningCourse.title.ilike(pattern))
    return query.order_by(LearningCourse.created_at.desc()).all()


@router.get("/courses/{course_id}", response_model=LearningCourseResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    course = db.query(LearningCourse).filter(LearningCourse.id == course_id, LearningCourse.is_active.is_(True)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/enroll/{course_id}", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    course = db.query(LearningCourse).filter(LearningCourse.id == course_id, LearningCourse.is_active.is_(True)).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = db.query(Enrollment).filter(Enrollment.student_id == current_user.id, Enrollment.course_id == course_id).first()
    if existing:
        return existing
    enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/enrollments", response_model=list[EnrollmentResponse])
def list_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return db.query(Enrollment).filter(Enrollment.student_id == current_user.id).order_by(Enrollment.enrolled_at.desc()).all()


@router.get("/progress/{course_id}", response_model=list[CourseProgressResponse])
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return db.query(CourseProgress).filter(
        CourseProgress.student_id == current_user.id,
        CourseProgress.course_id == course_id,
    ).all()


@router.put("/progress/{course_id}/{module_id}", response_model=CourseProgressResponse)
def update_course_progress(
    course_id: int,
    module_id: str,
    completed_sections: list[str] = Query(default=[]),
    current_section: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    progress = db.query(CourseProgress).filter(
        CourseProgress.student_id == current_user.id,
        CourseProgress.course_id == course_id,
        CourseProgress.module_id == module_id,
    ).first()
    if not progress:
        progress = CourseProgress(
            student_id=current_user.id,
            course_id=course_id,
            module_id=module_id,
            completed_sections=completed_sections,
            current_section=current_section,
        )
        db.add(progress)
    else:
        progress.completed_sections = list(set(progress.completed_sections + completed_sections))
        if current_section:
            progress.current_section = current_section

    # Update enrollment progress
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == course_id,
    ).first()
    if enrollment:
        total_modules = db.query(CourseProgress).filter(
            CourseProgress.student_id == current_user.id,
            CourseProgress.course_id == course_id,
        ).count()
        completed_modules = db.query(CourseProgress).filter(
            CourseProgress.student_id == current_user.id,
            CourseProgress.course_id == course_id,
        ).count()
        if total_modules > 0:
            enrollment.progress_pct = min(100.0, (completed_modules / max(1, total_modules)) * 100)
        if enrollment.progress_pct >= 100.0:
            enrollment.completed = True
            enrollment.completed_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)

    db.commit()
    db.refresh(progress)
    return progress


@router.get("/bookmarks", response_model=list[BookmarkResponse])
def list_bookmarks(
    resource_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    query = db.query(Bookmark).filter(Bookmark.student_id == current_user.id)
    if resource_type:
        query = query.filter(Bookmark.resource_type == resource_type)
    return query.order_by(Bookmark.created_at.desc()).all()


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    payload: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    bookmark = Bookmark(
        student_id=current_user.id,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        resource_title=payload.resource_title,
        notes=payload.notes,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.student_id == current_user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()


@router.get("/notes", response_model=list[NoteResponse])
def list_notes(
    resource_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    query = db.query(Note).filter(Note.student_id == current_user.id)
    if resource_type:
        query = query.filter(Note.resource_type == resource_type)
    return query.order_by(Note.updated_at.desc()).all()


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    note = Note(
        student_id=current_user.id,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    note = db.query(Note).filter(Note.id == note_id, Note.student_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.tags is not None:
        note.tags = payload.tags
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    note = db.query(Note).filter(Note.id == note_id, Note.student_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()


@router.get("/certificates", response_model=list[CertificateResponse])
def list_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return db.query(Certificate).filter(Certificate.student_id == current_user.id).order_by(Certificate.issued_at.desc()).all()


@router.get("/history", response_model=LearningHistoryResponse)
def get_learning_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).order_by(Enrollment.enrolled_at.desc()).limit(20).all()
    items = []
    for enrollment in enrollments:
        course = db.query(LearningCourse).filter(LearningCourse.id == enrollment.course_id).first()
        action = "COMPLETED" if enrollment.completed else "ENROLLED" if enrollment.progress_pct == 0 else "PROGRESS"
        items.append(LearningHistoryItem(
            course_id=enrollment.course_id,
            course_title=course.title if course else "Unknown",
            action=action,
            timestamp=enrollment.enrolled_at,
        ))
    return LearningHistoryResponse(items=items)

