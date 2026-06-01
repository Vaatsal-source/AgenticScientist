from google import genai
from google.genai import types  # Import the configuration types module
from app.config import settings

class GeminiEmbedder:
    def __init__(self):
        # Initializes the client using GEMINI_API_KEY from environment variables automatically
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = "gemini-embedding-001" 

    def get_embedding(self, text: str) -> list[float]:
        """Generates a structural embedding optimized for a search QUERY."""
        if not text.strip():
            return []
        
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=768,       # Force truncation to match your Neon schema
                task_type="RETRIEVAL_QUERY"       # Optimize for incoming user queries
            )
        )
        return response.embeddings[0].values

    def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for multiple chunks optimized for DOCUMENT storage."""
        valid_texts = [t for t in texts if t.strip()]
        if not valid_texts:
            return []
            
        response = self.client.models.embed_content(
            model=self.model,
            contents=valid_texts,
            config=types.EmbedContentConfig(
                output_dimensionality=768,       # Force truncation to match your Neon schema
                task_type="RETRIEVAL_DOCUMENT"    # Optimize for stored contextual knowledge bases
            )
        )
        return [emb.values for emb in response.embeddings]