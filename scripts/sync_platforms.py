#!/usr/bin/env python3
"""Build flattened exports and sync to Kaggle and Hugging Face."""

import subprocess
import sys
import shutil
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAGGLE_DIR = os.path.join(REPO, "kaggle")
HF_REPO = "danielrosehill/Iran-Israel-War-2026"
KAGGLE_HANDLE = "danielrosehill/iran-israel-war-2026"
DATASET_CARD = os.path.join(REPO, "docs", "hf_dataset_card.md")


def build():
    print("==> Building CSV and Parquet exports...")
    subprocess.run([sys.executable, os.path.join(REPO, "scripts", "build_kaggle.py")], check=True)


def sync_kaggle(notes):
    import kagglehub

    print(f"\n==> Uploading to Kaggle ({KAGGLE_HANDLE})...")
    if notes:
        kagglehub.dataset_upload(KAGGLE_HANDLE, KAGGLE_DIR, version_notes=notes)
    else:
        kagglehub.dataset_upload(KAGGLE_HANDLE, KAGGLE_DIR)
    print("    Kaggle sync complete.")


def sync_hf(notes):
    from huggingface_hub import HfApi

    print(f"\n==> Uploading to Hugging Face ({HF_REPO})...")

    # Copy dataset card into kaggle/ as README.md for HF
    readme_dst = os.path.join(KAGGLE_DIR, "README.md")
    shutil.copy2(DATASET_CARD, readme_dst)

    api = HfApi()
    api.upload_folder(
        folder_path=KAGGLE_DIR,
        repo_id=HF_REPO,
        repo_type="dataset",
        commit_message=notes or "Update dataset",
    )

    # Clean up copied README
    os.remove(readme_dst)
    print("    Hugging Face sync complete.")


def main():
    notes = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    build()
    sync_kaggle(notes)
    sync_hf(notes)

    print("\n==> All platforms synced.")
    print(f"    Kaggle:      https://www.kaggle.com/datasets/{KAGGLE_HANDLE}")
    print(f"    Hugging Face: https://huggingface.co/datasets/{HF_REPO}")


if __name__ == "__main__":
    main()
