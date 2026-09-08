from backend.services.parser import parse_receipt


def test_parser_extracts_items_and_totals():
    text = """MY CAFE
Pizza 2 250 500
Coke 1 80 80
Subtotal 580
CGST 29
SGST 29
Grand Total 638
"""
    bill = parse_receipt(text, 0.9)
    assert len(bill.items) == 2
    assert bill.subtotal == 580
    assert bill.cgst == 29
    assert bill.sgst == 29
    assert bill.printed_total == 638
