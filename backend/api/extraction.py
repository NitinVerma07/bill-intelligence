from fastapi import APIRouter, HTTPException
from backend.models.bill import Bill

router = APIRouter(prefix="/api/v1", tags=["Review"])
_bill_store: dict[str, Bill] = {}


@router.get("/bill/{bill_id}", response_model=Bill)
async def get_bill(bill_id: str):
    if bill_id in _bill_store:
        return _bill_store[bill_id]
    raise HTTPException(404, "Bill not found")


@router.post("/bill/{bill_id}/confirm", response_model=Bill)
async def confirm_bill(bill_id: str, updated_bill: Bill):
    updated_bill.id = bill_id
    updated_bill.is_confirmed = True
    _bill_store[bill_id] = updated_bill
    return updated_bill
