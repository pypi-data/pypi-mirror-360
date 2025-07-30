import socket
import subprocess
import time
import uuid
import requests

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

def is_qdrant_running(host='localhost', port=6333):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False

def wait_for_qdrant_ready(host='localhost', port=6333, timeout=30):
    """Wait for Qdrant HTTP API to respond."""
    url = f"http://{host}:{port}/collections"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("✅ Qdrant is ready.")
                return True
        except requests.exceptions.RequestException:
            pass
        print("⏳ Waiting for Qdrant to be ready...")
        time.sleep(1)
    raise RuntimeError("❌ Timed out waiting for Qdrant to start.")

def start_qdrant_with_docker():
    print("🚀 Qdrant not running. Starting with Docker...")
    try:
        subprocess.Popen([
            "docker", "run", "--rm", "-p", "6333:6333", "qdrant/qdrant"
        ])
    except Exception as e:
        raise RuntimeError(f"❌ Failed to start Qdrant: {e}")

class QdrantVectorStore:
    def __init__(self, collection_name, host="localhost", port=6333, dim=384):
        self.collection_name = collection_name

        if not is_qdrant_running(host, port):
            start_qdrant_with_docker()
            wait_for_qdrant_ready(host, port)

        self.client = QdrantClient(host=host, port=port)

        existing_collections = [
            col.name for col in self.client.get_collections().collections
        ]
        if collection_name not in existing_collections:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def add_embeddings(self, texts, embeddings):
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings[i],
                payload={"text": texts[i]},
            ) for i in range(len(texts))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def query(self, query_vector, top_k=5):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
        )
        return [r.payload["text"] for r in results]
