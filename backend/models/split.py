from pydantic import BaseModel, Field


class PersonSplitDetail(BaseModel):
    person_id: str
    person_name: str
    food_subtotal: float
    discount_allocated: float
    cgst_allocated: float
    sgst_allocated: float
    service_charge_allocated: float
    other_tax_allocated: float
    final_total: float
    item_breakdown: list[dict] = Field(default_factory=list)


class SplitResult(BaseModel):
    bill_id: str | None = None
    verified_food_base: float
    verified_tax_total: float
    verified_service_charge: float
    verified_discount_total: float
    verified_grand_total: float
    calculated_grand_total: float
    reconciliation_matched: bool
    reconciliation_difference: float
    person_splits: list[PersonSplitDetail]
    reconciliation_message: str
