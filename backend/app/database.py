from sqlalchemy import create_engine, text, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.config import settings

# Engine configured with proactive pre-ping mechanics to prevent Neon connection timeouts
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,  # Auto-recycle connections older than 30 minutes
    pool_pre_ping=True   # Issue a lightweight test query before routing any ORM statement
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 1. RAG Vector Storage Table ---
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_file = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    # gemini-embedding-001 output forced to 768 dimensions
    embedding = Column(Vector(768))

# --- 2. Short-Term Memory Chat Log Table ---
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False) # Groups separate chat instances
    role = Column(String(50), nullable=False)                    # Strict mapping: 'user' or 'model'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- 3. Long-Term Memory Dashboard Data Table ---
class LongTermMemory(Base):
    __tablename__ = "long_term_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, default="default_user")
    category = Column(String(100), nullable=False)               # e.g., 'User Profile', 'Physics Concept'
    fact_summary = Column(Text, nullable=False)                  # Insights extracted by Gemini
    importance_score = Column(Integer, default=3)                # Scale 1-5 for front-end visual weight
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

def init_db():
    """Executes initial migrations and extensions setup on Cloud Neon Postgres."""
    with engine.connect() as conn:
        # Register pgvector extension within the instance
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()