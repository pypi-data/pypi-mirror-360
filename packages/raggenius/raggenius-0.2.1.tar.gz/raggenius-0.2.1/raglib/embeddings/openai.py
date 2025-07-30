# raglib/embeddings/openai.py

from openai import OpenAI
import numpy as np
import os

class OpenAIEmbedding:
    def __init__(self, api_key=None, model_name="text-embedding-3-small"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key) if self.api_key else OpenAI()

    def embed_text(self, text):
        response = self.client.embeddings.create(input=[text], model=self.model_name)
        return np.array(response.data[0].embedding)

    def embed_texts(self, texts):
        response = self.client.embeddings.create(input=texts, model=self.model_name)
        return np.array([d.embedding for d in response.data]) 