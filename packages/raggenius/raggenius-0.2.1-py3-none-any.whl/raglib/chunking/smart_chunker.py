# raglib/chunking/smart_chunker.py

class SmartChunker:
    def __init__(self, chunk_size=200, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text):
        sentences = text.split(". ")
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + ". "
            else:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from previous
                current_chunk = sentence[-self.overlap:] + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
