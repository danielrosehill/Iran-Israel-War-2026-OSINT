Sync the dataset to Kaggle and Hugging Face.

## Instructions

1. Rebuild the Kaggle/HF exports and upload to both platforms:

```bash
source .venv/bin/activate && python3 scripts/sync_platforms.py "Add attacking_force field, fix cluster munition data, update schema"
```

Pass a short version note describing what changed. If the user provided context about recent changes, use that. Otherwise summarise the latest git commit message.

2. Report the results:
   - Whether Kaggle upload succeeded
   - Whether Hugging Face upload succeeded
   - Print the dataset URLs:
     - Kaggle: https://www.kaggle.com/datasets/danielrosehill/iran-israel-war-2026
     - Hugging Face: https://huggingface.co/datasets/danielrosehill/Iran-Israel-War-2026

3. If either upload fails, show the error and suggest troubleshooting steps (credential issues, network, etc).
