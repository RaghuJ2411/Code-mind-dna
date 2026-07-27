from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.message import Conversation, ConversationParticipant, Message
from app.models.user import User, UserRole
from app.schemas.message import (
    ConversationDetailResponse,
    ConversationResponse,
    MessageResponse,
    ParticipantResponse,
    SendMessageRequest,
    UnreadCountResponse,
)

router = APIRouter(prefix="/mentor/messages", tags=["mentor-messages"])


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    conversation_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    participant_subquery = (
        db.query(ConversationParticipant.conversation_id)
        .filter(ConversationParticipant.user_id == current_user.id)
        .subquery()
    )
    query = db.query(Conversation).filter(Conversation.id.in_(participant_subquery))
    if conversation_type:
        query = query.filter(Conversation.conversation_type == conversation_type)

    conversations = query.order_by(Conversation.updated_at.desc()).all()
    result = []
    for conv in conversations:
        last_msg = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        unread = (
            db.query(Message)
            .filter(
                Message.conversation_id == conv.id,
                Message.is_read.is_(False),
                Message.sender_id != current_user.id,
            )
            .count()
        )
        result.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            conversation_type=conv.conversation_type,
            unread_count=unread,
            last_message=last_msg.content[:100] if last_msg else None,
            last_message_at=last_msg.created_at if last_msg else None,
            is_active=conv.is_active,
            created_at=conv.created_at,
        ))
    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == current_user.id,
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")

    db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != current_user.id,
        Message.is_read.is_(False),
    ).update({"is_read": True})
    participant.last_read_at = datetime.now(timezone.utc)
    db.commit()

    participants = (
        db.query(ConversationParticipant, User)
        .join(User, ConversationParticipant.user_id == User.id)
        .filter(ConversationParticipant.conversation_id == conversation_id)
        .all()
    )
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        conversation_type=conversation.conversation_type,
        participants=[
            ParticipantResponse(user_id=p.ConversationParticipant.user_id, user_name=u.full_name, user_role=u.role.value)
            for p, u in participants
        ],
        messages=[{
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": next((u.full_name for p, u in participants if p.user_id == m.sender_id), "Unknown"),
            "content": m.content,
            "attachment_url": m.attachment_url,
            "attachment_type": m.attachment_type,
            "is_read": m.is_read,
            "created_at": m.created_at,
        } for m in messages],
        created_at=conversation.created_at,
    )


@router.post("/conversations/{conversation_id}/send", response_model=MessageResponse)
def send_message(
    conversation_id: int,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id,
        ConversationParticipant.user_id == current_user.id,
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")

    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=payload.content,
        attachment_url=payload.attachment_url,
        attachment_type=payload.attachment_type,
    )
    db.add(message)
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(message)

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender_name=current_user.full_name,
        content=message.content,
        attachment_url=message.attachment_url,
        attachment_type=message.attachment_type,
        is_read=message.is_read,
        created_at=message.created_at,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    participant_subquery = (
        db.query(ConversationParticipant.conversation_id)
        .filter(ConversationParticipant.user_id == current_user.id)
        .subquery()
    )
    total_unread = (
        db.query(Message)
        .filter(
            Message.conversation_id.in_(participant_subquery),
            Message.is_read.is_(False),
            Message.sender_id != current_user.id,
        )
        .count()
    )
    return UnreadCountResponse(total_unread=total_unread)

