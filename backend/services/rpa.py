import csv
import glob
import os
import time
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pdf_outputs")
LEDGER_CSV = os.path.join(OUTPUT_DIR, "split_ledger.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def init_ledger_csv():
    if not os.path.exists(LEDGER_CSV):
        with open(LEDGER_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "Timestamp", "Original Filename", "Standardized Filename",
                "Person Name", "Food Subtotal (INR)", "Allocated Tax (INR)",
                "Final Total (INR)", "Status"
            ])


def log_transaction_to_ledger(orig_filename, new_filename, person_name, food_subtotal, tax_allocated, final_total):
    init_ledger_csv()
    with open(LEDGER_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            orig_filename, new_filename, person_name,
            f"{food_subtotal:.2f}", f"{tax_allocated:.2f}",
            f"{final_total:.2f}", "Processed by local RPA"
        ])


def run_rpa_watcher(watch_dir=OUTPUT_DIR, interval_sec=5, run_once=False):
    init_ledger_csv()
    processed = set()
    while True:
        for path in glob.glob(os.path.join(watch_dir, "*.pdf")):
            filename = os.path.basename(path)
            if filename in processed or filename.startswith("std_"):
                continue
            person = filename.split("_split")[0] if "_split" in filename else "Person"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"std_{person}_{timestamp}.pdf"
            new_path = os.path.join(watch_dir, new_name)
            try:
                os.rename(path, new_path)
                log_transaction_to_ledger(filename, new_name, person, 0, 0, 0)
                processed.add(filename)
            except OSError:
                pass
        if run_once:
            return
        time.sleep(interval_sec)
