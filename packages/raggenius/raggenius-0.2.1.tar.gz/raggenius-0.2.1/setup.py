from setuptools import setup, find_packages

setup(
    name="raggenius",
    version="0.2.1",  # 🔁 Bump this for every release
    description="A modular and extensible RAG (Retrieval-Augmented Generation) library with OCR and vector DB support.",
    author="Abhishek Ghotekar",
    author_email="your-email@example.com",  # optional
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "raglib>=0.2.1",             # Your custom dependency
        "sentence-transformers",     # Embeddings
        "qdrant-client",             # Vector DB
        "faiss-cpu",                 # Optional vector store
        "openai",                    # For OpenAI embedding/LLM
        "google-generativeai",      # For Gemini
        "pytesseract",               # OCR
        "Pillow",                    # Image processing
        "PyYAML"                     # For config handling
    ],
    entry_points={
        "console_scripts": [
            "raggenius-setup=raggenius.setup:run_setup_wizard"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
)
