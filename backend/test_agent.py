import sys
from app.database import SessionLocal, init_db
from app.agents.feynman_agent import FeynmanAgent
from app.memory.long_term import LongTermMemoryManager

def test_feynman_with_memory():
    print("🛠️ Syncing database tables...")
    init_db()
    
    print("🧠 Awakening the Digital Twin of Richard Feynman...")
    agent = FeynmanAgent()
    lt_memory = LongTermMemoryManager()
    db = SessionLocal()
    
    session_id = "feynman_session_999"
    query = "I am a VLSI engineering student working on an offline AI triage application. Can you explain why you thought space-time points were like particles in 1965?"
    
    print(f"\n--- User asks: '{query}' ---")
    sys.stdout.write("Feynman: ")
    
    try:
        # 1. Execute live stream
        for chunk in agent.answer_question_stream(db, session_id=session_id, query=query, limit=2):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        print("\n-------------------------------------------")
        
        # 2. Fire the Long Term memory synthesis engine right after
        print("\n⚙️ Triggering asynchronous background memory consolidation loop...")
        lt_memory.analyze_and_update_memory(db, session_id=session_id)
        
        # 3. Read back what is stored for verification
        print("\n📊 Current Records Inside Memory Visualization Dashboard Server Cache:")
        saved_facts = lt_memory.fetch_all_memories(db)
        for fact in saved_facts:
            print(f" -> [{fact['category']}] (Score: {fact['importance_score']}/5) {fact['fact_summary']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_feynman_with_memory()