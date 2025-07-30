import numpy as np
try:
    import faiss
except ImportError:
    raise ImportError("faiss is not installed. Please install faiss-cpu or faiss-gpu.")
import uuid

class FaissVectorStore:
    """
    In-memory vector store using FAISS for similarity search.
    Compatible with the interface of QdrantVectorStore.
    """
    def __init__(self, dim, collection_name="default", metric="cosine"):
        self.collection_name = collection_name
        self.texts = []
        self.ids = []
        self.metric = metric
        self.dim = dim
        if metric == "cosine":
            self.index = faiss.IndexFlatIP(dim)
        elif metric == "l2":
            self.index = faiss.IndexFlatL2(dim)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

    def add_embeddings(self, texts, embeddings):
        """
        Add embeddings and their corresponding texts to the FAISS index.
        Args:
            texts (List[str]): List of texts.
            embeddings (np.ndarray): 2D numpy array of shape (n, dim).
        """
        embeddings = np.array(embeddings, dtype=np.float32)
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        # Normalize for cosine similarity
        if self.metric == "cosine":
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / (norms + 1e-10)
        self.index.add(embeddings)  # type: ignore
        self.texts.extend(texts)
        self.ids.extend([str(uuid.uuid4()) for _ in texts])

    def query(self, query_vector, top_k=5):
        """
        Query the FAISS index for the most similar texts.
        Args:
            query_vector (np.ndarray): 1D numpy array of shape (dim,).
            top_k (int): Number of top results to return.
        Returns:
            List[str]: List of top matching texts.
        """
        if self.index.ntotal == 0:
            return []
        query_vector = np.array(query_vector, dtype=np.float32)
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        # Normalize for cosine similarity
        if self.metric == "cosine":
            query_vector = query_vector / (np.linalg.norm(query_vector, axis=1, keepdims=True) + 1e-10)
        D, I = self.index.search(query_vector, top_k)  # type: ignore
        results = []
        for idx in I[0]:
            if 0 <= idx < len(self.texts):
                results.append(self.texts[idx])
        return results 