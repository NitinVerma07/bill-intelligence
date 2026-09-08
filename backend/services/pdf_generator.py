from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from backend.models.split import PersonSplitDetail, SplitResult


def generate_person_pdf(person_split: PersonSplitDetail, restaurant_name: str, split_result: SplitResult) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(restaurant_name or "Restaurant Receipt", styles["Title"]),
        Paragraph(f"Individual Split Receipt — {person_split.person_name}", styles["Heading2"]),
        Spacer(1, 12),
    ]
    rows = [["Item", "Share", "Amount"]]
    for item in person_split.item_breakdown:
        rows.append([item["item_name"], f'{item["share_fraction"] * 100:.0f}%', f'₹{item["share_price"]:.2f}'])
    rows += [
        ["Food", "", f"₹{person_split.food_subtotal:.2f}"],
        ["Discount", "", f"-₹{person_split.discount_allocated:.2f}"],
        ["Tax", "", f"+₹{person_split.cgst_allocated + person_split.sgst_allocated + person_split.other_tax_allocated:.2f}"],
        ["Service charge", "", f"+₹{person_split.service_charge_allocated:.2f}"],
        ["FINAL", "", f"₹{person_split.final_total:.2f}"],
    ]
    table = Table(rows, colWidths=[300, 80, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer
