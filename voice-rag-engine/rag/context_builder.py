# Context builder for the RAG pipeline

def build_context(retrieved_passages: list[dict], max_chars: int = 4000) -> str:
    """
    Constructs a structured and bounded context string from retrieved passages.
    
    Each passage is expected to be a dictionary containing:
      - 'metadata': dict with 'query_id', 'passage_index', 'text', etc.
      
    Example output format:
      [Source 123456_2]
      This is the passage text.
      
    Truncates the context if it exceeds max_chars to ensure low latency.
    """
    context_parts = []
    current_length = 0
    
    for item in retrieved_passages:
        meta = item.get("metadata", {})
        query_id = meta.get("query_id", "unknown")
        passage_index = meta.get("passage_index", "0")
        chunk_index = meta.get("chunk_index", "0")
        text = meta.get("text", "").strip()
        
        if not text:
            continue
            
        # Create a unique source label
        source_label = f"[Source {query_id}_{passage_index}_{chunk_index}]"
        passage_block = f"{source_label}\n{text}\n\n"
        
        if current_length + len(passage_block) > max_chars:
            # If adding this block exceeds limit, break or slice if we have room
            remaining_chars = max_chars - current_length
            if remaining_chars > len(source_label) + 20: # only append if we can fit the label and some text
                sliced_text = text[:remaining_chars - len(source_label) - 5]
                passage_block = f"{source_label}\n{sliced_text}...\n\n"
                context_parts.append(passage_block)
            break
            
        context_parts.append(passage_block)
        current_length += len(passage_block)
        
    return "".join(context_parts).strip()
