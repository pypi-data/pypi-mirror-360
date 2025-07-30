# raglib/embeddings/huggingface.py

from sentence_transformers import SentenceTransformer

class HuggingFaceEmbedding:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text):
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts):
        return self.model.encode(texts, convert_to_numpy=True)
