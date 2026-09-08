from backend.models.bill import Bill
from backend.services.ocr import run_ocr_pass
from backend.services.parser import parse_receipt
from backend.services.confidence import mark_review_items


class LocalOCRProvider:
    def extract_bill(self, image_path: str) -> Bill:
        ocr = run_ocr_pass(image_path)
        bill = parse_receipt(ocr["raw_text"], ocr["confidence"])
        bill.image_path = image_path
        return mark_review_items(bill)
