import os
import sys
from app.database import SessionLocal, init_db
from app.rag.ingestion import IngestionEngine

def main():
    # 1. Ensure DB extension & schema matchers are initialized in Neon
    print("🛠️ Synchronizing remote Neon database schemas...")
    init_db()
    
    # 2. Define data raw directories
    raw_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    engine = IngestionEngine()
    db = SessionLocal()
    
    try:
        # Scan folder for txt or md lecture source documents
        files = [f for f in os.listdir(raw_dir) if f.endswith(('.txt', '.md'))]
        
        if not files:
            print(f"\n📥 No documents found in '{raw_dir}'!")
            print(f"💡 Please drop raw text files (e.g., feynman_1965_nobel.txt) in that folder and re-run.")
            return

        print(f"🚀 Found {len(files)} files target for ingestion pipeline processing.")
        for file in files:
            full_path = os.path.join(raw_dir, file)
            engine.ingest_file(db, full_path)
            
        print("🎉 Ingestion complete! Data is fully queryable inside Neon pgvector.")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {str(e)}", file=sys.stderr)
    finally:
        db.close()

if __name__ == "__main__":
    main()