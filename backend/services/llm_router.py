from backend.models.bill import Bill
from .ocr import run_ocr_pass
from .parser import parse_receipt
from .confidence import mark_review_items


class LLMRouter:
    """
    Backward-compatible service name from the original project.

    IMPORTANT: the default implementation is fully local and does not call
    Gemini, Claude, OpenAI, or any remote API.
    """

    def extract(self, image_path: str, provider_name: str | None = None) -> Bill:
        ocr = run_ocr_pass(image_path)
        bill = parse_receipt(ocr["raw_text"], ocr["confidence"])
        bill = mark_review_items(bill)
        bill.image_path = image_path
        bill.extraction_mode = "local_ocr"
        return bill
