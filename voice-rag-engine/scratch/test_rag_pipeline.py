import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()
from rag.pipeline import TextRAGPipeline

p = TextRAGPipeline(
    index_dir="retrieval/indexes/hin_sentence_aware_plain",
    llm_provider="groq",
    llm_model="groq/compound-mini"
)
res = p.answer("भौमिक आकृतियाँ अक्सर कैसे बनती हैं?", language="hi")
with open("scratch/test_hin_rag.txt", "w", encoding="utf-8") as f:
    f.write(f"Answer: {res['answer']}\n")
    f.write(f"Grounded: {res['grounded']}\n")
    f.write(f"Refused: {res['refused']}\n")
    f.write(f"Sources: {res['sources']}\n")
    f.write(f"Confidence: {res['confidence']}\n")
