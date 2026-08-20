"""
Streaming module for MSMARCO-XI dataset on Hugging Face.
Allows streaming queries and passage data without downloading full parquet files locally.
"""

import sys
import argparse
from typing import Iterator, Dict, Any
from datasets import load_dataset


def stream_msmarco(
    language: str = "hin",
    split: str = "validation",
    max_samples: int = 5
) -> Iterator[Dict[str, Any]]:
    """
    Stream records from Hugging Face ai4bharat/MSMARCO-XI in real time.
    """
    val_suffix = "val" if split == "validation" else "train"
    data_file = f"{split}/{language}{val_suffix}.parquet"
    
    print(f"[Streaming] Loading stream for {data_file} from Hugging Face...")
    ds = load_dataset(
        "ai4bharat/MSMARCO-XI",
        data_files=data_file,
        streaming=True
    )

    count = 0
    # The default split name when loading data_files in streaming mode is 'train'
    split_name = list(ds.keys())[0]
    
    for item in ds[split_name]:
        yield item
        count += 1
        if max_samples and count >= max_samples:
            break


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Stream MSMARCO-XI dataset directly from Hugging Face.")
    parser.add_argument("--language", type=str, default="hin", help="Language code (hin, ben, guj, etc.)")
    parser.add_argument("--split", type=str, default="validation", choices=["validation", "train"])
    parser.add_argument("--samples", type=int, default=5, help="Number of records to stream")
    args = parser.parse_args()

    print("=" * 60)
    print("      HUGGING FACE DATASET STREAMING (NO FULL DOWNLOAD)")
    print("=" * 60)
    
    stream = stream_msmarco(language=args.language, split=args.split, max_samples=args.samples)
    
    for idx, sample in enumerate(stream, start=1):
        print(f"\n--- [Sample {idx}] ---")
        print(f"Query ID:   {sample.get('query_id')}")
        print(f"Query:      {sample.get('query')}")
        print(f"Eng Query:  {sample.get('Eng_Query')}")
        print(f"Answer:     {sample.get('Answer')[:120]}...")
        passages = sample.get("passages", {})
        if isinstance(passages, dict):
            trans_p = passages.get("Translated_passages", [])
            print(f"Passages Count: {len(trans_p)}")
            if trans_p:
                print(f"Passage 1 snippet: {trans_p[0][:120]}...")

    print("\n[Done] Successfully streamed samples without storing full dataset locally.")


if __name__ == "__main__":
    main()
