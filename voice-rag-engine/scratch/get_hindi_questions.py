import pandas as pd
from huggingface_hub import hf_hub_download
import json

path = hf_hub_download(repo_id='ai4bharat/MSMARCO-XI', filename='validation/hinval.parquet', repo_type='dataset')
df = pd.read_parquet(path)

# Find answerable questions
ans_df = df[df['Answer'].str.len() > 10]
valid_samples = ans_df[['query_id', 'query', 'Answer', 'Eng_Query']].head(6).to_dict('records')

with open('scratch/hindi_questions.json', 'w', encoding='utf-8') as f:
    json.dump(valid_samples, f, ensure_ascii=False, indent=2)

print("Saved 6 questions to scratch/hindi_questions.json")
