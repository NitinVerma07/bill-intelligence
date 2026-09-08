import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api import upload_router, extraction_router, assignment_router, calculation_router
from backend.database.database import init_db

app = FastAPI(
    title="Bill Intelligence - API-Free",
    description="Local OCR bill extraction, human review, proportional splitting and reconciliation.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(upload_router)
app.include_router(extraction_router)
app.include_router(assignment_router)
app.include_router(calculation_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "mode": "local_ocr", "api_key_required": False}
