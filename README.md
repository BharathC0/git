# AI-Powered Invoice Processing System

## Features
- Upload invoices (PDF/Image)
- Extract text/data from invoices
- Categorize expenses using NLP (spaCy)
- Store and visualize extracted data

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
3. Upload invoices via `/upload/` endpoint.

## Notes
- Requires Tesseract OCR installed for image extraction.
- NLP categorization is a placeholder; extend `nlp_utils.py` for real use. 