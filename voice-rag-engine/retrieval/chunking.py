import re
import sys
import os

# Add local pkg directory to sys.path to resolve any external dependencies in this package
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pkg'))
if pkg_path not in sys.path:
    sys.path.insert(0, pkg_path)

def chunk_passage_baseline(text: str) -> list[str]:
    """
    Experiment 1: Passage-as-chunk baseline.
    Treats each passage as a single retrieval unit.
    """
    if not text or not text.strip():
        return []
    return [text.strip()]

def chunk_fixed_size(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Experiment 2: Fixed-size character chunking with overlap.
    """
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        # Move start forward by step size (chunk_size - overlap)
        step = chunk_size - overlap
        if step <= 0:
            # Prevent infinite loops if overlap is configured poorly
            step = chunk_size
        start += step
        # If we have reached the end of the string
        if start >= len(text):
            break
    return chunks

def chunk_sentence_aware(text: str, max_chars: int) -> list[str]:
    """
    Experiment 3: Sentence-aware chunking.
    Splits text on sentence boundaries (supporting English '.', '?', '!' and Hindi '।'),
    and aggregates sentences up to max_chars.
    """
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
        
    # Split by sentence boundaries, keeping delimiters by using positive lookbehind.
    # Delimiters: English sentence endings (. ! ?) and Hindi danda (।)
    sentences = re.split(r'(?<=[।\.!\?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Fallback for very long sentences that exceed max_chars on their own
        if len(sentence) > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            # Split the outlier sentence using fixed-size chunking
            sentence_chunks = chunk_fixed_size(sentence, max_chars, overlap=max_chars // 5)
            chunks.extend(sentence_chunks)
        else:
            # Calculate length with space separator if adding to existing chunk
            space_padding = 1 if current_chunk else 0
            if current_length + len(sentence) + space_padding <= max_chars:
                current_chunk.append(sentence)
                current_length += len(sentence) + space_padding
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = len(sentence)
                
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def format_contextual_representation(text: str, query_type: str, language: str) -> str:
    """
    Experiment 4: Contextual representation.
    Prepend metadata to the passage text, e.g. [query_type] [language] passage_text.
    """
    q_type = str(query_type).strip().upper()
    lang = str(language).strip()
    return f"[{q_type}] [{lang}] {text}"
