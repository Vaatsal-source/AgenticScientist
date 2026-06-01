import asyncio
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import init_db, get_db, ChatMessage, LongTermMemory
from app.agents.feynman_agent import FeynmanAgent
from app.memory.long_term import LongTermMemoryManager

app = FastAPI(
    title="Richard Feynman Digital Twin API",
    description="Backend engine driving RAG context, short-term session tracking, and long-term memory dashboard arrays.",
    version="1.0.0"
)

# Configure CORS so your Next.js application can seamlessly query endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Next.js frontend source location configuration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
feynman_agent = FeynmanAgent()
memory_manager = LongTermMemoryManager()

# Ensure tables are initialized on startup
@app.on_event("startup")
def on_startup():
    print("🛠️ Synchronizing database models on Neon...")
    init_db()
    print("🚀 API Gateway initialized successfully!")

# --- Pydantic Schemas for JSON Payloads ---
class ChatQueryRequest(BaseModel):
    session_id: str
    query: str

# --- HTTP Endpoints ---

@app.post("/api/chat/stream")
async def chat_stream_endpoint(
    request: ChatQueryRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Exposes an SSE (Server-Sent Events) route for token-by-token text streaming.
    Spawns an asynchronous background task to consolidate memories when finished.
    """
    def event_generator():
        try:
            # Yield chunks natively as they stream back from Gemini 2.5 Flash
            for chunk in feynman_agent.answer_question_stream(
                db=db, 
                session_id=request.session_id, 
                query=request.query
            ):
                # SSE standard format: must start with "data: " and end with double newlines
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: [ERROR]: {str(e)}\n\n"
        finally:
            # Once the stream finishes, queue the heavy memory consolidation loop as a background thread
            background_tasks.add_task(
                memory_manager.analyze_and_update_memory, 
                db=db, 
                session_id=request.session_id
            )

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/memory/dashboard")
def get_memory_dashboard_records(db: Session = Depends(get_db)):
    """
    Fetches all synthesized long-term memory facts from Neon.
    Directly populates your extra-credit Memory Visualization Dashboard!
    """
    try:
        records = memory_manager.fetch_all_memories(db)
        return {"status": "success", "count": len(records), "memories": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load memory arrays: {str(e)}")


@app.delete("/api/memory/clear")
def clear_all_conversation_data(session_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Resets a conversation thread by clearing out selected short-term logs.
    """
    try:
        # Explicitly filter using the model column attribute with safety synchronization configurations
        deleted_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete(synchronize_session=False)
        db.commit()
        return {"status": "success", "message": f"Cleared {deleted_count} messages for session {session_id}."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"ORM Purge Error: {str(e)}")


@app.delete("/api/memory/reset", status_code=status.HTTP_200_OK)
def master_reset_all_memories(db: Session = Depends(get_db)):
    """
    Nukes the entire brain database using direct SQLAlchemy model queries
    to avoid raw SQL string mismatch errors.
    """
    try:
        # 1. Clear out short-term chat messages safely via ORM
        db.query(ChatMessage).delete(synchronize_session=False)
        
        # 2. Clear out long-term memory metrics directly targeting our declarative mapping class
        db.query(LongTermMemory).delete(synchronize_session=False)

        db.commit()
        return {
            "status": "success", 
            "message": "System wide reset successful. All profiles purged cleanly."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"ORM Purge Error: {str(e)}"
        )