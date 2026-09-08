# Bill Intelligence — Local / No-API-Key Edition

This is a deadline-friendly replacement for the original project.

## What changed

- Removed the dangerous fake-bill fallback from the real upload path.
- No Gemini / Claude / OpenAI API key is required.
- Uses local OpenCV preprocessing + Tesseract OCR + deterministic Python parsing.
- Human review is mandatory before calculation.
- Tax, service charge and discount are allocated proportionally to each person's actual food subtotal.
- Shared items are split only among the people selected for that item.
- Printed total is kept separate from calculated total so a genuinely wrong printed total can be flagged.
- Includes PDF generation and an RPA-style CSV ledger watcher.

## Important limitation

Local OCR is not as strong as a multimodal vision model on difficult receipts. It is intentionally API-free. For the best deadline demo, use a clear, mostly front-facing bill photo and correct any OCR mistakes on the Review screen.

## Windows setup

### 1. Install Tesseract

If `winget` is available:

    winget install UB-Mannheim.TesseractOCR

If that command is unavailable, install Tesseract OCR for Windows and make sure `tesseract.exe` is on PATH. The backend also checks the common path:

    C:\Program Files\Tesseract-OCR\tesseract.exe

### 2. Backend

    cd Bill_Intelligence_Local
    py -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r backend\requirements.txt
    uvicorn backend.main:app --reload

Backend:
    http://127.0.0.1:8000
Health:
    http://127.0.0.1:8000/health

### 3. Frontend

Open another terminal:

    cd Bill_Intelligence_Local\frontend
    npm install
    npm run dev

Open:
    http://localhost:5173

## If PowerShell blocks activation

You can run:

    .\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload

## Test

From the project root:

    .\venv\Scripts\python.exe -m pytest backend\tests -q

## Demo flow

1. Upload a real bill photo.
2. Local OCR extracts items and totals.
3. Review/edit extracted values.
4. Confirm.
5. Add 2–3 people.
6. Assign each item to one or more people.
7. Calculate.
8. Show proportional tax/service/discount and reconciliation.

## Do not add API keys

The default application does not read or require a Gemini/Claude/OpenAI key.
