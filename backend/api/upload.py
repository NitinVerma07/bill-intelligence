import os
import shutil
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.tables import BillTable, BillItemTable
from backend.models.bill import Bill
from backend.services.llm_router import LLMRouter

router = APIRouter(prefix="/api/v1", tags=["Upload"])
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=Bill)
async def upload_bill(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload a JPEG, PNG, or WebP image.")

    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Unsupported image format.")

    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        bill = LLMRouter().extract(path)
    except Exception as exc:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(422, str(exc)) from exc

    bill.id = str(uuid.uuid4())
    bill.image_path = f"/uploads/{filename}"

    row = BillTable(
        id=bill.id,
        restaurant_name=bill.restaurant_name,
        subtotal=bill.subtotal,
        discount=bill.discount,
        service_charge=bill.service_charge,
        cgst=bill.cgst,
        sgst=bill.sgst,
        other_tax=bill.other_tax,
        printed_total=bill.printed_total,
        calculated_total=bill.calculated_total,
        image_path=bill.image_path,
        is_confirmed=False,
    )
    for item in bill.items:
        row.items.append(BillItemTable(
            id=str(uuid.uuid4()), name=item.name, quantity=item.quantity,
            unit_price=item.unit_price, total_price=item.total_price,
            confidence=item.confidence, source=item.source,
            bbox=item.bbox, needs_review=item.needs_review
        ))
    db.add(row)
    db.commit()
    return bill
