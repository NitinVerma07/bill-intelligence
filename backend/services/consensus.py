from backend.models.bill import Bill


def evaluate_consensus(bill_a: Bill, bill_b: Bill) -> Bill:
    # Kept as an optional extension point. The API-free default app does not
    # call two remote LLMs. It can be used later if a provider is configured.
    merged = bill_a.model_copy(deep=True)
    if len(bill_a.items) != len(bill_b.items):
        for item in merged.items:
            item.needs_review = True
    for i, item in enumerate(merged.items):
        if i < len(bill_b.items):
            other = bill_b.items[i]
            if abs(item.total_price - other.total_price) > 0.50 or item.name.lower() != other.name.lower():
                item.needs_review = True
                item.confidence = round(min(item.confidence, other.confidence) * 0.7, 2)
    return merged
