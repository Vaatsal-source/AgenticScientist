from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from app.config import settings
from app.rag.vector_store import VectorStoreManager
from app.agents.prompts import FEYNMAN_SYSTEM_INSTRUCTION, format_rag_prompt
from app.memory.short_term import ShortTermMemoryManager

class FeynmanAgent:
    def __init__(self):
        # Automatically connects using GEMINI_API_KEY from settings
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"
        self.vector_store = VectorStoreManager()

    def answer_question(self, db: Session, session_id: str, query: str, limit: int = 3) -> str:
        """Executes standard synchronous generation while maintaining verified history models."""
        # 1. Log incoming user raw query to Short-Term tables
        ShortTermMemoryManager.save_message(db, session_id=session_id, role="user", content=query)

        # 2. Extract RAG blocks
        retrieved_context = self.vector_store.similarity_search(db, query=query, limit=limit)
        compiled_prompt = format_rag_prompt(user_query=query, retrieved_chunks=retrieved_context)
        
        # 3. Pull previous dialogue sequence as explicit structural types
        history_turns = ShortTermMemoryManager.get_conversation_history(db, session_id=session_id, limit=6)
        
        # 4. Append structural ground data block as final historical execution point
        history_turns.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=compiled_prompt)]
            )
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=history_turns,
            config=types.GenerateContentConfig(
                system_instruction=FEYNMAN_SYSTEM_INSTRUCTION,
                temperature=0.7,
                top_p=0.95
            )
        )
        
        ShortTermMemoryManager.save_message(db, session_id=session_id, role="model", content=response.text)
        return response.text

    def answer_question_stream(self, db: Session, session_id: str, query: str, limit: int = 3):
        """Streams text chunks while maintaining short-term context windows."""
        # 1. Log user question
        ShortTermMemoryManager.save_message(db, session_id=session_id, role="user", content=query)

        # 2. Extract RAG context mappings
        retrieved_context = self.vector_store.similarity_search(db, query=query, limit=limit)
        compiled_prompt = format_rag_prompt(user_query=query, retrieved_chunks=retrieved_context)
        
        # 3. Read history as verified SDK formats
        history_turns = ShortTermMemoryManager.get_conversation_history(db, session_id=session_id, limit=6)
        
        # 4. Append final context-injected prompt
        history_turns.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=compiled_prompt)]
            )
        )
        
        response_stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=history_turns,
            config=types.GenerateContentConfig(
                system_instruction=FEYNMAN_SYSTEM_INSTRUCTION,
                temperature=0.7,
                top_p=0.95
            )
        )
        
        full_response = ""
        for chunk in response_stream:
            if chunk.text:
                full_response += chunk.text
                yield chunk.text
                
        # 5. Commit full response chunk to history
        ShortTermMemoryManager.save_message(db, session_id=session_id, role="model", content=full_response)