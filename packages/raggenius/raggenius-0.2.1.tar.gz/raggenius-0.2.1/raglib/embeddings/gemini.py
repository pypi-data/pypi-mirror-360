# raglib/embeddings/gemini.py

import google.generativeai as genai
import numpy as np

class GeminiEmbedding:
    def __init__(self, api_key=None, model_name="models/embedding-001"):
        if api_key is not None:
            genai.configure(api_key=api_key)
        self.model = genai.get_model(model_name)

    def embed_text(self, text):
        response = self.model.embed_content([text])
        # The API returns a list of embeddings
        return np.array(response['embedding'])

    def embed_texts(self, texts):
        response = self.model.embed_content(texts)
        # The API returns a list of embeddings
        return np.array([r['embedding'] for r in response['embeddings']]) 