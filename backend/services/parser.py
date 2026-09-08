import re
from typing import Optional

from backend.models.bill import Bill, BillItem


# ============================================================
# WORDS THAT SHOULD NEVER BE TREATED AS FOOD ITEMS
# ============================================================

SUMMARY_WORDS = (
    "subtotal",
    "sub total",
    "grand total",
    "total",
    "net total",
    "tax",
    "cgst",
    "sgst",
    "gst",
    "service charge",
    "service",
    "discount",
    "coupon",
    "round off",
    "rounding",
    "cash",
    "change",
    "amount paid",
    "amount payable",
    "balance",
    "invoice",
    "invoice no",
    "invoice number",
    "bill no",
    "bill number",
    "receipt no",
    "receipt number",
    "order no",
    "order number",
    "date",
    "time",
    "table",
    "table no",
    "table number",
    "waiter",
    "server",
    "cashier",
    "thank",
    "phone",
    "mobile",
    "mob",
    "contact",
    "telephone",
    "tel",
    "address",
    "email",
    "www",
    "http",
    "https",
    "gstin",
    "fssai",
    "upi",
    "transaction",
    "transaction id",
    "payment",
    "card",
    "cashier",
)


# ============================================================
# MONEY PARSER
# ============================================================

def money(value: str) -> float:
    """
    Convert OCR-extracted money text into float.

    Examples:
        ₹250       -> 250.0
        Rs 250     -> 250.0
        Rs. 250    -> 250.0
        1,250.50   -> 1250.50
    """

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .strip()
    )

    return float(value)


# ============================================================
# PHONE NUMBER DETECTION
# ============================================================

def is_phone_number(text: str) -> bool:
    """
    Detect common Indian phone/contact number formats.

    Examples detected:
        9876543210
        98765 43210
        98765-43210
        +91 9876543210
        +91-9876543210
        919876543210
        0731-1234567
        0731 1234567
    """

    text = text.strip()

    # Remove common phone-number separators
    cleaned = re.sub(r"[\s().\-+]", "", text)

    # Remove country code 91
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]

    # Indian mobile number
    if re.fullmatch(r"[6-9]\d{9}", cleaned):
        return True

    # Indian landline-style number
    if re.fullmatch(r"0\d{2,4}\d{6,8}", cleaned):
        return True

    return False


# ============================================================
# PHONE NUMBER INSIDE A LINE
# ============================================================

def contains_phone_number(text: str) -> bool:
    """
    Detect phone numbers embedded inside text.

    Examples:
        Contact: 9876543210
        Mob: 98765 43210
        Phone +91 9876543210
    """

    # Indian mobile number with optional +91 and separators
    mobile_pattern = (
        r"(?<!\d)"
        r"(?:\+?91[\s\-]?)?"
        r"[6-9]\d{4}[\s\-]?\d{5}"
        r"(?!\d)"
    )

    if re.search(mobile_pattern, text):
        return True

    # Common landline pattern
    landline_pattern = (
        r"(?<!\d)"
        r"0\d{2,4}[\s\-]?\d{6,8}"
        r"(?!\d)"
    )

    if re.search(landline_pattern, text):
        return True

    return False


# ============================================================
# GSTIN DETECTION
# ============================================================

def contains_gstin(text: str) -> bool:
    """
    Detect Indian GSTIN-like values.

    Example:
        23ABCDE1234F1Z5
    """

    gstin_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z]\d\b"

    return bool(re.search(gstin_pattern, text.upper()))


# ============================================================
# URL / EMAIL DETECTION
# ============================================================

def contains_url_or_email(text: str) -> bool:
    """
    Detect website URLs and email addresses.
    """

    if re.search(r"https?://|www\.", text.lower()):
        return True

    if re.search(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", text):
        return True

    return False


# ============================================================
# DATE / TIME DETECTION
# ============================================================

def looks_like_date_or_time(text: str) -> bool:
    """
    Detect common receipt date/time formats.
    """

    # 08/09/2026
    if re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        text
    ):
        return True

    # 08-09-2026
    if re.search(
        r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",
        text
    ):
        return True

    # 21:30 or 9:30 PM
    if re.search(
        r"\b\d{1,2}:\d{2}(?:\s*[APap][Mm])?\b",
        text
    ):
        return True

    return False


# ============================================================
# METADATA DETECTOR
# ============================================================

def is_metadata_line(text: str) -> bool:
    """
    Detect lines that contain receipt metadata rather than
    actual food/product line items.
    """

    low = text.lower().strip()

    # --------------------------------------------------------
    # Explicit metadata keywords
    # --------------------------------------------------------

    if any(word in low for word in SUMMARY_WORDS):
        return True

    # --------------------------------------------------------
    # Phone numbers
    # --------------------------------------------------------

    if is_phone_number(text):
        return True

    if contains_phone_number(text):
        return True

    # --------------------------------------------------------
    # GSTIN
    # --------------------------------------------------------

    if contains_gstin(text):
        return True

    # --------------------------------------------------------
    # URL / Email
    # --------------------------------------------------------

    if contains_url_or_email(text):
        return True

    # --------------------------------------------------------
    # Date / Time
    # --------------------------------------------------------

    if looks_like_date_or_time(text):
        return True

    return False


# ============================================================
# PARSE LABELED AMOUNTS
# ============================================================

def parse_labeled_amounts(lines: list[str]):
    """
    Extract subtotal, discount, service charge, taxes and
    printed total from labeled receipt lines.
    """

    result = {
        "subtotal": 0.0,
        "discount": 0.0,
        "service_charge": 0.0,
        "cgst": 0.0,
        "sgst": 0.0,
        "other_tax": 0.0,
        "printed_total": 0.0,
    }

    for line in lines:

        low = line.lower().strip()

        nums = re.findall(
            r"(?<!\d)"
            r"(\d{1,7}(?:,\d{3})*(?:\.\d{1,2})?)"
            r"(?!\d)",
            line
        )

        if not nums:
            continue

        try:
            value = money(nums[-1])
        except ValueError:
            continue

        # ----------------------------------------------------
        # Grand / final total
        # ----------------------------------------------------

        if (
            "grand total" in low
            or low.startswith("total")
            or "net total" in low
            or "amount payable" in low
            or "amount due" in low
            or "payable" in low
        ):
            result["printed_total"] = value

        # ----------------------------------------------------
        # Subtotal
        # ----------------------------------------------------

        elif "subtotal" in low or "sub total" in low:
            result["subtotal"] = value

        # ----------------------------------------------------
        # Service charge
        # ----------------------------------------------------

        elif (
            "service charge" in low
            or (
                "service" in low
                and "tax" not in low
            )
        ):
            result["service_charge"] = value

        # ----------------------------------------------------
        # CGST
        # ----------------------------------------------------

        elif "cgst" in low:
            result["cgst"] = value

        # ----------------------------------------------------
        # SGST
        # ----------------------------------------------------

        elif "sgst" in low:
            result["sgst"] = value

        # ----------------------------------------------------
        # Discount
        # ----------------------------------------------------

        elif "discount" in low or "coupon" in low:
            result["discount"] = value

        # ----------------------------------------------------
        # Other taxes
        # ----------------------------------------------------

        elif (
            "gst" in low
            or "tax" in low
            or "cess" in low
            or "utgst" in low
        ):
            result["other_tax"] += value

    return result


# ============================================================
# ITEM LINE PARSER
# ============================================================

def parse_item_line(line: str) -> Optional[BillItem]:
    """
    Convert a single OCR line into a BillItem.

    The parser deliberately rejects:
        - phone numbers
        - contact information
        - GSTIN
        - URLs
        - email
        - dates/times
        - invoice numbers
        - table/waiter metadata
        - totals/taxes
        - numeric-only OCR garbage
    """

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    clean = re.sub(r"\s+", " ", line).strip()

    if len(clean) < 3:
        return None

    # --------------------------------------------------------
    # Reject metadata BEFORE extracting numbers
    # --------------------------------------------------------

    if is_metadata_line(clean):
        return None

    # --------------------------------------------------------
    # Remove common leading serial numbers
    #
    # Examples:
    #   1. Paneer Tikka 280
    #   2) Coke 80
    #   3- Naan 60
    # --------------------------------------------------------

    clean = re.sub(
        r"^\s*\d+[\).\-\s]+",
        "",
        clean
    ).strip()

    if not clean:
        return None

    # --------------------------------------------------------
    # Find numeric values
    # --------------------------------------------------------

    nums = list(
        re.finditer(
            r"(?<!\d)"
            r"(\d{1,7}(?:,\d{3})*(?:\.\d{1,2})?)"
            r"(?!\d)",
            clean
        )
    )

    if not nums:
        return None

    # --------------------------------------------------------
    # Rightmost number is normally item total
    # --------------------------------------------------------

    last = nums[-1]

    try:
        total = money(last.group(1))
    except ValueError:
        return None

    if total <= 0:
        return None

    # Everything before the last number is the item name
    name = clean[:last.start()].strip(" -:|")

    if not name or len(name) < 2:
        return None

    # --------------------------------------------------------
    # Reject numeric-only names
    # --------------------------------------------------------

    if name.isdigit():
        return None

    # --------------------------------------------------------
    # Reject names containing long numeric sequences
    #
    # Protects against:
    #   9876543210 250
    #   123456789 100
    # --------------------------------------------------------

    name_digits = re.sub(r"\D", "", name)

    if len(name_digits) >= 7:
        return None

    # --------------------------------------------------------
    # Reject phone number if OCR split it strangely
    # --------------------------------------------------------

    if contains_phone_number(name):
        return None

    # --------------------------------------------------------
    # Reject GSTIN
    # --------------------------------------------------------

    if contains_gstin(name):
        return None

    # --------------------------------------------------------
    # Reject URL / email
    # --------------------------------------------------------

    if contains_url_or_email(name):
        return None

    # --------------------------------------------------------
    # Previous numeric values
    # --------------------------------------------------------

    preceding = []

    for match in nums[:-1]:
        try:
            preceding.append(
                money(match.group(1))
            )
        except ValueError:
            continue

    quantity = 1.0
    unit_price = total

    # ========================================================
    # QUANTITY + UNIT PRICE + TOTAL
    # ========================================================

    if len(preceding) >= 2:

        # Common format:
        #
        # Item       Qty   Rate   Amount
        #
        # Coke        2     80     160

        q = preceding[-2]
        up = preceding[-1]

        if (
            0 < q <= 100
            and 0 < up <= 100000
            and abs(q * up - total)
            <= max(0.10, total * 0.03)
        ):
            quantity = q
            unit_price = up

    # ========================================================
    # ONE PRECEDING NUMBER
    # ========================================================

    elif len(preceding) == 1:

        candidate = preceding[0]

        # ----------------------------------------------------
        # Candidate is likely quantity
        # ----------------------------------------------------

        if (
            0 < candidate <= 100
            and abs(candidate * total - total) < 0.01
        ):
            quantity = candidate

            if candidate != 0:
                unit_price = total / candidate

        # ----------------------------------------------------
        # Small integer preceding total
        # ----------------------------------------------------

        elif (
            0 < candidate < total
            and float(candidate).is_integer()
            and candidate <= 20
        ):
            quantity = candidate

            if candidate != 0:
                unit_price = total / candidate

    # ========================================================
    # FINAL SAFETY CHECKS
    # ========================================================

    # Don't accept extremely long "item names"
    if len(name) > 100:
        return None

    # Don't accept names that are mostly numbers
    digit_count = sum(ch.isdigit() for ch in name)
    alpha_count = sum(ch.isalpha() for ch in name)

    if digit_count > alpha_count and digit_count >= 4:
        return None

    # Don't accept standalone serial/invoice-like names
    if len(name.split()) == 1 and name.isdigit():
        return None

    # Don't accept obvious metadata after normalization
    if is_metadata_line(name):
        return None

    # ========================================================
    # CREATE BILL ITEM
    # ========================================================

    return BillItem(
        name=name,
        quantity=round(quantity, 2),
        unit_price=round(unit_price, 2),
        total_price=round(total, 2),
        confidence=0.70,
        source="local_ocr",
    )


# ============================================================
# RECEIPT PARSER
# ============================================================

def parse_receipt(
    raw_text: str,
    ocr_confidence: float = 0.55
) -> Bill:
    """
    Convert raw OCR text into the canonical Bill model.

    Pipeline:
        OCR text
            ↓
        Normalize lines
            ↓
        Extract labeled amounts
            ↓
        Filter metadata
            ↓
        Parse item lines
            ↓
        Remove duplicates
            ↓
        Detect restaurant name
            ↓
        Calculate best-effort total
            ↓
        Return Bill
    """

    # --------------------------------------------------------
    # Normalize OCR lines
    # --------------------------------------------------------

    lines = [
        re.sub(r"\s+", " ", x).strip()
        for x in raw_text.splitlines()
    ]

    lines = [
        x for x in lines
        if x
    ]

    # --------------------------------------------------------
    # Extract summary amounts
    # --------------------------------------------------------

    amounts = parse_labeled_amounts(lines)

    # --------------------------------------------------------
    # Parse items
    # --------------------------------------------------------

    items = []

    for line in lines:

        item = parse_item_line(line)

        if item:

            item.confidence = round(
                min(
                    0.95,
                    max(
                        0.35,
                        ocr_confidence
                    )
                ),
                2
            )

            items.append(item)

    # --------------------------------------------------------
    # Remove duplicate items
    # --------------------------------------------------------

    unique = []
    seen = set()

    for item in items:

        key = (
            item.name.lower(),
            item.quantity,
            item.total_price
        )

        if key not in seen:

            seen.add(key)
            unique.append(item)

    items = unique

    # --------------------------------------------------------
    # Detect restaurant name
    # --------------------------------------------------------

    restaurant_name = None

    for line in lines[:8]:

        low = line.lower()

        # Restaurant name should not look like metadata
        if is_metadata_line(line):
            continue

        # Restaurant name shouldn't contain large numbers
        if re.search(r"\d{2,}", line):
            continue

        # Keep reasonable length
        if len(line) <= 80:
            restaurant_name = line
            break

    # --------------------------------------------------------
    # Calculate item sum
    # --------------------------------------------------------

    item_sum = round(
        sum(
            item.total_price
            for item in items
        ),
        2
    )

    # --------------------------------------------------------
    # Use explicit subtotal if available
    # Otherwise use sum of items
    # --------------------------------------------------------

    subtotal = (
        amounts["subtotal"]
        or item_sum
    )

    # --------------------------------------------------------
    # Printed total
    # --------------------------------------------------------

    printed_total = amounts["printed_total"]

    # --------------------------------------------------------
    # If printed total wasn't detected,
    # calculate best-effort total.
    # --------------------------------------------------------

    if printed_total <= 0:

        printed_total = round(
            subtotal
            - amounts["discount"]
            + amounts["service_charge"]
            + amounts["cgst"]
            + amounts["sgst"]
            + amounts["other_tax"],
            2
        )

    # --------------------------------------------------------
    # No items = extraction failure
    # --------------------------------------------------------

    if not items:

        raise RuntimeError(
            "OCR found text but could not confidently identify "
            "bill line items. Please use the review screen to "
            "enter the items manually or upload a clearer image."
        )

    # --------------------------------------------------------
    # Final Bill object
    # --------------------------------------------------------

    return Bill(
        restaurant_name=restaurant_name,
        items=items,
        subtotal=subtotal,
        discount=amounts["discount"],
        service_charge=amounts["service_charge"],
        cgst=amounts["cgst"],
        sgst=amounts["sgst"],
        other_tax=amounts["other_tax"],
        printed_total=printed_total,

        calculated_total=round(
            subtotal
            - amounts["discount"]
            + amounts["service_charge"]
            + amounts["cgst"]
            + amounts["sgst"]
            + amounts["other_tax"],
            2
        ),

        overall_confidence=round(
            sum(
                item.confidence
                for item in items
            ) / len(items),
            2
        ),

        extraction_mode="local_ocr",
    )