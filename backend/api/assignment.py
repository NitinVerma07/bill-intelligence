from fastapi import APIRouter
from pydantic import BaseModel
from backend.models.person import Person

router = APIRouter(prefix="/api/v1", tags=["Assignment"])


class AssignmentRequest(BaseModel):
    bill_id: str
    people: list[Person]


@router.post("/assignment")
async def save_assignment(request: AssignmentRequest):
    return {
        "status": "success",
        "bill_id": request.bill_id,
        "people_count": len(request.people),
        "people": request.people,
    }
