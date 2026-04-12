"""
Batchjobbhantering – Automatiserad filbearbetning
=================================================
Simulerar ett verkligt batchjobb som:
  1. Läser CSV-filer från en inkorgsmoapp
  2. Validerar och transformerar data
  3. Sparar resultat i en utkorgs-mapp
  4. Loggar allt till fil och terminal
  5. Skickar en sammanfattning (simulerat) när jobbet är klart

Kör direkt: python batch_job.py
Kör schemalagt (Linux/Mac): crontab -e  →  0 6 * * * python /sökväg/batch_job.py
"""

import csv
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

# ── Konfiguration ─────────────────────────────────────────────────────────────

BASE_DIR    = Path(__file__).parent
INBOX_DIR   = BASE_DIR / "inbox"
OUTBOX_DIR  = BASE_DIR / "outbox"
ARCHIVE_DIR = BASE_DIR / "archive"
LOG_DIR     = BASE_DIR / "logs"

for d in [INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR, LOG_DIR]:
    d.mkdir(exist_ok=True)

# ── Loggning ──────────────────────────────────────────────────────────────────

def setup_logger(job_name: str) -> logging.Logger:
    """Skapar en logger som skriver till både fil och terminal."""
    log_file = LOG_DIR / f"{job_name}_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = logging.getLogger(job_name)
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # Fil-handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Terminal-handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ── Exempeldata ───────────────────────────────────────────────────────────────

def create_sample_files():
    """Skapar tre test-CSV-filer i inbox-mappen."""
    files = {
        "orders_2024_01.csv": [
            ["order_id", "customer_name", "amount", "status"],
            ["1001", "Anna Svensson",  "1299.00", "delivered"],
            ["1002", "Erik Lindgren",  "459.50",  "shipped"],
            ["1003", "Maria Nilsson",  "",         "pending"],   # saknat belopp
            ["1004", "Johan Karlsson", "8750.00", "delivered"],
        ],
        "orders_2024_02.csv": [
            ["order_id", "customer_name", "amount", "status"],
            ["1005", "Sara Eriksson",   "299.00",  "delivered"],
            ["1006", "Lars Petersson",  "OGILTIG", "shipped"],   # felaktigt belopp
            ["1007", "Karin Andersson", "5500.00", "delivered"],
        ],
        "orders_empty.csv": [
            ["order_id", "customer_name", "amount", "status"],  # Tom fil
        ],
    }

    for filename, rows in files.items():
        path = INBOX_DIR / filename
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)


# ── Validering & transformation ───────────────────────────────────────────────

def validate_row(row: dict, row_num: int, logger: logging.Logger) -> dict | None:
    """
    Validerar en rad. Returnerar transformerad rad eller None vid fel.
    """
    errors = []

    # Kontrollera obligatoriska fält
    for field in ["order_id", "customer_name", "amount", "status"]:
        if not row.get(field, "").strip():
            errors.append(f"Tomt obligatoriskt fält: '{field}'")

    # Validera amount som tal
    try:
        amount = float(row.get("amount", ""))
        if amount < 0:
            errors.append("Negativt belopp är inte tillåtet")
    except ValueError:
        errors.append(f"Ogiltigt belopp: '{row.get('amount')}'")
        amount = None

    if errors:
        for err in errors:
            logger.warning(f"  Rad {row_num}: {err} – {row}")
        return None

    return {
        "order_id":      row["order_id"].strip(),
        "customer_name": row["customer_name"].strip().title(),
        "amount":        round(amount, 2),
        "status":        row["status"].strip().lower(),
        "processed_at":  datetime.now().isoformat(),
    }


def process_file(csv_path: Path, logger: logging.Logger) -> dict:
    """Bearbetar en CSV-fil och returnerar statistik."""
    stats = {"file": csv_path.name, "total": 0, "ok": 0, "errors": 0}
    results = []

    logger.info(f"Bearbetar: {csv_path.name}")

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            stats["total"] += 1
            transformed = validate_row(row, row_num, logger)
            if transformed:
                results.append(transformed)
                stats["ok"] += 1
            else:
                stats["errors"] += 1

    if not results:
        logger.warning(f"  Inga giltiga rader i {csv_path.name} – hoppar över.")
        return stats

    # Spara resultat som JSON i outbox
    out_file = OUTBOX_DIR / csv_path.with_suffix(".json").name
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"  ✓ Sparade {len(results)} rader → {out_file.name}")

    # Arkivera originalfilen
    shutil.move(str(csv_path), ARCHIVE_DIR / csv_path.name)
    logger.debug(f"  Arkiverade {csv_path.name}")

    return stats


# ── Huvudprocess ──────────────────────────────────────────────────────────────

def run_batch_job():
    logger = setup_logger("order_import")
    logger.info("=" * 55)
    logger.info("BATCHJOBB STARTAR")
    logger.info("=" * 55)

    create_sample_files()
    csv_files = list(INBOX_DIR.glob("*.csv"))

    if not csv_files:
        logger.info("Inga filer att bearbeta. Avslutar.")
        return

    logger.info(f"Hittade {len(csv_files)} fil(er) att bearbeta.\n")

    all_stats = []
    for csv_file in sorted(csv_files):
        stats = process_file(csv_file, logger)
        all_stats.append(stats)
        logger.info("")

    # Sammanfattning
    total_rows    = sum(s["total"]  for s in all_stats)
    total_ok      = sum(s["ok"]     for s in all_stats)
    total_errors  = sum(s["errors"] for s in all_stats)
    files_ok      = sum(1 for s in all_stats if s["ok"] > 0)

    logger.info("=" * 55)
    logger.info("BATCHJOBB KLART – SAMMANFATTNING")
    logger.info("=" * 55)
    logger.info(f"  Filer bearbetade : {len(all_stats)}")
    logger.info(f"  Filer med data   : {files_ok}")
    logger.info(f"  Rader totalt     : {total_rows}")
    logger.info(f"  Godkända rader   : {total_ok}")
    logger.info(f"  Felaktiga rader  : {total_errors}")
    logger.info("=" * 55)

    # Simulera notifiering
    if total_errors > 0:
        logger.warning(f"⚠️  {total_errors} rader hade valideringsfel – kräver manuell granskning.")
    else:
        logger.info("✅ Alla rader bearbetades utan fel.")

    # Städa upp demo-filer
    for d in [OUTBOX_DIR, ARCHIVE_DIR, LOG_DIR]:
        shutil.rmtree(d)
        d.mkdir()


if __name__ == "__main__":
    run_batch_job()
