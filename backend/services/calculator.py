from decimal import Decimal, ROUND_HALF_UP
from backend.models.bill import Bill
from backend.models.person import Person
from backend.models.split import PersonSplitDetail, SplitResult


def round_currency(value: float) -> float:
    return float(
        Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def calculate_split(bill: Bill, people: list[Person], tolerance: float = 0.02) -> SplitResult:
    if not people:
        raise ValueError("At least one person must be provided.")
    if bill.discount > bill.subtotal and bill.subtotal > 0:
        raise ValueError("Discount cannot exceed subtotal.")

    assignees = {i: [] for i in range(len(bill.items))}
    for person in people:
        for idx in person.assigned_item_indices:
            if idx < 0 or idx >= len(bill.items):
                raise ValueError(f"Invalid item index {idx} for {person.name}.")
            if person.id not in assignees[idx]:
                assignees[idx].append(person.id)

    for idx, people_ids in assignees.items():
        if not people_ids:
            raise ValueError(f"Item '{bill.items[idx].name}' is assigned to 0 people.")

    food = {p.id: 0.0 for p in people}
    breakdown = {p.id: [] for p in people}

    # Use exact cents for each item allocation and give any rounding remainder
    # to the last assignee, preserving the item total exactly.
    for idx, item in enumerate(bill.items):
        ids = assignees[idx]
        base_share = round_currency(item.total_price / len(ids))
        shares = [base_share] * len(ids)
        remainder = round_currency(item.total_price - sum(shares))
        shares[-1] = round_currency(shares[-1] + remainder)

        for pos, pid in enumerate(ids):
            share = shares[pos]
            food[pid] = round_currency(food[pid] + share)
            breakdown[pid].append({
                "item_index": idx,
                "item_name": item.name,
                "share_fraction": round(share / item.total_price, 4) if item.total_price else 0.0,
                "share_price": share,
                "quantity": round(item.quantity / len(ids), 2),
                "unit_price": item.unit_price,
            })

    food_base = round_currency(bill.subtotal if bill.subtotal > 0 else sum(food.values()))
    total_tax = round_currency(bill.cgst + bill.sgst + bill.other_tax)
    total_service = round_currency(bill.service_charge)
    total_discount = round_currency(bill.discount)

    # Proportional allocation based on what each person actually ate.
    splits = []
    for p in people:
        factor = food[p.id] / food_base if food_base > 0 else 1 / len(people)
        disc = round_currency(total_discount * factor)
        cgst = round_currency(bill.cgst * factor)
        sgst = round_currency(bill.sgst * factor)
        other = round_currency(bill.other_tax * factor)
        service = round_currency(total_service * factor)
        final = round_currency(food[p.id] - disc + cgst + sgst + other + service)

        splits.append(PersonSplitDetail(
            person_id=p.id,
            person_name=p.name,
            food_subtotal=food[p.id],
            discount_allocated=disc,
            cgst_allocated=cgst,
            sgst_allocated=sgst,
            service_charge_allocated=service,
            other_tax_allocated=other,
            final_total=final,
            item_breakdown=breakdown[p.id],
        ))

    calculated = round_currency(food_base - total_discount + total_tax + total_service)
    printed = round_currency(bill.printed_total) if bill.printed_total > 0 else calculated
    diff = round_currency(abs(printed - calculated))
    matched = diff <= tolerance

    message = (
        f"Reconciliation successful: ₹{calculated:.2f} matches printed total ₹{printed:.2f}."
        if matched else
        f"Reconciliation warning: printed ₹{printed:.2f}, calculated ₹{calculated:.2f}; difference ₹{diff:.2f}."
    )

    return SplitResult(
        bill_id=bill.id,
        verified_food_base=food_base,
        verified_tax_total=total_tax,
        verified_service_charge=total_service,
        verified_discount_total=total_discount,
        verified_grand_total=printed,
        calculated_grand_total=calculated,
        reconciliation_matched=matched,
        reconciliation_difference=diff,
        person_splits=splits,
        reconciliation_message=message,
    )
