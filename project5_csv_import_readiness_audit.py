import csv
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent

LOG_DIR = BASE / "09_Verification_Logs"
LOG_DIR.mkdir(exist_ok=True)

FILES = {
    "campaigns.csv": (120, 7),
    "daily_spend.csv": (11240, 6),
    "leads.csv": (261684, 5),
    "conversions.csv": (39696, 5),
}

BOMS = {
    "UTF-8": b"\xef\xbb\xbf",
    "UTF-16 LE": b"\xff\xfe",
    "UTF-16 BE": b"\xfe\xff",
    "UTF-32 LE": b"\xff\xfe\x00\x00",
    "UTF-32 BE": b"\x00\x00\xfe\xff",
}

report = []
total_rows = 0
total_columns = 0
overall_pass = True

def log(message):
    report.append(message)
    print(message)

log("PROJECT 5 - CSV IMPORT READINESS AUDIT")
log("=" * 55)
log(f"Audit Time: {datetime.now().isoformat(timespec='seconds')}")
log("Original CSV files will not be modified.")
log("")

for filename, expected in FILES.items():
    path = BASE / filename
    expected_rows, expected_cols = expected

    log(f"FILE: {filename}")
    log("-" * 45)

    if not path.exists():
        log("STATUS: FAIL - File not found")
        overall_pass = False
        log("")
        continue

    raw = path.read_bytes()

    detected_bom = next(
        (name for name, signature in BOMS.items()
         if raw.startswith(signature)),
        "None"
    )

    log(f"File Size: {len(raw):,} bytes")
    log(f"Detected BOM: {detected_bom}")

    rows = 0
    malformed = 0
    comma_fields = 0
    quote_fields = 0
    header = []

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            reader = csv.reader(file)

            header = next(reader)
            actual_cols = len(header)

            for row in reader:
                rows += 1

                if len(row) != actual_cols:
                    malformed += 1

                comma_fields += sum("," in x for x in row)
                quote_fields += sum('"' in x for x in row)

        checks = {
            "Expected Rows": rows == expected_rows,
            "Expected Columns": actual_cols == expected_cols,
            "Consistent Row Width": malformed == 0,
            "No Comma Fields": comma_fields == 0,
            "No Quote Fields": quote_fields == 0,
        }

        for name, passed in checks.items():
            log(f"{name}: {'PASS' if passed else 'FAIL'}")

        log(f"Actual Rows: {rows:,}")
        log(f"Actual Columns: {actual_cols}")
        log(f"Malformed Rows: {malformed}")
        log(f"Comma Fields: {comma_fields}")
        log(f"Quote Fields: {quote_fields}")
        log(f"Header: {', '.join(header)}")

        file_pass = all(checks.values())

        log(f"FILE STATUS: {'PASS' if file_pass else 'FAIL'}")

        if not file_pass:
            overall_pass = False

        total_rows += rows
        total_columns += actual_cols

    except Exception as error:
        log(f"STATUS: FAIL - {type(error).__name__}: {error}")
        overall_pass = False

    log("")

log("=" * 55)
log(f"TOTAL DATA ROWS: {total_rows:,}")
log(f"TOTAL COLUMNS: {total_columns}")
log(f"OVERALL STATUS: {'PASS' if overall_pass else 'FAIL'}")
log("")
log("SCOPE: Preliminary CSV structural readiness only.")
log("This is not a complete data-integrity or SQL import audit.")

report_path = LOG_DIR / "CSV_Import_Readiness_Audit.txt"
report_path.write_text("\n".join(report), encoding="utf-8")

print("")
print("AUDIT REPORT SAVED:")
print(report_path)
