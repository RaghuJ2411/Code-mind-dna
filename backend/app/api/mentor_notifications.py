from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.message import Message
from app.models.user import User, UserRole
from app.schemas.mentor import (
    MentorNotificationCreate,
    MentorNotificationResponse,
)

router = APIRouter(prefix="/mentor/notifications", tags=["mentor-notifications"])


@router.get("", response_model=list[MentorNotificationResponse])
def list_notifications(
    is_read: bool | None = Query(None),
    notification_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    query = db.query(Message).filter(
        Message.sender_id != current_user.id,
        Message.conversation_id.in_(
            db.query(Message.conversation_id).filter(
                Message.sender_id == current_user.id
            ).distinct()
        )
    )

    if is_read is not None:
        query = query.filter(Message.is_read == is_read)

    messages = query.order_by(Message.created_at.desc()).limit(limit).all()
    return [
        MentorNotificationResponse(
            id=msg.id,
            mentor_id=current_user.id,
            title=f"New Message #{msg.id}",
            message=msg.content[:200] if msg.content else "",
            notification_type="SYSTEM",
            student_id=msg.sender_id if msg.sender_id != 1 else None,
            priority="NORMAL",
            is_read=msg.is_read,
            read_at=None,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.post("", response_model=MentorNotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: MentorNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    from app.models.message import Conversation, ConversationParticipant

    # Create or find a system conversation
    conversation = Conversation(
        title=f"Notification: {payload.title}",
        conversation_type="MENTOR",
        created_by=current_user.id,
    )
    db.add(conversation)
    db.flush()

    participant = ConversationParticipant(
        conversation_id=conversation.id,
        user_id=current_user.id,
    )
    db.add(participant)

    msg = Message(
        conversation_id=conversation.id,
        sender_id=1,  # System
        content=f"[{payload.priority}] {payload.title}: {payload.message}",
        is_read=False,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MentorNotificationResponse(
        id=msg.id,
        mentor_id=current_user.id,
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
        student_id=payload.student_id,
        priority=payload.priority,
        is_read=False,
        read_at=None,
        created_at=msg.created_at,
    )


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    count = db.query(Message).filter(
        Message.sender_id != current_user.id,
        Message.is_read.is_(False),
        Message.conversation_id.in_(
            db.query(Message.conversation_id).filter(
                Message.sender_id == current_user.id
            ).distinct()
        )
    ).count()

    return {"unread_count": count}


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    msg = db.query(Message).filter(Message.id == notification_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Notification not found")

    msg.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    db.query(Message).filter(
        Message.sender_id != current_user.id,
        Message.is_read.is_(False),
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}

