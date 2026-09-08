from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.models.bill import Bill
from backend.models.person import Person
from backend.models.split import SplitResult, PersonSplitDetail
from backend.services.calculator import calculate_split
from backend.services.pdf_generator import generate_person_pdf

router = APIRouter(prefix="/api/v1", tags=["Calculation"])


class SplitCalculationRequest(BaseModel):
    bill: Bill
    people: list[Person]


class PDFExportRequest(BaseModel):
    person_split: PersonSplitDetail
    restaurant_name: str
    split_result: SplitResult


@router.post("/calculate", response_model=SplitResult)
async def calculate(request: SplitCalculationRequest):
    if not request.bill.is_confirmed:
        raise HTTPException(400, "Bill must be reviewed and confirmed before calculation.")
    try:
        return calculate_split(request.bill, request.people)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/pdf/export")
async def export_pdf(request: PDFExportRequest):
    pdf = generate_person_pdf(request.person_split, request.restaurant_name, request.split_result)
    filename = f"{request.person_split.person_name.replace(' ', '_')}_split.pdf"
    return StreamingResponse(
        pdf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
