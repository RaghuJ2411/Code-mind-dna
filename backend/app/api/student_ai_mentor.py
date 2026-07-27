from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.message import Conversation, ConversationParticipant, Message
from app.models.user import User, UserRole
from app.schemas.ai_mentor import (
    BugFixRequest, BugFixResponse, ChatHistoryResponse, ChatMessage,
    ChatRequest, ChatResponse, CodeExplanationRequest, CodeExplanationResponse,
    InterviewQuestionsRequest, InterviewQuestionsResponse,
    ResumeReviewRequest, ResumeReviewResponse,
)

router = APIRouter(prefix="/student/ai-mentor", tags=["student-ai-mentor"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_mentor(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    conversation_id = payload.conversation_id

    if not conversation_id:
        # Create new AI mentor conversation
        conversation = Conversation(
            title=f"AI Mentor - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
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
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=payload.message,
    )
    db.add(user_msg)

    # Generate AI response based on message content
    reply = _generate_ai_reply(payload.message)

    # Save AI response
    ai_msg = Message(
        conversation_id=conversation_id,
        sender_id=1,  # System/AI user ID
        content=reply,
    )
    db.add(ai_msg)

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)

    db.commit()

    return ChatResponse(reply=reply, conversation_id=conversation_id)


@router.get("/history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    participant_subquery = (
        db.query(ConversationParticipant.conversation_id)
        .filter(ConversationParticipant.user_id == current_user.id)
        .subquery()
    )
    conversations = (
        db.query(Conversation)
        .filter(Conversation.id.in_(participant_subquery), Conversation.conversation_type == "MENTOR")
        .order_by(Conversation.updated_at.desc())
        .limit(10)
        .all()
    )

    result = []
    for conv in conversations:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        result.append(ChatHistoryResponse(
            conversation_id=conv.id,
            messages=[
                ChatMessage(
                    role="assistant" if m.sender_id == 1 else "user",
                    content=m.content,
                    timestamp=m.created_at,
                )
                for m in messages
            ],
        ))

    return result


@router.post("/interview-questions", response_model=InterviewQuestionsResponse)
def generate_interview_questions(
    payload: InterviewQuestionsRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    questions = _generate_interview_questions(payload.role_name, payload.question_count)
    return InterviewQuestionsResponse(questions=questions)


@router.post("/resume-review", response_model=ResumeReviewResponse)
def review_resume(
    payload: ResumeReviewRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return ResumeReviewResponse(
        feedback="Your resume shows relevant skills but could be improved with more specific achievements and quantifiable results.",
        strengths=["Technical skills are well listed", "Clear career progression", "Relevant experience"],
        improvements=["Add quantifiable results", "Include more keywords from job descriptions", "Improve summary section"],
        match_score=75.0,
    )


@router.post("/code-explanation", response_model=CodeExplanationResponse)
def explain_code(
    payload: CodeExplanationRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return CodeExplanationResponse(
        explanation=f"This {payload.language} code implements the following logic...",
        key_concepts=["Algorithm design", "Data structures", "Time complexity"],
        suggestions=["Consider adding error handling", "Add comments for clarity", "Optimize for edge cases"],
    )


@router.post("/bug-fix", response_model=BugFixResponse)
def fix_bug(
    payload: BugFixRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    return BugFixResponse(
        fixed_code=payload.code,
        explanation="The issue is likely a logic error. Here's the analysis...",
        root_cause=payload.error_message or "Logic mismatch in conditional statements",
    )


def _generate_ai_reply(message: str) -> str:
    """Generate contextual AI mentor reply."""
    message_lower = message.lower()

    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! I'm your AI Mentor. I can help you with coding, career advice, interview preparation, and more. What would you like to work on today?"

    if "career" in message_lower or "job" in message_lower:
        return "Great topic! Let's discuss your career path. What roles are you interested in? I can help you identify skill gaps, prepare for interviews, and build a roadmap to your dream job."

    if "interview" in message_lower:
        return "Interview preparation is crucial! I can help you with:\n1. Common interview questions\n2. Coding challenge strategies\n3. Behavioral questions (STAR method)\n4. System design discussions\n\nWhat area would you like to focus on?"

    if "resume" in message_lower or "cv" in message_lower:
        return "Let me review your resume! A strong resume should highlight:\n- Quantifiable achievements\n- Relevant technical skills\n- Project impact\n- Clear career progression\n\nShare your resume and target role for specific feedback."

    if "project" in message_lower:
        return "Building projects is one of the best ways to learn! Consider:\n1. Full-stack applications\n2. Open source contributions\n3. Problem-solving tools\n4. Portfolio-worthy projects\n\nWhat type of project interests you?"

    if "bug" in message_lower or "error" in message_lower or "issue" in message_lower:
        return "Let's debug that issue! Share the code and error message. I'll help you identify the root cause and suggest fixes. Common issues include:\n- Logic errors\n- Edge cases\n- Performance bottlenecks\n- Memory leaks"

    if "learn" in message_lower or "study" in message_lower:
        return "Learning effectively requires a structured approach. I recommend:\n1. Start with fundamentals\n2. Practice consistently with coding challenges\n3. Build real projects\n4. Review and reflect on your progress\n\nWhat specific topic are you studying?"

    return "That's a great question! Let me help you think through this. Could you provide more details so I can give you the most relevant guidance? I specialize in coding help, career advice, interview prep, resume review, and learning strategies."


def _generate_interview_questions(role_name: str, count: int) -> list[str]:
    """Generate interview questions for a role."""
    questions = [
        f"Tell me about yourself and why you're interested in the {role_name} role.",
        f"What relevant experience do you have for the {role_name} position?",
        f"Describe a challenging {role_name} problem you solved and how you approached it.",
        f"How do you stay updated with the latest trends in {role_name}?",
        f"What technical skills make you a strong candidate for the {role_name} role?",
        "Describe a time you worked effectively in a team to achieve a goal.",
        "How do you handle tight deadlines and competing priorities?",
        "What is your greatest professional achievement so far?",
        "Where do you see your career in the next 3-5 years?",
        "Do you have any questions about the role or the company?",
    ]
    return questions[:count]

