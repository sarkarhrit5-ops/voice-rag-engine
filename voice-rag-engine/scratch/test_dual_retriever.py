import os
import sys
sys.path.insert(0, os.path.abspath('.'))
from dotenv import load_dotenv
load_dotenv()
from retrieval.indexer import VectorIndexer
from retrieval.retriever import DenseRetriever

idx_en = VectorIndexer(model_name="intfloat/multilingual-e5-small", device="cpu")
idx_en.load_index("retrieval/indexes/eng_sentence_aware_plain")
ret_en = DenseRetriever(idx_en)

idx_hi = VectorIndexer(model_name="intfloat/multilingual-e5-small", device="cpu")
idx_hi.model = idx_en.model
idx_hi.load_index("retrieval/indexes/hin_sentence_aware_plain")
ret_hi = DenseRetriever(idx_hi)

q_hi = "भौमिक आकृतियाँ अक्सर कैसे बनती हैं?"
p_hi, _ = ret_hi.retrieve(q_hi, k=3)
print("Hindi Query retrieved score:", p_hi[0]['score'])
print("Hindi Passage snippet:", p_hi[0]['metadata']['text'][:100].encode('utf-8', errors='replace').decode('utf-8'))

q_en = "How are landforms usually formed?"
p_en, _ = ret_en.retrieve(q_en, k=3)
print("English Query retrieved score:", p_en[0]['score'])
print("English Passage snippet:", p_en[0]['metadata']['text'][:100])
