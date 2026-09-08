# Bill Intelligence

An AI-assisted bill intelligence system that converts restaurant bill photographs into structured bill data, allows human verification, assigns items to multiple people, and calculates accurate individual shares with proportional tax and service-charge distribution.

## Overview

Bill Intelligence is designed to automate the process of splitting restaurant bills from photographs.

Instead of manually entering every item from a bill, the system:

1. Accepts a bill photograph.
2. Extracts text using OCR.
3. Identifies restaurant information, items, quantities, prices, taxes, discounts, and totals.
4. Presents the extracted information for human verification.
5. Allows users to define which person consumed each item.
6. Splits shared items among selected people.
7. Distributes taxes and service charges proportionally according to each person's actual food consumption.
8. Compares the calculated total with the printed bill total.
9. Generates a detailed final split.
10. Supports PDF generation and basic RPA-style ledger processing.

The project is designed to reduce manual bill-entry errors while keeping a human verification step before financial calculations are performed.

---

## Key Features

### 1. Bill Image Upload

Users can upload a restaurant bill photograph through the web interface.

Supported image formats include:

- JPEG
- PNG
- WebP

---

### 2. OCR-Based Extraction

The backend uses local OCR to extract text from bill images.

The OCR pipeline uses:

- Tesseract OCR
- OpenCV
- Pillow
- Image preprocessing

The system attempts to handle common real-world receipt problems such as:

- Low-quality images
- Uneven lighting
- Skewed photographs
- Faded thermal receipts
- OCR noise

---

### 3. Structured Bill Extraction

Extracted information is converted into a structured Pydantic model.

The bill can contain:

- Restaurant name
- Line items
- Quantity
- Unit price
- Item total
- Subtotal
- Discount
- Service charge
- CGST
- SGST
- Other taxes
- Printed total
- Calculated total
- Confidence values

---

### 4. Human Review

OCR is not treated as automatically correct.

Before bill calculations are performed, the extracted information is shown to the user for verification.

Users can review and correct:

- Item names
- Quantities
- Prices
- Taxes
- Discounts
- Totals

This creates a human-in-the-loop workflow.

---

### 5. Multi-Person Bill Splitting

Users can add multiple people and assign food items to them.

An item can belong to:

- One person
- Multiple people
- Everyone

For shared items, the cost is divided among the selected people.

Example:

```text
Pizza = ₹600

Consumed by:
Person A
Person B
Person C

Each person receives:

₹600 / 3 = ₹200
6. Proportional Tax and Service Charge

Taxes and service charges are not divided equally between people.

Instead, they are distributed according to each person's actual food subtotal.

Example:

Person A food = ₹500
Person B food = ₹300
Person C food = ₹200

Food subtotal = ₹1000

Person A's share:

500 / 1000 = 50%

Person B's share:

300 / 1000 = 30%

Person C's share:

200 / 1000 = 20%

If GST is ₹180:

Person A = ₹90
Person B = ₹54
Person C = ₹36

This provides a fairer calculation than dividing GST equally.

7. Printed vs Calculated Total Reconciliation

The system keeps the printed bill total separate from the calculated total.

For example:

Printed Total   = ₹2,651.72
Calculated Total = ₹2,650.72

The difference is highlighted so that a human can investigate possible:

OCR errors
Incorrect printed totals
Missing charges
Rounding differences
Data-entry mistakes

The system does not silently modify the bill to force the totals to match.

8. Confidence-Aware Extraction

Extracted items include confidence information.

Low-confidence extraction can be reviewed by the user before calculation.

This is particularly useful for difficult receipts where OCR may incorrectly recognize:

Characters
Prices
Quantities
Item names
9. PDF Generation

The system can generate a detailed bill-splitting report containing:

Restaurant information
Original bill details
Item assignments
Individual food totals
Tax allocation
Service charge allocation
Final amount for each person
10. Basic RPA Support

The project also includes a lightweight RPA-style workflow for processing bill/ledger data.

The RPA component can watch/process CSV-based transaction information and integrate it with the bill-processing workflow.

Technology Stack
Backend
Python
FastAPI
Pydantic
SQLAlchemy
Tesseract OCR
OpenCV
Pillow
NumPy
ReportLab
Frontend
React
Vite
JavaScript
CSS
Database
SQLite
SQLAlchemy
Testing
Pytest
Project Architecture
Bill_Intelligence
│
├── backend
│   │
│   ├── api
│   │   ├── upload.py
│   │   ├── extraction.py
│   │   ├── assignment.py
│   │   └── calculation.py
│   │
│   ├── database
│   │   ├── database.py
│   │   └── tables.py
│   │
│   ├── models
│   │   ├── bill.py
│   │   ├── person.py
│   │   └── split.py
│   │
│   ├── providers
│   │   └── local.py
│   │
│   ├── services
│   │   ├── calculator.py
│   │   ├── confidence.py
│   │   ├── consensus.py
│   │   ├── llm_router.py
│   │   ├── ocr.py
│   │   ├── parser.py
│   │   ├── pdf_generator.py
│   │   ├── preprocessing.py
│   │   └── rpa.py
│   │
│   ├── tests
│   │   ├── test_calculator.py
│   │   └── test_parser.py
│   │
│   ├── uploads
│   └── main.py
│
└── frontend
    │
    ├── src
    │   ├── components
    │   │   ├── UploadScreen.jsx
    │   │   ├── ReviewScreen.jsx
    │   │   ├── AssignmentScreen.jsx
    │   │   └── ResultsScreen.jsx
    │   │
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    │
    ├── index.html
    ├── package.json
    └── vite.config.js
System Workflow
             ┌─────────────────┐
             │   Bill Image    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Image Processing│
             │    OpenCV       │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │   OCR Engine    │
             │    Tesseract    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Bill Parser     │
             │ + Validation    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Human Review    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Item Assignment │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Split Calculator│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Tax / Service   │
             │ Proportional    │
             │ Allocation      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Final Results   │
             │ + Reconciliation│
             └─────────────────┘
Installation
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/bill-intelligence.git
cd bill-intelligence
Backend Setup

Create and activate a virtual environment.

Windows
python -m venv venv

Activate it:

.\venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r backend\requirements.txt
Install Tesseract OCR

The application requires Tesseract OCR for local bill-text extraction.

On Windows, install Tesseract and ensure it is available at:

C:\Program Files\Tesseract-OCR\tesseract.exe

The application also checks common Tesseract installation locations.

Start the Backend

From the project root:

.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload

The backend will normally be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Frontend Setup

Open another terminal.

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Vite will display the local frontend URL in the terminal.

Running Tests

From the project root:

.\venv\Scripts\python.exe -m pytest backend\tests -q
Example Use Case

Suppose a restaurant bill contains:

Paneer Tikka       ₹280
Butter Chicken     ₹420
Garlic Naan         ₹60
Coke                ₹80

Subtotal           ₹840
CGST                ₹42
SGST                ₹42
Total              ₹924

Three people are added:

Alice
Bob
Charlie

The user assigns:

Paneer Tikka       → Alice
Butter Chicken     → Bob
Garlic Naan        → Alice + Bob
Coke               → Charlie

The system calculates each person's food consumption and distributes CGST/SGST proportionally based on those amounts.

Important Design Decisions
Human-in-the-loop

OCR output is not blindly trusted.

The extracted bill is reviewed before financial calculations.

No fake fallback bill

If OCR/extraction fails, the system does not silently substitute a hard-coded bill.

Instead, the user receives an extraction error and can correct the data through the review workflow.

Proportional charges

Taxes and service charges follow actual consumption rather than being divided equally.

Reconciliation

Printed totals and calculated totals remain separate so discrepancies can be detected.

Limitations

The current system uses local OCR and deterministic parsing.

Receipt layouts vary significantly, so OCR and parsing accuracy can depend on:

Image quality
Lighting
Receipt layout
Font
Camera angle
Handwriting
OCR quality

Human review is therefore an important part of the workflow.

Future Improvements

Potential improvements include:

Multimodal LLM extraction
Better table/receipt layout detection
Two-photo bill merging
Advanced confidence scoring
Automatic correction of OCR errors
More extensive real-world bill evaluation
Support for additional languages/scripts
Cloud deployment
Authentication and user accounts
Persistent bill history
Mobile-friendly interface
Advanced RPA integrations
Project Goal

The goal of Bill Intelligence is to combine:

Computer Vision
      +
OCR
      +
Structured Data Extraction
      +
Human Verification
      +
Rule-Based Financial Calculation
      +
RPA

into a practical system for automated restaurant bill processing and fair multi-person bill splitting.

License

This project is intended for educational, research, and development purposes.


---

# 10. Add a `.gitkeep` to uploads

Git doesn't track empty folders.

Run:

```powershell
New-Item -ItemType File -Path .\backend\uploads\.gitkeep -Force