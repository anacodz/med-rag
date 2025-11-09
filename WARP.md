# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Setup

1.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env
    # Edit .env with API keys (set GEMINI_API_KEY for Google Gemini / Generative API)
    ```

### Running the pipeline

*   **Dry-run the pipeline:**
    ```bash
    python run_pipeline.py --config config.yaml --dry-run
    ```
*   **Run the full pipeline:**
    ```bash
    python run_pipeline.py --config config.yaml
    ```

### Testing
This project does not have a dedicated test suite. To test, run the pipeline with the `--dry-run` flag.

## Code Architecture

This repository implements a RAG-style search, deduplication, and screening pipeline for EEG-BCI systematic reviews.

*   `run_pipeline.py`: The main orchestrator for the pipeline.
*   `config.yaml`: Configuration file for the pipeline.
*   `connectors/`: Contains data source connectors for PubMed, IEEE, CrossRef, and Google Scholar.
*   `utils/`: Includes utilities for deduplication, PDF extraction, logging, and Gemini integration (`utils/llm.py`).
*   `screeners/`: Holds the title/abstract and full-text screeners.
*   `exporters/`: Contains writers for CSV, JSON, and BibTeX formats.
*   `artifacts/`: Stores outputs and cached search logs.

## Notes
*   Respect the terms of service and rate limits of the services being scraped.
*   Ensure that API keys, especially `GEMINI_API_KEY`, are added to a `.env` file before running the pipeline.
