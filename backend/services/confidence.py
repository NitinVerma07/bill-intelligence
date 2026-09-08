from backend.models.bill import Bill


def calculate_overall_confidence(bill: Bill) -> float:
    if not bill.items:
        return 0.0
    return round(sum(item.confidence for item in bill.items) / len(bill.items), 2)


def mark_review_items(bill: Bill, threshold: float = 0.75) -> Bill:
    for item in bill.items:
        if item.confidence < threshold:
            item.needs_review = True
    bill.overall_confidence = calculate_overall_confidence(bill)
    return bill
