# Patient-slide malaria triage review

A read-only FastAPI application for reviewing the 24 patient-slide summaries in `results/results.json`. It reads all data from disk, serves representative cell crops directly from `data/images/parasitized/` and `data/images/uninfected/`, and does not use a database or overlays.

## Run

From the project directory:

```bash
uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/.
