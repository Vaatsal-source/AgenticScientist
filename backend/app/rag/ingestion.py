import os
import re
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.rag.vector_store import VectorStoreManager

class SmartTextSplitter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """
        Splits text recursively by trying paragraphs, then sentences, 
        ensuring context isn't awkwardly sheared mid-thought.
        """
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Primitive but effective structural split (paragraphs or sentences)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If a single sentence is excessively long, truncate or accept it
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Setup next chunk with designated overlapping historical structural data
                # Retain last few words or characters for smooth vector transitions
                overlap_words = current_chunk.split()[-15:] if current_chunk else []
                overlap_prefix = " ".join(overlap_words)
                
                if len(overlap_prefix) + len(sentence) <= self.chunk_size:
                    current_chunk = overlap_prefix + (" " if overlap_prefix else "") + sentence
                else:
                    current_chunk = sentence
                    
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

class IngestionEngine:
    def __init__(self):
        self.splitter = SmartTextSplitter()
        self.store_manager = VectorStoreManager()

    def ingest_file(self, db: Session, file_path: str):
        """Reads, chunks, embeds, and stores a document into Neon Postgres."""
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return

        file_name = os.path.basename(file_path)
        print(f"📖 Processing raw transcript: '{file_name}'...")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Step 1: Chunk text
        chunks = self.splitter.split_text(raw_content)
        print(f"✂️ Fragmented document into {len(chunks)} contextual chunks.")

        if not chunks:
            print("⚠️ No valid textual assets parsed.")
            return

        # Step 2: Extract embeddings and upload to Cloud database
        print(f"📡 Generating embeddings via text-embedding-004 & uploading to Neon...")
        self.store_manager.add_document(db, source_name=file_name, text_chunks=chunks)
        print(f"✅ Successfully ingested: {file_name}\n")