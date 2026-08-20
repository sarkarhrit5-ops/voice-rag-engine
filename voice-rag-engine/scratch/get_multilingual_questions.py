import sys
import json
from datasets import load_dataset

languages = [
    ("en", "English", "validation/hinval.parquet"), # Eng_Query in hinval
    ("ben", "Bengali (বাংলা)", "validation/benval.parquet"),
    ("guj", "Gujarati (ગુજરાતી)", "validation/gujval.parquet"),
    ("mar", "Marathi (मराठी)", "validation/marval.parquet"),
    ("tam", "Tamil (தமிழ்)", "validation/tamval.parquet"),
    ("tel", "Telugu (తెలుగు)", "validation/telval.parquet"),
    ("pan", "Punjabi (ਪੰਜਾਬੀ)", "validation/panval.parquet"),
    ("urd", "Urdu (اردو)", "validation/urdval.parquet")
]

results = {}

for code, name, data_file in languages:
    print(f"Fetching sample for {name} ({code})...")
    try:
        ds = load_dataset("ai4bharat/MSMARCO-XI", data_files=data_file, streaming=True)
        split_name = list(ds.keys())[0]
        samples = []
        for item in ds[split_name]:
            ans = item.get("Answer") or ""
            q = item.get("query") if code != "en" else item.get("Eng_Query")
            eng_q = item.get("Eng_Query")
            if q and len(q) > 5 and not "No Answer Present" in str(ans) and not "कोई उत्तर नहीं" in str(ans):
                samples.append({
                    "query_id": item.get("query_id"),
                    "question": q,
                    "eng_translation": eng_q,
                    "answer_snippet": str(ans)[:100] + "..." if ans else "N/A"
                })
                if len(samples) >= 2:
                    break
        results[name] = samples
    except Exception as e:
        print(f"Error fetching {name}: {e}")

with open("scratch/multilingual_questions.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved multilingual questions to scratch/multilingual_questions.json")
