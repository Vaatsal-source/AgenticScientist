from sqlalchemy import text
from app.database import DocumentChunk  # Import the unified model instead of redefining it!
from app.rag.embedder import GeminiEmbedder

class VectorStoreManager:
    def __init__(self):
        self.embedder = GeminiEmbedder()

    def add_document(self, db, source_name: str, text_chunks: list[str]):
        """Embeds text blocks and uploads them securely into Cloud PostgreSQL."""
        embeddings = self.embedder.get_embeddings_batch(text_chunks)
        
        db_chunks = [
            DocumentChunk(
                source_file=source_name,
                content=chunk,
                embedding=emb
            )
            for chunk, emb in zip(text_chunks, embeddings)
        ]
        
        db.add_all(db_chunks)
        db.commit()

    def similarity_search(self, db, query: str, limit: int = 5) -> list[dict]:
        """Queries Neon instance using vector distance operations."""
        query_vector = self.embedder.get_embedding(query)
        if not query_vector:
            return []

        # Utilize pgvector cosine distance operator (<=>) via a clean textual execution
        stmt = text("""
            SELECT source_file, content, (embedding <=> :vector) as distance 
            FROM document_chunks 
            ORDER BY embedding <=> :vector 
            LIMIT :limit;
        """)
        
        # Execute raw vectorized matching against Neon
        result = db.execute(stmt, {"vector": str(query_vector), "limit": limit})
        
        items = []
        for row in result:
            items.append({
                "source": row.source_file,
                "content": row.content,
                "score": 1 - row.distance # Converting distance to similarity score
            })
        return items