"""
integration_pipeline.py
========================
End-to-end order integration flow:

  1. Read orders from CSV
  2. Validate each record
  3. Send valid orders to API
  4. Log all outcomes
  5. Write success and failed records to separate files

Run: python integration_pipeline.py
"""

import csv
import logging
import requests
from pathlib import Path
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent
INPUT_FILE = BASE_DIR / "input" / "orders.csv"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR    = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ── Logging ───────────────────────────────────────────────────────────────────

log_file = LOG_DIR / f"integration_{datetime.now():%Y%m%d_%H%M%S}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)

# ── API ───────────────────────────────────────────────────────────────────────

API_URL = "https://jsonplaceholder.typicode.com/posts"

# Simulated failure scenarios for demo purposes
SIMULATE_500 = {"1005"}  # order_ids that trigger a system error
SIMULATE_400 = {"1006"}  # order_ids that trigger an integration error


# ── Validation ────────────────────────────────────────────────────────────────

def validate(order: dict) -> list[str]:
    """Returns a list of validation errors. Empty = valid."""
    errors = []

    for field in ["order_id", "customer_id", "email", "amount", "currency", "order_date"]:
        if not order.get(field, "").strip():
            errors.append(f"missing field: '{field}'")

    if errors:
        return errors  # stop early if required fields are missing

    try:
        if float(order["amount"]) <= 0:
            errors.append(f"amount must be > 0, got '{order['amount']}'")
    except ValueError:
        errors.append(f"amount must be a number, got '{order['amount']}'")

    if order["currency"].upper() not in {"SEK", "EUR", "USD"}:
        errors.append(f"currency must be SEK, EUR or USD, got '{order['currency']}'")

    if "@" not in order["email"]:
        errors.append(f"invalid email: '{order['email']}'")

    try:
        datetime.strptime(order["order_date"], "%Y-%m-%d")
    except ValueError:
        errors.append(f"invalid date format: '{order['order_date']}' (expected YYYY-MM-DD)")

    return errors


# ── API call ──────────────────────────────────────────────────────────────────

def send_to_api(order: dict) -> tuple[int, str]:
    """Sends order to API. Returns (status_code, message)."""
    order_id = order.get("order_id", "")

    if order_id in SIMULATE_500:
        return 500, "External system unavailable"
    if order_id in SIMULATE_400:
        return 400, "Order already exists in target system"

    try:
        response = requests.post(API_URL, json={
            "title":  f"Order {order_id}",
            "body":   f"Customer {order['customer_id']} | {order['amount']} {order['currency']}",
            "userId": 1,
        }, timeout=10)
        return response.status_code, "OK"
    except requests.exceptions.RequestException as e:
        return 500, str(e)


# ── File I/O ──────────────────────────────────────────────────────────────────

def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [{k: v.strip() for k, v in row.items()} for row in csv.DictReader(f)]


def write_csv(records: list[dict], path: Path):
    if not records:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys(), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run():
    log.info("=" * 55)
    log.info("ORDER INTEGRATION PIPELINE STARTING")
    log.info("=" * 55)

    orders = read_csv(INPUT_FILE)
    log.info(f"Read {len(orders)} orders from {INPUT_FILE.name}")

    success = []
    failed  = []

    for order in orders:
        oid = order["order_id"]

        # Step 1 – Validate
        errors = validate(order)
        if errors:
            for e in errors:
                log.error(f"Order {oid} | VALIDATION ERROR | {e}")
            order["failure_reason"] = "; ".join(errors)
            order["failure_type"]   = "VALIDATION_ERROR"
            failed.append(order)
            continue

        log.info(f"Order {oid} | validation passed")

        # Step 2 – Send to API
        status, message = send_to_api(order)

        if status == 201:
            log.info(f"Order {oid} | API success | {status}")
            success.append(order)
        elif status == 400:
            log.error(f"Order {oid} | INTEGRATION ERROR | {message}")
            order["failure_reason"] = message
            order["failure_type"]   = "INTEGRATION_ERROR"
            failed.append(order)
        else:
            log.error(f"Order {oid} | SYSTEM ERROR | {status} {message}")
            order["failure_reason"] = message
            order["failure_type"]   = "SYSTEM_ERROR"
            failed.append(order)

    # Step 3 – Write output
    write_csv(success, OUTPUT_DIR / "success.csv")
    write_csv(failed,  OUTPUT_DIR / "failed_records.csv")

    # Step 4 – Summary
    log.info("=" * 55)
    log.info("PIPELINE COMPLETE – SUMMARY")
    log.info("=" * 55)
    log.info(f"  Total    : {len(orders)}")
    log.info(f"  Success  : {len(success)}")
    log.info(f"  Failed   : {len(failed)}")
    if failed:
        log.warning(f"⚠️  {len(failed)} orders need manual review → output/failed_records.csv")
    else:
        log.info("✅ All orders processed successfully.")
    log.info("=" * 55)


if __name__ == "__main__":
    run()
