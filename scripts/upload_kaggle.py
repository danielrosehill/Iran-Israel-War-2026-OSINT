#!/usr/bin/env python3
"""Build and upload flattened CSV/Parquet to Kaggle."""

import subprocess
import sys
import kagglehub

HANDLE = "danielrosehill/iran-israel-war-2026"
KAGGLE_DIR = "kaggle"

def main():
    # Rebuild exports first
    print("Building CSV and Parquet exports...")
    subprocess.run([sys.executable, "build_kaggle.py"], check=True)

    notes = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if notes:
        print(f"Uploading with version notes: {notes}")
        kagglehub.dataset_upload(HANDLE, KAGGLE_DIR, version_notes=notes)
    else:
        print("Uploading dataset...")
        kagglehub.dataset_upload(HANDLE, KAGGLE_DIR)
    print("Done.")

if __name__ == "__main__":
    main()
