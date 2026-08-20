import sys
sys.path.insert(0, '.')
from rag.pipeline import TextRAGPipeline
import json

pipeline = TextRAGPipeline(llm_provider="mock", llm_model="mock-low-latency")

test_questions = [
    {"id": 1, "type": "grounded", "question": "कॉर्पोरेशन क्या है?", "translation": "What is a corporation?"},
    {"id": 2, "type": "grounded", "question": "ईमानदारी या सच्चाई की परिभाषा", "translation": "Definition of honesty or integrity"},
    {"id": 3, "type": "grounded", "question": "रेचल कार्सन ने क्यों एक दायित्व बर्दाश्त करने के लिए लिखा", "translation": "Why did Rachel Carson write 'The Obligation to Endure'?"},
    {"id": 4, "type": "refusal", "question": "पोटेशियम में कम खाद्य पदार्थों का चार्ट।", "translation": "Chart for foods low in potassium."},
    {"id": 5, "type": "refusal", "question": "लिंकन में अब वायुमंडलीय दबाव क्या है?", "translation": "What is the barometric pressure in Lincoln now?"}
]

results = []
for item in test_questions:
    res = pipeline.answer(item["question"], language="hi")
    results.append({
        "id": item["id"],
        "expected_type": item["type"],
        "question": item["question"],
        "translation": item["translation"],
        "grounded": res.get("grounded"),
        "refused": res.get("refused"),
        "answer": res.get("answer"),
        "top_passage_score": res.get("scores", [0])[0] if res.get("scores") else 0
    })

with open("scratch/db_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved test results to scratch/db_test_results.json")
