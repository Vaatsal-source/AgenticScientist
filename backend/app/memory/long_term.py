import json
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from app.config import settings
from app.database import LongTermMemory

class LongTermMemoryManager:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    def analyze_and_update_memory(self, db: Session, session_id: str):
        """
        Analyzes the short-term chat logs for a session, extracts key insights,
        and saves them into long-term structured memory storage.
        """
        from app.database import ChatMessage
        
        # 1. Fetch the last 10 messages from this session to understand the context
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )
        
        if not messages:
            return
            
        # Reverse to get chronological order
        messages.reverse()

        # 2. Format the short-term dialogue sequence as a transparent text log
        chat_transcript = ""
        for msg in messages:
            role_label = "Feynman" if msg.role == 'model' else "User"
            chat_transcript += f"{role_label}: {msg.content}\n"

        analysis_prompt = f"""
        You are a memory consolidation background sub-system for Richard Feynman's Digital Twin.
        Your task is to analyze the following dialogue transcript and extract lasting, high-level insights that should be remembered across future sessions.

        Look for:
        - Specific user details or preferences (e.g., if they are an engineering student, their field of study, or things they are building).
        - Deep scientific concepts discussed or cleared up.
        - Historical timeline points or anchors requested (e.g., interest in 1965 Nobel developments).

        Dialogue Transcript:
        \"\"\"
        {chat_transcript}
        \"\"\"

        Return ONLY a valid JSON list of objects matching this exact structural schema:
        [
          {{
            "category": "User Profile" OR "Physics Concept" OR "Timeline Anchor" OR "General Insight",
            "fact_summary": "A concise, clear single-sentence summary of the fact to persist.",
            "importance_score": 1 to 5 (where 5 is highly critical for a dashboard layout)
          }}
        ]
        
        CRITICAL: If no meaningful persistent facts are found in this snapshot, return an empty list: []
        Do not include markdown blocks like ```json or any conversational filler. Return raw valid JSON.
        """

        try:
            # Enforce native schema compliance using application/json mode
            response = self.client.models.generate_content(
                model=self.model,
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1  # Set to 0.1 for highly objective fact extraction
                )
            )
            
            clean_text = response.text.strip()
            if not clean_text:
                return

            extracted_memories = json.loads(clean_text)
            
            # 3. Deduplicate and insert newly discovered insights into Neon
            for mem in extracted_memories:
                category = mem.get("category", "General Insight")
                fact_summary = mem.get("fact_summary", "").strip()
                importance = mem.get("importance_score", 3)
                
                if not fact_summary:
                    continue
                    
                # Simple check to see if we've already stored this exact fact summary recently
                exists = db.query(LongTermMemory).filter(
                    LongTermMemory.fact_summary == fact_summary
                ).first()
                
                if not exists:
                    new_fact = LongTermMemory(
                        category=category,
                        fact_summary=fact_summary,
                        importance_score=importance
                    )
                    db.add(new_fact)
            
            db.commit()
            print(f"💾 Background Memory Worker: Successfully synthesized and committed {len(extracted_memories)} insights to Neon.")
            
        except Exception as e:
            db.rollback()
            print(f"⚠️ Background Memory Worker processing error: {e}")

    def fetch_all_memories(self, db: Session) -> list[dict]:
        """Retrieves rows cleanly sorted by recency to feed into the frontend dashboard panel."""
        memories = db.query(LongTermMemory).order_by(LongTermMemory.created_at.desc()).all()
        return [
            {
                "id": m.id,
                "category": m.category,
                "fact_summary": m.fact_summary,
                "importance_score": m.importance_score,
                "created_at": m.created_at.isoformat()
            }
            for m in memories
        ]