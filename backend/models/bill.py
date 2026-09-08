from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class BillItem(BaseModel):
    id: Optional[str] = None
    name: str = "Unknown Item"
    quantity: float = 1.0
    unit_price: float = 0.0
    total_price: float = 0.0
    confidence: float = 0.0
    source: str = "local_ocr"
    bbox: Optional[list[int]] = None
    needs_review: bool = False

    @field_validator("quantity", "unit_price", "total_price")
    @classmethod
    def non_negative_money(cls, value):
        return max(0.0, float(value))

    @field_validator("confidence")
    @classmethod
    def confidence_range(cls, value):
        return min(1.0, max(0.0, float(value)))

    @model_validator(mode="after")
    def validate_line_item(self):
        if self.quantity > 0 and self.unit_price > 0:
            expected = round(self.quantity * self.unit_price, 2)
            if abs(expected - round(self.total_price, 2)) > 0.05:
                self.needs_review = True
        return self


class Bill(BaseModel):
    id: Optional[str] = None
    restaurant_name: Optional[str] = None
    items: list[BillItem] = Field(default_factory=list)
    subtotal: float = 0.0
    discount: float = 0.0
    service_charge: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0
    other_tax: float = 0.0
    printed_total: float = 0.0
    calculated_total: float = 0.0
    image_path: Optional[str] = None
    is_confirmed: bool = False
    overall_confidence: float = 0.0
    extraction_mode: str = "local_ocr"

    @model_validator(mode="after")
    def normalize(self):
        self.subtotal = round(max(0.0, self.subtotal), 2)
        self.discount = round(max(0.0, self.discount), 2)
        self.service_charge = round(max(0.0, self.service_charge), 2)
        self.cgst = round(max(0.0, self.cgst), 2)
        self.sgst = round(max(0.0, self.sgst), 2)
        self.other_tax = round(max(0.0, self.other_tax), 2)
        self.printed_total = round(max(0.0, self.printed_total), 2)
        return self
