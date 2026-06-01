from sqlalchemy.orm import Session
from google.genai import types
from app.database import ChatMessage

class ShortTermMemoryManager:
    @staticmethod
    def save_message(db: Session, session_id: str, role: str, content: str) -> ChatMessage:
        """Saves a single turn of conversation history."""
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_conversation_history(db: Session, session_id: str, limit: int = 10) -> list[types.Content]:
        """Retrieves the recent K turns of conversation for prompt injection."""
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )
        
        # Format explicitly into structural payloads compatible with conversational flows
        # Note: Gemini 2.5 Flash expects chat roles to map strictly to 'user' or 'model'
        return [
            types.Content(
                role=m.role,
                parts=[types.Part.from_text(text=m.content)]
            )
            for m in messages[-limit:]
        ]