# RAG EEG-BCI Pipeline

This repository contains a copy-pasteable, production-ready scaffold for a RAG-style search + dedupe + screening pipeline targeted at EEG-BCI systematic reviews.

See the top-level `run_pipeline.py` for the orchestrator and `config.yaml` for the configuration.

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env with API keys (set GEMINI_API_KEY for Google Gemini / Generative API)
```

2. Dry-run the pipeline:

```bash
python run_pipeline.py --config config.yaml --dry-run
```

3. Run the full pipeline:

```bash
python run_pipeline.py --config config.yaml
```

Files of interest

- `connectors/` - data source connectors (PubMed, IEEE, CrossRef, Google Scholar fallback, repositories)
- `utils/` - dedupe, PDF extraction, logging utilities (includes `utils/llm.py` for Gemini integration)
- `screeners/` - title/abstract and full text screeners
- `exporters/` - CSV/JSON/BibTeX writers
- `artifacts/` - outputs and cached search logs

Notes

- Respect service TOS and rate limits when scraping (Google Scholar scraping is fragile).
- Add API keys to `.env` before running. The pipeline supports Google Gemini via the `GEMINI_API_KEY` environment variable. The `google-generativeai` client is included in `requirements.txt`.
