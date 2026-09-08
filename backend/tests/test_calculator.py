from backend.models.bill import Bill, BillItem
from backend.models.person import Person
from backend.services.calculator import calculate_split


def test_dynamic_split():
    bill = Bill(
        id="b1",
        items=[
            BillItem(name="Pizza", quantity=1, unit_price=600, total_price=600),
            BillItem(name="Coke", quantity=2, unit_price=80, total_price=160),
        ],
        subtotal=760,
        cgst=19,
        sgst=19,
        printed_total=798,
        is_confirmed=True,
    )
    people = [
        Person(id="p1", name="A", assigned_item_indices=[0]),
        Person(id="p2", name="B", assigned_item_indices=[1]),
    ]
    result = calculate_split(bill, people)
    assert result.calculated_grand_total == 798
    assert result.reconciliation_matched
    assert sum(p.final_total for p in result.person_splits) == 798
