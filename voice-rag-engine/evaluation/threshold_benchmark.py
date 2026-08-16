import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from rag.pipeline import TextRAGPipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Sweep retrieval confidence thresholds for the Hindi RAG benchmark.")
    parser.add_argument("--samples", type=int, default=5000, help="Number of validation queries to sample (default: 5000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--top_k", type=int, default=5, help="Top-K retrieval to evaluate")
    parser.add_argument("--index_dir", type=str, default="retrieval/indexes/eng_sentence_aware_plain", help="Index directory to use")
    parser.add_argument("--csv_out", type=str, default="evaluation/threshold_benchmark_results.csv", help="Output CSV path")
    parser.add_argument("--md_out", type=str, default="evaluation/threshold_benchmark_report.md", help="Output Markdown report path")
    return parser.parse_args()


def get_grouped_sample(samples: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    repo_id = "ai4bharat/MSMARCO-XI"
    filename = "validation/hinval.parquet"
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    df = pd.read_parquet(local_path)
    sample_df = df.sample(n=min(samples, len(df)), random_state=seed).copy()
    sample_df["num_selected"] = sample_df["passages"].apply(
        lambda p: sum(p.get("is_selected", [])) if isinstance(p, dict) else 0
    )
    group1 = sample_df[sample_df["num_selected"] > 0].copy()
    group2 = sample_df[sample_df["num_selected"] == 0].copy()
    return sample_df, group1, group2


def evaluate_threshold(threshold: float, group1: pd.DataFrame, group2: pd.DataFrame, top_k: int, index_dir: str):
    pipeline = TextRAGPipeline(
        index_dir=index_dir,
        model_name="intfloat/multilingual-e5-small",
        device="cpu",
        llm_provider="mock",
        llm_model="mock-low-latency",
    )

    answerable_correct = 0
    answerable_refused = 0
    no_answer_correct_refusals = 0
    no_answer_incorrect_answers = 0

    for _, row in group1.iterrows():
        query = row["query"]
        query_id = int(row["query_id"])
        res = pipeline.answer(query=query, language="hi", top_k=top_k, min_score=threshold, query_id=query_id)
        if res["grounded"] and not res["refused"]:
            answerable_correct += 1
        elif res["refused"]:
            answerable_refused += 1

    for _, row in group2.iterrows():
        query = row["query"]
        query_id = int(row["query_id"])
        res = pipeline.answer(query=query, language="hi", top_k=top_k, min_score=threshold, query_id=query_id)
        if res["refused"]:
            no_answer_correct_refusals += 1
        else:
            no_answer_incorrect_answers += 1

    total_answerable = len(group1)
    total_no_answer = len(group2)

    false_answer_rate = (no_answer_incorrect_answers / total_no_answer) if total_no_answer else 0.0
    false_refusal_rate = (answerable_refused / total_answerable) if total_answerable else 0.0
    grounded_answer_rate = (answerable_correct / total_answerable) if total_answerable else 0.0
    refusal_accuracy = (no_answer_correct_refusals / total_no_answer) if total_no_answer else 0.0
    precision = (answerable_correct / (answerable_correct + no_answer_incorrect_answers)) if (answerable_correct + no_answer_incorrect_answers) else 0.0
    recall = (answerable_correct / (answerable_correct + answerable_refused)) if (answerable_correct + answerable_refused) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "threshold": threshold,
        "answerable_queries_correctly_answered": answerable_correct,
        "answerable_queries_incorrectly_refused": answerable_refused,
        "no_answer_queries_correctly_refused": no_answer_correct_refusals,
        "no_answer_queries_incorrectly_answered": no_answer_incorrect_answers,
        "false_answer_rate": false_answer_rate,
        "false_refusal_rate": false_refusal_rate,
        "grounded_answer_rate": grounded_answer_rate,
        "refusal_accuracy": refusal_accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main():
    args = parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    sample_df, group1, group2 = get_grouped_sample(args.samples, args.seed)
    print(f"Loaded validation sample: {len(sample_df)} rows | answerable={len(group1)} | no-answer={len(group2)}")

    results = []
    for threshold in np.arange(0.65, 0.85 + 1e-9, 0.02):
        threshold = round(float(threshold), 2)
        print(f"Evaluating threshold {threshold:.2f}...")
        metrics = evaluate_threshold(threshold, group1, group2, args.top_k, args.index_dir)
        results.append(metrics)

    output_csv = Path(args.csv_out)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "threshold",
                "answerable_queries_correctly_answered",
                "answerable_queries_incorrectly_refused",
                "no_answer_queries_correctly_refused",
                "no_answer_queries_incorrectly_answered",
                "false_answer_rate",
                "false_refusal_rate",
                "grounded_answer_rate",
                "refusal_accuracy",
                "precision",
                "recall",
                "f1",
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    best = max(results, key=lambda r: (r["f1"], -r["false_refusal_rate"], r["grounded_answer_rate"]))

    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Threshold benchmark report",
        "",
        f"- Sample size: {len(sample_df)} validation queries",
        f"- Answerable queries: {len(group1)}",
        f"- No-answer queries: {len(group2)}",
        f"- Best tradeoff threshold: {best['threshold']:.2f}",
        "",
        "| threshold | correct answer | incorrect refusal | correct refusal | incorrect answer | false answer rate | false refusal rate | grounded answer rate | refusal accuracy | precision | recall | f1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        lines.append(
            f"| {row['threshold']:.2f} | {row['answerable_queries_correctly_answered']} | {row['answerable_queries_incorrectly_refused']} | {row['no_answer_queries_correctly_refused']} | {row['no_answer_queries_incorrectly_answered']} | {row['false_answer_rate']:.4f} | {row['false_refusal_rate']:.4f} | {row['grounded_answer_rate']:.4f} | {row['refusal_accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} |"
        )

    lines += [
        "",
        "## Best threshold",
        "",
        f"The threshold with the strongest F1 tradeoff while minimizing false refusals is {best['threshold']:.2f}. It achieved grounded-answer rate {best['grounded_answer_rate']:.4f}, false-refusal rate {best['false_refusal_rate']:.4f}, and F1 {best['f1']:.4f}.",
        "",
        "This threshold should be treated as the candidate production guardrail until a live-provider benchmark confirms it under real generation latency and a larger validation sample.",
    ]

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"CSV written to {output_csv}")
    print(f"Markdown report written to {md_path}")
    print(f"Best threshold: {best['threshold']:.2f} (F1={best['f1']:.4f}, false_refusal_rate={best['false_refusal_rate']:.4f}, grounded_answer_rate={best['grounded_answer_rate']:.4f})")


if __name__ == "__main__":
    main()
