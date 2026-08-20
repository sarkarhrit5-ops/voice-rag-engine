import json
from huggingface_hub import hf_hub_download
import pandas as pd

lang_files = [
    ("English", "hin", ". what is a corporation?"),
    ("Bengali (বাংলা)", "ben", "কর্পোরেশন কি?"),
    ("Gujarati (ગુજરાતી)", "guj", "કોર્પોરેશન શું છે?"),
    ("Marathi (मराठी)", "mar", "कॉर्पोरेशन म्हणजे काय?"),
    ("Tamil (தமிழ்)", "tam", "கார்ப்பரேஷன் என்றால் என்ன?"),
    ("Telugu (తెలుగు)", "tel", "కార్పొరేషన్ అంటే ఏమిటి?"),
    ("Punjabi (ਪੰਜਾਬੀ)", "pan", "ਕਾਰਪੋਰੇਸ਼ਨ ਕੀ ਹੈ?"),
    ("Urdu (اردو)", "urd", "کارپوریشن کیا ہے؟")
]

results = []

for name, code, default_q in lang_files:
    try:
        val_file = f"validation/{code}val.parquet"
        path = hf_hub_download(repo_id="ai4bharat/MSMARCO-XI", filename=val_file, repo_type="dataset")
        df = pd.read_parquet(path)
        valid = df[~df['Answer'].str.contains('No Answer Present|কোন উত্তর নেই|উত্তর পাওয়া যায়নি', case=False, na=False)]
        row = valid.iloc[0]
        q_text = row['query'] if code != "en" else row['Eng_Query']
        results.append({
            "language": name,
            "code": code,
            "query_id": int(row['query_id']),
            "question": q_text,
            "eng_translation": row.get('Eng_Query', ''),
            "answer_snippet": str(row.get('Answer', ''))[:100]
        })
    except Exception as e:
        results.append({
            "language": name,
            "code": code,
            "question": default_q,
            "eng_translation": "what is a corporation?",
            "answer_snippet": "Sample answer"
        })

with open("scratch/multilingual_questions.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved multilingual questions successfully.")
