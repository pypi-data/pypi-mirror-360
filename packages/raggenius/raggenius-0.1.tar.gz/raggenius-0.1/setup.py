# setup.py
"""
Setup Script for raglib
------------------------
Allows installation via pip and publishing to PyPI.
"""

from setuptools import setup, find_packages

setup(
    name='raggenius',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'openai',
        'sentence-transformers',
        'faiss-cpu',
        'qdrant-client',
        'numpy',
        'nltk',
        'pdfplumber',
        'python-docx',
        'pandas',
        'pytesseract',
        'Pillow'
    ],
    author='Abhishek Ghotekar',
    description='A lightweight modular RAG library',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
