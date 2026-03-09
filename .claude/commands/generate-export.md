Generate a new timestamped export bundle and update exports/latest/.

## Instructions

1. Rebuild the SQLite database from JSON sources:

```bash
source .venv/bin/activate && python3 scripts/build_db.py
```

2. Generate the export bundle (creates timestamped snapshot + overwrites latest/):

```bash
python3 scripts/build_export.py
```

3. Report the results:
   - Timestamp of the new export
   - Number of files generated
   - Any errors from GeoJSON or ArcGIS sub-builds
   - Wave counts per operation from the DB summary

4. After a successful export, remind the user:
   - To commit and push if they want the raw GitHub URLs to update
   - To run `python3 scripts/sync_platforms.py` if they want to sync to Kaggle and Hugging Face

Do NOT auto-commit, auto-push, or auto-sync to platforms. Just generate the export and report.
