#!/usr/bin/env python3
"""Upload the data/ directory to Kaggle as a dataset."""

import sys
import kagglehub

HANDLE = "danielrosehill/iran-israel-war-2026"
DATA_DIR = "data"
IGNORE = [".git/", "*.pyc", "__pycache__/"]

def main():
    notes = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if notes:
        print(f"Uploading with version notes: {notes}")
        kagglehub.dataset_upload(HANDLE, DATA_DIR, version_notes=notes, ignore_patterns=IGNORE)
    else:
        print("Uploading dataset...")
        kagglehub.dataset_upload(HANDLE, DATA_DIR, ignore_patterns=IGNORE)
    print("Done.")

if __name__ == "__main__":
    main()
