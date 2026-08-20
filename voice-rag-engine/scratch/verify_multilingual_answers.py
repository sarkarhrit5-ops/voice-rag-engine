import sys
sys.path.insert(0, '.')
import json
from rag.pipeline import TextRAGPipeline

pipeline = TextRAGPipeline()

test_cases = [
    ("mr", "कॉर्पोरेशन म्हणजे काय?"), # Marathi
    ("hi", "कॉर्पोरेशन क्या है?"),    # Hindi
    ("en", "What is a corporation?"), # English
    ("bn", "কর্পোরেশন কী?"),         # Bengali
    ("mr", "आजचे हवामान कसे आहे?")     # Marathi Out-of-Domain (Refusal test)
]

output = []
for lang, q in test_cases:
    res = pipeline.answer(q, language=lang)
    output.append({
        "language": lang,
        "question": q,
        "refused": res.get("refused"),
        "grounded": res.get("grounded"),
        "answer": res.get("answer")
    })

with open("scratch/verified_answers.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Saved verified answers to scratch/verified_answers.json")
