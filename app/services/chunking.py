import re
from typing import List


def fixed_size_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into fixed size chunks with a specified overlap.

    Args:
        text (str): The input text to chunk.
        chunk_size (int): Maximum size of each chunk.
        overlap (int): Number of characters to overlap between consecutive chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
        if start >= len(text) or chunk_size <= overlap:
            break

    return chunks


def sentence_chunk(text: str, max_sentences: int = 5) -> List[str]:
    """
    Splits text into chunks based on sentence boundaries.

    Args:
        text (str): The input text to chunk.
        max_sentences (int): Maximum number of sentences per chunk.

    Returns:
        List[str]: A list of text chunks.
    """
    if not text:
        return []

    # Basic sentence splitting using regex
    # Matches sentence endings (. ! ?) followed by whitespace and uppercase or end of string
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        if len(current_chunk) >= max_sentences:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
